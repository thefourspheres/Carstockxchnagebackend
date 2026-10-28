import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _indian_mobile(v: str) -> str:
    digits = re.sub(r"\D", "", v or "")
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if not re.fullmatch(r"[6-9]\d{9}", digits):
        raise ValueError("Enter a valid 10-digit mobile number")
    return digits


class _Public(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    mobile_ok = field_validator("mobile", check_fields=False)(_indian_mobile)


class CallbackRequest(_Public):
    name: str = Field(..., min_length=2, max_length=150)
    mobile: str
    description: Optional[str] = Field(None, max_length=1000)
    whatsapp_opt_in: bool = True


class TestDriveRequest(_Public):
    name: str = Field(..., min_length=2, max_length=150)
    mobile: str
    car_brand: str = Field(..., min_length=1, max_length=100)
    car_model: str = Field(..., min_length=1, max_length=100)
    whatsapp_opt_in: bool = True


class CarReportRequest(_Public):
    name: str = Field(..., min_length=2, max_length=150)
    mobile: str
    email: EmailStr
    car_id: UUID
    whatsapp_opt_in: bool = True


class carsalerequest(_Public):
    Ownername: str = Field(..., min_length=2, max_length=150)
    carregisteryear: int
    mobile: str
    email: EmailStr
    car_model: str = Field(..., min_length=1, max_length=100)
    expected_price: float = Field(..., gt=0, le=100_000_000)

    @field_validator("carregisteryear")
    @classmethod
    def year_ok(cls, v):
        if not 1980 <= v <= datetime.now().year:
            raise ValueError("Enter a valid registration year")
        return v
