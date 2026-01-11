from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.permissions import requireORGANIZATION_ADMIN
from app.modules.admin.role.role_model import Role
from app.modules.admin.role.employee_role_model import EmployeeRole
from app.modules.admin.employee.employee_model import Employee
from uuid import UUID

from app.modules.admin.role.role_schema import AssignRoleSchema, RoleCreate, RoleResponse

router = APIRouter(prefix="/admin/roles", tags=["Roles"])

@router.post("/create")
async def create_role(
    payload: RoleCreate,
    user = Depends(requireORGANIZATION_ADMIN()),
    db: AsyncSession = Depends(get_db)
):
    # Check if role already exists
    existing_role = await db.execute(
        select(Role).where(Role.name == payload.name.upper())
    )
    if existing_role.scalar_one_or_none():
        raise HTTPException(
            status_code=404,
            detail=f"Role '{payload.name}' already exists"
        )
    
    # Create the role
    role = Role(name=payload.name.upper())
    db.add(role)
    await db.commit()
    await db.refresh(role)  # Refresh to get the ID and any default values
    
    return {
        "message": "Role created successfully",
        "role": {
            "id": role.id,
            "name": role.name,
        }
    }


@router.post("/assign")
async def assign_role(
    payload: AssignRoleSchema,
    user=Depends(requireORGANIZATION_ADMIN()),
    db: AsyncSession = Depends(get_db)
):
    emp = await db.get(Employee, payload.employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    role = await db.get(Role, payload.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    exists = await db.execute(
        select(EmployeeRole).where(
            EmployeeRole.employee_id == payload.employee_id,
            EmployeeRole.role_id == payload.role_id
        )
    )

    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Role already assigned")

    db.add(
        EmployeeRole(
            employee_id=payload.employee_id,
            role_id=payload.role_id
        )
    )




    await db.commit()

    return {"message": "Role assigned successfully"}


@router.get("/getroles", response_model=List[RoleResponse])
async def get_active_roles(
    user = Depends(requireORGANIZATION_ADMIN()),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Role).order_by(Role.id)
    )
    roles = result.scalars().all()
    return roles