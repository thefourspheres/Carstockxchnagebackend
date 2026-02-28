from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.params import Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.permissions import requireORGANIZATION_ADMIN

from app.core.database import get_db
from app.core.permissions import require_roles
from .car_schema import (
    CarCreateSchema,
    CarUpdateSchema,
    CarIDOnlySchema,
)
from .car_service import CarService

router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)

# =======================
# CAR CRUD
# =======================

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car(
    payload: CarCreateSchema,
    db: AsyncSession = Depends(get_db),
    # user=Depends(requireORGANIZATION_ADMIN())
    user=Depends(require_roles("SALES","PURCHASE"))
):
    car = await CarService.create_car(db, payload, user)
    return {
        "success": True,
        "message": "Car created successfully",
        "car_id": str(car.id)
    }


@router.post("/list", status_code=status.HTTP_200_OK)
async def list_cars(
    db: AsyncSession = Depends(get_db),
    # user=Depends(requireORGANIZATION_ADMIN())):
    user=Depends(require_roles("SALES","PURCHASE"))):

    #  "ADMIN", "SUPER_ADMIN", "PURCHASE"
    cars = await CarService.get_my_cars(db, user)
    return {
        "success": True,
        "total": len(cars),
        "cars": cars
    }


@router.post("/details", status_code=status.HTTP_200_OK)
async def car_details(
    payload: CarIDOnlySchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("PURCHASE"))
):
    car = await CarService.get_car_by_id(db, payload.car_id, user)
    return {
        "success": True,
        "data": car
    }


@router.post("/update", status_code=status.HTTP_200_OK)
async def update_car(
    payload: CarUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("PURCHASE"))
):
    car = await CarService.update_car(db, payload.car_id, payload, user)
    return {
        "success": True,
        "message": "Car updated successfully",
        "car_id": str(car.id)
    }


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_car(
    payload: CarIDOnlySchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("PURCHASE"))
):
    await CarService.delete_car(db, payload.car_id, user)
    return {
        "success": True,
        "message": "Car deleted successfully"
    }


@router.post("/delete-permanent", status_code=status.HTTP_200_OK)
async def delete_car_permanent(
    payload: CarIDOnlySchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("PURCHASE"))
):
    await CarService.hard_delete_car(db, payload.car_id, user)
    return {
        "success": True,
        "message": "Car permanently deleted"
    }

# =======================
# CAR IMAGES
# =======================

@router.post("/upload-images", status_code=status.HTTP_201_CREATED)
async def upload_car_images(
    car_id: UUID = Form(...),
    image_type: str = Form(...),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    # user=Depends(requireORGANIZATION_ADMIN())
    user=Depends(require_roles("SALES","PURCHASE"))
):
    """
    Upload multiple images for a car (ALL DATA FROM BODY)
    """
    result = await CarService.upload_car_images(
        db=db,
        car_id=car_id,
        image_type=image_type,
        files=files,
        user=user
    )

    return {
        "success": True,
        "message": f"{len(result)} image(s) uploaded",
        "car_id": str(car_id),
        "image_type": image_type,
        "uploaded_count": len(result),
        "images": [
            {
            "id": str(img.id),
            "image_url": img.image_url,
            "image_type": img.image_type,
            "content_type": img.content_type,
            "is_primary": img.is_primary,
            "display_order": img.display_order,
            "created_at": img.created_at.isoformat() if img.created_at else None
            }
            for img in result
        ]
    }
    
    

@router.post("/get-images", status_code=status.HTTP_200_OK)
async def get_images(
    payload: CarIDOnlySchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("SALES","PURCHASE"))
    # user=Depends(requireORGANIZATION_ADMIN())
):
    images = await CarService.get_car_images(
        db, payload.car_id, user
    )
    return {
        "success": True,
        "total_images": len(images),
        "images": images
    }


@router.post("/delete-image", status_code=status.HTTP_200_OK)
async def delete_image(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("PURCHASE"))
):
    await CarService.delete_car_image(db, image_id, user)
    return {
        "success": True,
        "message": "Image deleted"
    }


@router.post("/delete-all-images", status_code=status.HTTP_200_OK)
async def delete_all_images(
    payload: CarIDOnlySchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("PURCHASE"))
):
    await CarService.delete_all_car_images(db, payload.car_id, user)
    return {
        "success": True,
        "message": "All images deleted"
    }


@router.post("/health", status_code=status.HTTP_200_OK)
async def health():
    return {
        "success": True,
        "status": "healthy",
        "module": "cars"
    }
