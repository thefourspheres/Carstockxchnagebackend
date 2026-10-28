from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.storage.factory import get_storage
from .car_image_model import CarImage
from .car_model import Car
from .car_schema import CarCreateSchema, CarUpdateSchema

IMAGE_TYPES = {"banner", "exterior", "interior", "engine"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_FILES_PER_UPLOAD = 20


def _ids(user: dict) -> tuple[UUID, UUID]:
    return UUID(str(user["sub"])), UUID(str(user["organization_id"]))


def _summary(car: Car) -> dict:
    active = sorted((i for i in car.images if i.is_active), key=lambda i: i.display_order or 0)
    banner = next((i.image_url for i in active if i.image_type == "banner"), None)
    return {
        "id": car.id, "name": car.name, "brand": car.brand, "car_type": car.car_type,
        "condition": car.condition, "year": car.year, "fuel_type": car.fuel_type,
        "transmission": car.transmission, "color": car.color, "description": car.description,
        "actual_price": car.actual_price, "discounted_price": car.discounted_price,
        "status": car.status, "banner_image": banner or (active[0].image_url if active else None),
        "image_count": len(active), "created_at": car.created_at, "updated_at": car.updated_at,
    }


class CarService:

    @staticmethod
    async def _get(db: AsyncSession, car_id: UUID, user: dict, with_images: bool = False) -> Car:
        _, org_id = _ids(user)
        q = select(Car).where(Car.id == car_id, Car.organization_id == org_id, Car.is_active.is_(True))
        if with_images:
            q = q.options(selectinload(Car.images))
        car = (await db.execute(q)).scalar_one_or_none()
        if not car:
            raise HTTPException(404, "Car not found")
        return car

    @staticmethod
    async def create_car(db: AsyncSession, payload: CarCreateSchema, user: dict) -> Car:
        user_id, org_id = _ids(user)
        car = Car(**payload.model_dump(), created_by=user_id, organization_id=org_id)
        db.add(car)
        await db.commit()
        await db.refresh(car)
        return car

    @staticmethod
    async def list_cars(db: AsyncSession, user: dict, status: Optional[str] = None,
                        search: Optional[str] = None) -> List[dict]:
        _, org_id = _ids(user)
        q = (select(Car).options(selectinload(Car.images))
             .where(Car.organization_id == org_id, Car.is_active.is_(True))
             .order_by(Car.created_at.desc()))
        if status:
            q = q.where(Car.status == status)
        if search:
            term = f"%{search.strip()[:50]}%"
            q = q.where(or_(Car.name.ilike(term), Car.brand.ilike(term)))
        cars = (await db.execute(q)).scalars().all()
        return [_summary(c) for c in cars]

    @staticmethod
    async def get_car(db: AsyncSession, car_id: UUID, user: dict) -> dict:
        return _summary(await CarService._get(db, car_id, user, with_images=True))

    @staticmethod
    async def update_car(db: AsyncSession, payload: CarUpdateSchema, user: dict) -> Car:
        car = await CarService._get(db, payload.car_id, user)
        changes = payload.model_dump(exclude_unset=True, exclude={"car_id"})
        actual = Decimal(changes.get("actual_price", car.actual_price))
        discounted = changes.get("discounted_price", car.discounted_price)
        if discounted is not None and Decimal(discounted) >= actual:
            raise HTTPException(422, "Discounted price must be less than actual price")
        for key, value in changes.items():
            setattr(car, key, value)
        await db.commit()
        await db.refresh(car)
        return car

    @staticmethod
    async def delete_car(db: AsyncSession, car_id: UUID, user: dict) -> None:
        car = await CarService._get(db, car_id, user)
        car.is_active = False
        await db.commit()

    # ---------- images ----------

    @staticmethod
    async def upload_car_images(db: AsyncSession, car_id: UUID, image_type: str,
                                files: List[UploadFile], user: dict) -> List[CarImage]:
        image_type = (image_type or "").lower()
        if image_type not in IMAGE_TYPES:  # also blocks path traversal via image_type
            raise HTTPException(400, f"image_type must be one of: {', '.join(sorted(IMAGE_TYPES))}")
        if not files or len(files) > MAX_FILES_PER_UPLOAD:
            raise HTTPException(400, f"Upload 1 to {MAX_FILES_PER_UPLOAD} images at a time")
        await CarService._get(db, car_id, user)

        storage = get_storage()
        _, org_id = _ids(user)
        base_path = f"org/{org_id}/cars/{car_id}/{image_type}"
        images = []
        for file in files:
            if file.content_type != "image/webp" or not (file.filename or "").lower().endswith(".webp"):
                raise HTTPException(400, "Only WEBP images allowed")
            if file.size is not None and file.size > MAX_IMAGE_BYTES:
                raise HTTPException(413, "Each image must be 5 MB or smaller")
            path = await storage.upload(file, base_path)
            img = CarImage(car_id=car_id, image_type=image_type, image_url=path,
                           content_type=file.content_type,
                           file_size_kb=(file.size or 0) // 1024 or None)
            db.add(img)
            images.append(img)
        await db.commit()
        for img in images:
            await db.refresh(img)
        return images

    @staticmethod
    async def get_car_images(db: AsyncSession, car_id: UUID, user: dict,
                             image_type: Optional[str] = None) -> List[CarImage]:
        await CarService._get(db, car_id, user)
        q = select(CarImage).where(CarImage.car_id == car_id, CarImage.is_active.is_(True))
        if image_type:
            q = q.where(CarImage.image_type == image_type)
        return (await db.execute(q.order_by(CarImage.display_order))).scalars().all()

    @staticmethod
    async def delete_car_image(db: AsyncSession, image_id: UUID, user: dict) -> None:
        _, org_id = _ids(user)
        image = (await db.execute(
            select(CarImage).join(Car).where(
                CarImage.id == image_id, Car.organization_id == org_id, CarImage.is_active.is_(True))
        )).scalar_one_or_none()
        if not image:
            raise HTTPException(404, "Image not found")
        image.is_active = False
        await db.commit()

    @staticmethod
    async def delete_all_car_images(db: AsyncSession, car_id: UUID, user: dict) -> None:
        for img in await CarService.get_car_images(db, car_id, user):
            img.is_active = False
        await db.commit()
