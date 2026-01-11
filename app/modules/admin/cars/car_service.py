from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from typing import List
from uuid import UUID

from .car_model import Car
from .car_image_model import CarImage
from .car_schema import CarCreateSchema, CarUpdateSchema
from app.core.storage.factory import get_storage


class CarService:

    # =====================
    # INTERNAL HELPERS
    # =====================
    @staticmethod
    def _uuid(value: str | UUID) -> UUID:
        if isinstance(value, UUID):
            return value
        return UUID(value)

    # =====================
    # CAR CRUD
    # =====================
    @staticmethod
    async def create_car(db: AsyncSession, payload: CarCreateSchema, user: dict):
        car = Car(
            **payload.model_dump(exclude_none=True),
            created_by=CarService._uuid(user["sub"]),
            organization_id=CarService._uuid(user["organization_id"]),
        )
        db.add(car)
        await db.commit()
        await db.refresh(car)
        return car

    @staticmethod
    async def get_my_cars(db: AsyncSession, user: dict):
        user_id = CarService._uuid(user["sub"])
        result = await db.execute(
            select(Car)
            .options(selectinload(Car.images))
            .where(Car.created_by == user_id, Car.is_active.is_(True))
        )
        return result.scalars().all()

    @staticmethod
    async def get_car_by_id(db: AsyncSession, car_id: UUID, user: dict):
        user_id = CarService._uuid(user["sub"])
        result = await db.execute(
            select(Car)
            .options(selectinload(Car.images))
            .where(
                Car.id == car_id,
                Car.created_by == user_id,
                Car.is_active.is_(True)
            )
        )
        car = result.scalar_one_or_none()
        if not car:
            raise HTTPException(404, "Car not found")
        return car

    @staticmethod
    async def update_car(db: AsyncSession, car_id: UUID, payload: CarUpdateSchema, user: dict):
        car = await CarService.get_car_by_id(db, car_id, user)
        for k, v in payload.model_dump(exclude={"car_id"}, exclude_none=True).items():
            setattr(car, k, v)
        await db.commit()
        await db.refresh(car)
        return car

    @staticmethod
    async def delete_car(db: AsyncSession, car_id: UUID, user: dict):
        car = await CarService.get_car_by_id(db, car_id, user)
        car.is_active = False
        await db.commit()

    # =====================
    # IMAGE MANAGEMENT
    # =====================
    @staticmethod
    async def upload_car_images(
        db: AsyncSession,
        car_id: UUID,
        image_type: str,
        files: List,
        user: dict
    ):
        await CarService.get_car_by_id(db, car_id, user)
        storage = get_storage()
        images = []

        base_path = f"org/{user['organization_id']}/cars/{car_id}/{image_type}"

        for file in files:
            if not file.filename.lower().endswith(".webp"):
                raise HTTPException(400, "Only WEBP images allowed")

            path = await storage.upload(file, base_path)
            img = CarImage(
                car_id=car_id,
                image_type=image_type,
                image_url=path,
                # file_name=file.filename,
                content_type=file.content_type,
                # created_by=CarService._uuid(user["sub"])
            )
            db.add(img)
            images.append(img)

        await db.commit()
        for img in images:
            await db.refresh(img)

        return images

    @staticmethod
    async def get_car_images(
        db: AsyncSession,
        car_id: UUID,
        user: dict,
        image_type: str | None = None
    ):
        await CarService.get_car_by_id(db, car_id, user)

        stmt = select(CarImage).where(
            CarImage.car_id == car_id,
            CarImage.is_active.is_(True)
        )
        if image_type:
            stmt = stmt.where(CarImage.image_type == image_type)

        result = await db.execute(stmt.order_by(CarImage.display_order))
        return result.scalars().all()

    @staticmethod
    async def delete_car_image(db: AsyncSession, image_id: UUID, user: dict):
        user_id = CarService._uuid(user["sub"])

        result = await db.execute(
            select(CarImage)
            .join(Car)
            .where(
                CarImage.id == image_id,
                Car.created_by == user_id,
                CarImage.is_active.is_(True)
            )
        )
        image = result.scalar_one_or_none()
        if not image:
            raise HTTPException(404, "Image not found")

        image.is_active = False
        await db.commit()

    @staticmethod
    async def set_primary_image(db: AsyncSession, car_id: UUID, image_id: UUID, user: dict):
        await CarService.get_car_by_id(db, car_id, user)
        result = await db.execute(
            select(CarImage).where(
                CarImage.id == image_id,
                CarImage.car_id == car_id,
                CarImage.is_active.is_(True)
            )
        )
        image = result.scalar_one_or_none()
        if not image:
            raise HTTPException(404, "Image not found")

        await image.mark_as_primary(db)
        await db.commit()
