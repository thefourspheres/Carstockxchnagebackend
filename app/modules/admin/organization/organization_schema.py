# organization_schema.py
from pydantic import BaseModel, EmailStr

class CreateOrganizationAdminRequest(BaseModel):
    organization_name: str
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    admin_mobile: str
