from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class CallbackRequest(BaseModel):
    name: str
    mobile: str
    description: Optional[str] = None
    whatsapp_opt_in: bool = True


class TestDriveRequest(BaseModel):
    name: str
    mobile: str
    car_brand: str
    car_model: str
    whatsapp_opt_in: bool = True


class CarReportRequest(BaseModel):
    name: str
    mobile: str
    email: EmailStr
    car_id: UUID
    whatsapp_opt_in: bool = True


class carsalerequest(BaseModel):
    Ownername: str
    carregisteryear: int
    mobile: str
    email: EmailStr
    car_model: str
    expected_price: float