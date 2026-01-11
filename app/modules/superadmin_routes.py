from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.permissions import require_super_admin
from app.core.security import hash_password

from app.modules.admin.organization.organization_model import Organization
from app.modules.admin.employee.employee_model import Employee
from app.modules.admin.role.employee_role_model import EmployeeRole
from app.modules.admin.role.role_model import Role
from app.modules.admin.organization.organization_schema import CreateOrganizationAdminRequest

router = APIRouter(
    prefix="/superadmin",
    tags=["Super Admin"]
)

@router.post("/create-organization")
async def create_organization_with_admin(
    payload: CreateOrganizationAdminRequest,
    user=Depends(require_super_admin()),
    db: AsyncSession = Depends(get_db)
):
    # 1️⃣ Create organization
    org = Organization(name=payload.organization_name)
    db.add(org)
    await db.flush()

    # 2️⃣ Create admin user
    admin = Employee(
        name=payload.admin_name,
        email=payload.admin_email,
        password_hash=hash_password(payload.admin_password),
        designation="ORGANIZATION_ADMIN",
        organization_id=org.id,
        is_active=True
    )
    db.add(admin)
    await db.flush()

    # 3️⃣ Assign ADMIN role
    result = await db.execute(
        select(Role).where(Role.name == "ORGANIZATION_ADMIN")
    )
    role = result.scalar_one()

    db.add(EmployeeRole(
        employee_id=admin.id,
        role_id=role.id
    ))

    await db.commit()

    return {
        "message": "Organization and Admin created successfully",
        "organization_id": str(org.id),
        "admin_id": str(admin.id)
    }
