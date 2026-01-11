from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime


# =========================
# CREATE CAR
# =========================
class CarCreateSchema(BaseModel):
    # Required
    name: str = Field(..., min_length=1, max_length=100)
    brand: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=datetime.now().year + 1)

    # Optional basics
    kilometer: Optional[int] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, max_length=20)
    transmission: Optional[str] = Field(None, max_length=20)
    price: Optional[int] = Field(None, ge=0)

    # JSON / flexible fields
    engine_specs: Optional[Union[Dict[str, Any], str]] = None
    dimensions: Optional[Union[Dict[str, Any], str]] = None
    capacity_fuel: Optional[Union[Dict[str, Any], str]] = None
    suspension: Optional[Union[Dict[str, Any], str]] = None
    tyres: Optional[Union[Dict[str, Any], str]] = None
    features: Optional[Union[Dict[str, Any], str]] = None

    # Extra details
    color: Optional[str] = None
    registration_number: Optional[str] = None
    registration_year: Optional[int] = None
    insurance_valid_until: Optional[str] = None
    ownership: Optional[str] = None
    rto: Optional[str] = None

    # -------------------------
    # Validators
    # -------------------------
    @field_validator("fuel_type")
    @classmethod
    def validate_fuel_type(cls, v):
        if not v:
            return v
        v = v.lower()
        if v == "disel":
            return "Diesel"
        if v not in {"petrol", "diesel", "cng", "electric", "hybrid"}:
            raise ValueError("Fuel type must be Petrol, Diesel, CNG, Electric, or Hybrid")
        return v.title()

    @field_validator("transmission")
    @classmethod
    def validate_transmission(cls, v):
        if not v:
            return v
        v = v.lower()
        if v not in {"manual", "automatic", "cvt", "amt", "dct"}:
            raise ValueError("Transmission must be Manual, Automatic, CVT, AMT, or DCT")
        return v.upper() if v in {"cvt", "amt", "dct"} else v.title()

    @field_validator("insurance_valid_until")
    @classmethod
    def validate_insurance_date(cls, v):
        if v:
            datetime.strptime(v, "%Y-%m-%d")
        return v


# =========================
# UPDATE CAR
# =========================
class CarUpdateSchema(BaseModel):
    car_id: UUID = Field(..., description="Car ID to update")

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    brand: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=datetime.now().year + 1)
    kilometer: Optional[int] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, max_length=20)
    transmission: Optional[str] = Field(None, max_length=20)
    price: Optional[int] = Field(None, ge=0)

    engine_specs: Optional[Union[Dict[str, Any], str]] = None
    dimensions: Optional[Union[Dict[str, Any], str]] = None
    capacity_fuel: Optional[Union[Dict[str, Any], str]] = None
    suspension: Optional[Union[Dict[str, Any], str]] = None
    tyres: Optional[Union[Dict[str, Any], str]] = None
    features: Optional[Union[Dict[str, Any], str]] = None

    color: Optional[str] = None
    registration_number: Optional[str] = None
    registration_year: Optional[int] = None
    insurance_valid_until: Optional[str] = None
    ownership: Optional[str] = None
    rto: Optional[str] = None

    @field_validator("fuel_type")
    @classmethod
    def validate_fuel_type(cls, v):
        return CarCreateSchema.validate_fuel_type(v)

    @field_validator("transmission")
    @classmethod
    def validate_transmission(cls, v):
        return CarCreateSchema.validate_transmission(v)

    @field_validator("insurance_valid_until")
    @classmethod
    def validate_insurance_date(cls, v):
        return CarCreateSchema.validate_insurance_date(v)


# =========================
# SIMPLE REQUEST SCHEMAS
# =========================
class CarIDOnlySchema(BaseModel):
    car_id: UUID


class CarDeleteSchema(BaseModel):
    car_id: UUID
    confirm: bool


# =========================
# RESPONSE SCHEMA
# =========================
class CarResponseSchema(BaseModel):
    id: UUID
    name: str
    brand: str
    year: int

    kilometer: Optional[int]
    fuel_type: Optional[str]
    transmission: Optional[str]
    price: Optional[int]

    engine_specs: Optional[Union[Dict[str, Any], str]]
    dimensions: Optional[Union[Dict[str, Any], str]]
    capacity_fuel: Optional[Union[Dict[str, Any], str]]
    suspension: Optional[Union[Dict[str, Any], str]]
    tyres: Optional[Union[Dict[str, Any], str]]
    features: Optional[Union[Dict[str, Any], str]]

    color: Optional[str]
    registration_number: Optional[str]
    registration_year: Optional[int]
    insurance_valid_until: Optional[str]
    ownership: Optional[str]
    rto: Optional[str]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
