from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CarType = Literal["Hatchback", "Sedan", "SUV", "MUV", "Coupe", "Convertible", "Pickup", "Van"]
Condition = Literal["New", "Used", "Certified Pre-Owned"]
FuelType = Literal["Petrol", "Diesel", "CNG", "Electric", "Hybrid"]
Transmission = Literal["Manual", "Automatic", "AMT", "CVT", "DCT"]
Status = Literal["Available", "Reserved", "Sold", "Draft"]

MIN_YEAR = 1980
Price = Decimal


def _max_year() -> int:
    return datetime.now().year + 1


def _clean(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v = " ".join(v.split())
    return v or None


def _check_year(v: Optional[int]) -> Optional[int]:
    if v is not None and not MIN_YEAR <= v <= _max_year():
        raise ValueError(f"Model year must be between {MIN_YEAR} and {_max_year()}")
    return v


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CarCreateSchema(_Strict):
    name: str = Field(..., min_length=2, max_length=100)
    brand: str = Field(..., min_length=2, max_length=50)
    car_type: CarType
    condition: Condition
    year: int
    fuel_type: FuelType
    transmission: Transmission
    color: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = Field(None, max_length=2000)
    actual_price: Price = Field(..., gt=0, le=Decimal("100000000"), decimal_places=2)
    discounted_price: Optional[Price] = Field(None, gt=0, le=Decimal("100000000"), decimal_places=2)
    status: Status = "Available"

    squash_text = field_validator("name", "brand", "color")(_clean)
    check_year = field_validator("year")(_check_year)

    @model_validator(mode="after")
    def _discount_below_actual(self):
        if self.discounted_price is not None and self.discounted_price >= self.actual_price:
            raise ValueError("Discounted price must be less than actual price")
        return self


class CarUpdateSchema(_Strict):
    car_id: UUID
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    brand: Optional[str] = Field(None, min_length=2, max_length=50)
    car_type: Optional[CarType] = None
    condition: Optional[Condition] = None
    year: Optional[int] = None
    fuel_type: Optional[FuelType] = None
    transmission: Optional[Transmission] = None
    color: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = Field(None, max_length=2000)
    actual_price: Optional[Price] = Field(None, gt=0, le=Decimal("100000000"), decimal_places=2)
    discounted_price: Optional[Price] = Field(None, gt=0, le=Decimal("100000000"), decimal_places=2)
    status: Optional[Status] = None

    squash_text = field_validator("name", "brand", "color")(_clean)
    check_year = field_validator("year")(_check_year)

    @model_validator(mode="after")
    def _required_stay_required(self):
        # Explicit null would wipe a NOT NULL column.
        required = {"name", "brand", "car_type", "condition", "year", "fuel_type",
                    "transmission", "actual_price", "status"}
        nulled = sorted(f for f in self.model_fields_set & required if getattr(self, f) is None)
        if nulled:
            raise ValueError(f"These fields cannot be empty: {', '.join(nulled)}")
        return self


class CarIDOnlySchema(BaseModel):
    car_id: UUID
    image_type: Optional[str] = None


CarIdSchema = CarIDOnlySchema


class ImageDeleteSchema(BaseModel):
    image_id: UUID


class CarResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    brand: str
    car_type: str
    condition: str
    year: int
    fuel_type: str
    transmission: str
    color: Optional[str]
    description: Optional[str]
    actual_price: Decimal
    discounted_price: Optional[Decimal]
    status: str
    banner_image: Optional[str] = None
    image_count: int = 0
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
