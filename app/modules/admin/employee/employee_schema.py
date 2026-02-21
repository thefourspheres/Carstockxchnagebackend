from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date

class EmployeeSignupRequest(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    address: str | None = None
    blood_group: str | None = None
    date_of_birth: date | None = None
    designation: str | None = None
    password: str
    is_active: Optional[bool] = None







    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 characters")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
