from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.admin.cars.car_image_model import CarImage
from app.modules.admin.cars.car_model import Car
from app.modules.admin.cars.car_options import PUBLIC_STATUSES

# Never expose internal fields (created_by, organization_id, is_active).
PUBLIC_FIELDS = ("name", "brand", "car_type", "condition", "year", "fuel_type",
                 "transmission", "color", "description", "status")


def _public_car(car: Car) -> dict:
    images = sorted((i for i in car.images if i.is_active), key=lambda i: i.display_order or 0)
    banner = next((i.image_url for i in images if i.image_type == "banner"), None)
    price = car.discounted_price or car.actual_price
    return {
        "id": str(car.id),
        **{f: getattr(car, f) for f in PUBLIC_FIELDS},
        "actual_price": float(car.actual_price),
        "discounted_price": float(car.discounted_price) if car.discounted_price else None,
        "price": float(price),
        "banner_image": banner or (images[0].image_url if images else None),
    }


def _public_query():
    return (select(Car).options(selectinload(Car.images))
            .where(Car.is_active.is_(True), Car.status.in_(PUBLIC_STATUSES))
            .order_by(Car.created_at.desc()))


class PublicCarService:

    @staticmethod
    async def get_homepage_cars(db: AsyncSession, limit: int = 12):
        cars = (await db.execute(_public_query().limit(limit))).scalars().all()
        return [_public_car(c) for c in cars]

    @staticmethod
    async def get_all_cars_full(db: AsyncSession):
        cars = (await db.execute(_public_query())).scalars().all()
        return [_public_car(c) for c in cars]

    @staticmethod
    async def get_car_images(db: AsyncSession, car_id: UUID):
        rows = await db.execute(
            select(CarImage.image_url)
            .join(Car)
            .where(CarImage.car_id == car_id, CarImage.is_active.is_(True),
                   Car.is_active.is_(True), Car.status.in_(PUBLIC_STATUSES))
            .order_by(CarImage.image_type != "banner", CarImage.display_order)
        )
        return {"car_id": str(car_id), "images": list(rows.scalars())}
