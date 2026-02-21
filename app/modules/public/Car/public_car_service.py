from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.admin.cars.car_model import Car
from app.modules.admin.cars.car_image_model import CarImage


class PublicCarService:

    # 1️⃣ Homepage cars (basic details + banner)
    @staticmethod
    async def get_homepage_cars(db: AsyncSession):
        result = await db.execute(
            select(Car).where(Car.is_active == True)
        )
        cars = result.scalars().all()

        response = []

        for car in cars:
            banner_result = await db.execute(
                select(CarImage.image_url)
                .where(
                    CarImage.car_id == car.id,
                    CarImage.image_type == "banner"
                )
                .limit(1)
            )
            banner_image = banner_result.scalar()

            response.append({
                "car_id": str(car.id),
                "car_name": car.name,
                "car_brand": car.brand,
                "car_price": car.price,
                "fuel_type": car.fuel_type,
                "owner_series": getattr(car, "owner_series", None),
                "kilometer": car.kilometer,
                "car_type": getattr(car, "car_type", None),
                "banner_image": banner_image
            })

        return response


    # 2️⃣ All cars with full details + banner only
    @staticmethod
    async def get_all_cars_full(db: AsyncSession):
        result = await db.execute(select(Car))
        cars = result.scalars().all()

        data = []

        for car in cars:
            banner_result = await db.execute(
                select(CarImage.image_type)
                .where(
                    CarImage.car_id == car.id,
                    CarImage.image_type == "banner"
                )
                .limit(1)
            )

            data.append({
                "car": car,
                "banner_image": banner_result.scalar()
            })

        return data


    # 3️⃣ All images by car_id (grouped by type)
    @staticmethod
    async def get_car_images(db: AsyncSession, car_id: str):
        result = await db.execute(
            select(CarImage).where(CarImage.car_id == car_id)
        )
        images = result.scalars().all()

        response = {}

        for img in images:
            response.setdefault(img.image_type, []).append(img.image_path)

        return {
            "car_id": car_id,
            "images": response
        }
