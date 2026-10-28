from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import CAR_MANAGE, CAR_VIEW, require_roles
from .car_options import OPTIONS
from .car_schema import (
    CarCreateSchema,
    CarIDOnlySchema,
    CarResponseSchema,
    CarUpdateSchema,
    ImageDeleteSchema,
    Status,
)
from .car_service import CarService

router = APIRouter(prefix="/cars", tags=["Cars"])
can_view = require_roles(*CAR_VIEW)
can_manage = require_roles(*CAR_MANAGE)


class CarListFilter(BaseModel):
    status: Optional[Status] = None
    search: Optional[str] = None


@router.get("/options")
async def car_options(user=Depends(can_view)):
    return OPTIONS


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car(payload: CarCreateSchema, db: AsyncSession = Depends(get_db), user=Depends(can_manage)):
    car = await CarService.create_car(db, payload, user)
    return {"success": True, "message": "Car created successfully", "car_id": str(car.id)}


@router.put("/update")
async def update_car(payload: CarUpdateSchema, db: AsyncSession = Depends(get_db), user=Depends(can_manage)):
    await CarService.update_car(db, payload, user)
    return {"success": True, "message": "Car updated successfully"}


@router.post("/list")
async def list_cars(payload: Optional[CarListFilter] = None, db: AsyncSession = Depends(get_db),
                    user=Depends(can_view)):
    f = payload or CarListFilter()
    cars = await CarService.list_cars(db, user, f.status, f.search)
    return {"success": True, "total": len(cars),
            "cars": [CarResponseSchema.model_validate(c) for c in cars]}


@router.post("/get-car-by-id")
async def get_car_by_id(payload: CarIDOnlySchema, db: AsyncSession = Depends(get_db), user=Depends(can_view)):
    car = await CarService.get_car(db, payload.car_id, user)
    return {"success": True, "data": CarResponseSchema.model_validate(car)}


@router.post("/delete")
async def delete_car(payload: CarIDOnlySchema, db: AsyncSession = Depends(get_db), user=Depends(can_manage)):
    await CarService.delete_car(db, payload.car_id, user)
    return {"success": True, "message": "Car deleted successfully"}


# ---------- images ----------

@router.post("/upload-images", status_code=status.HTTP_201_CREATED)
async def upload_car_images(
    car_id: UUID = Form(...),
    image_type: str = Form(...),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(can_manage),
):
    result = await CarService.upload_car_images(db, car_id, image_type, files, user)
    return {
        "success": True,
        "message": f"{len(result)} image(s) uploaded",
        "car_id": str(car_id),
        "uploaded_count": len(result),
        "images": [img.to_dict() | {"image_type": img.image_type} for img in result],
    }


@router.post("/get-images")
async def get_images(payload: CarIDOnlySchema, db: AsyncSession = Depends(get_db), user=Depends(can_view)):
    images = await CarService.get_car_images(db, payload.car_id, user, payload.image_type)
    return {"success": True, "total_images": len(images),
            "images": [img.to_dict() | {"image_type": img.image_type} for img in images]}


@router.post("/delete-image")
async def delete_image(payload: ImageDeleteSchema, db: AsyncSession = Depends(get_db), user=Depends(can_manage)):
    await CarService.delete_car_image(db, payload.image_id, user)
    return {"success": True, "message": "Image deleted"}


@router.post("/delete-all-images")
async def delete_all_images(payload: CarIDOnlySchema, db: AsyncSession = Depends(get_db),
                            user=Depends(can_manage)):
    await CarService.delete_all_car_images(db, payload.car_id, user)
    return {"success": True, "message": "All images deleted"}
