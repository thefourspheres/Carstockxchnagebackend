# role_schema.py
from pydantic import BaseModel
from uuid import UUID

class RoleCreate(BaseModel):
    name: str


class AssignRoleSchema(BaseModel):
    employee_id: UUID
    role_id: int

class RoleResponse(BaseModel):
    id: int
    name: str