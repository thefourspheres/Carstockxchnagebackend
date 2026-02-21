from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class LeadFilterRequest(BaseModel):
    lead_type: Optional[str] = None
    status: Optional[str] = None
    assigned_department: Optional[str] = None


class LeadResponse(BaseModel):
    id: UUID
    lead_type: str
    name: str
    mobile: str
    email: Optional[str] = None
    description: Optional[str] = None
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_id: Optional[UUID] = None
    status: str
    assigned_department: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CarSalesLeadResponse(BaseModel):
    id: UUID
    ownername: str
    carregisteryear: int
    mobile: str
    email: Optional[str] = None
    car_model: Optional[str] = None
    expected_price: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    