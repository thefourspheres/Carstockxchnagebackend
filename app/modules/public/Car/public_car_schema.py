from pydantic import BaseModel
from uuid import UUID
from typing import List, Dict, Optional

class HomePageCarResponse(BaseModel):
    car_id: UUID
    name: str
    brand: str
    price: int
    fuel_type: Optional[str]
    ownership: Optional[str]
    kilometer: Optional[int]
    # car_type: Optional[str]
    banner_image: Optional[str]


class CarFullDetailsResponse(BaseModel):
    car_id: UUID
    name: str
    brand: str
    price: int
    fuel_type: Optional[str]
    ownership: Optional[str]
    kilometer: Optional[int]
    banner_image: Optional[str]


class CarImagesResponse(BaseModel):
    image_type: str
    images: List[str]

class CarImagesRequest(BaseModel):
    car_id: UUID