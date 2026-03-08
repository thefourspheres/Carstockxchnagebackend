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
                    CarImage.image_type == "banner",
                    CarImage.is_active.is_(True)
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
                select(CarImage.image_url)
                .where(
                    CarImage.car_id == car.id,
                    CarImage.image_type == "banner",
                    CarImage.is_active.is_(True)
                )
                .order_by(CarImage.display_order)
                .limit(1)
            )

            banner_image = banner_result.scalar()

            data.append({
                "id": str(car.id),
                "organization_id": str(car.organization_id),
                "created_by": str(car.created_by),
                "name": car.name,
                "brand": car.brand,
                "year": car.year,
                "kilometer": car.kilometer,
                "fuel_type": car.fuel_type,
                "transmission": car.transmission,
                "price": car.price,
                    # ✅ Specifications ek object ke andar
                "specifications": {
                "engine_specs": car.engine_specs,
                "dimensions": car.dimensions,
                "capacity_fuel": car.capacity_fuel,
                "suspension": car.suspension,
                "tyres": car.tyres,
                    },


                "features": car.features,
                "is_active": car.is_active,
                "created_at": str(car.created_at),
                "updated_at": str(car.updated_at),
                "color": car.color,
                "registration_year": car.registration_year,
                "insurance_valid_until": car.insurance_valid_until,
                "ownership": car.ownership,
                "rto": car.rto,
                "car_type": car.car_type,
                "exteriors_lights_rating": car.exteriors_lights_rating,
                "core_systems_rating": car.core_systems_rating,
                "supporting_systems_rating": car.supporting_systems_rating,
                "interiors_ac_rating": car.interiors_ac_rating,
                "inspection_rating": car.inspection_rating,
                "insurance_type": car.insurance_type,
                "banner_image": banner_image
            # ❌ saleprice, bottomprice, registration_number — nahi dala
        })

        return data

    # 3️⃣ All images by car_id (grouped by type)
    @staticmethod
    async def get_car_images(db: AsyncSession, car_id: str):
        result = await db.execute(
            select(CarImage).where(CarImage.car_id == car_id)
        )
        images = result.scalars().all()

        response = []

        for img in images:
            response.append(img.image_url)

        return {
            "car_id": car_id,
            "images": response
        }
