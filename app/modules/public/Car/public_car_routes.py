from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.public.Car.public_car_schema import CarImagesRequest
from .public_car_service import PublicCarService

router = APIRouter(
    prefix="/public/cars",
    tags=["Public Cars"]
)

# 1️⃣ Homepage API
@router.get("/homepage")
async def homepage_cars(db: AsyncSession = Depends(get_db)):
    return await PublicCarService.get_homepage_cars(db)


# 2️⃣ All Cars with Full Details (Banner only)
@router.get("/all")
async def all_cars(db: AsyncSession = Depends(get_db)):
    return await PublicCarService.get_all_cars_full(db)


@router.post("/images")
async def car_images(
    payload: CarImagesRequest,
    db: AsyncSession = Depends(get_db)
):
    return await PublicCarService.get_car_images(db, payload.car_id)