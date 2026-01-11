from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_super_admin
from app.modules.admin.employee.employee_model import Employee
from app.modules.admin.organization.organization_model import Organization
from app.modules.admin.organization.organization_schema import CreateOrganizationAdminRequest
from app.modules.admin.organization.organization_service import OrganizationService
from app.modules.admin.role.employee_role_model import EmployeeRole
from app.modules.admin.role.role_model import Role
from app.utils.hashing import hash_password

router = APIRouter(
    prefix="/super-admin/organizations",
    tags=["Super Admin"]
)
@router.post("/create-organization")
async def create_organization_with_admin(
    payload: CreateOrganizationAdminRequest,
    
    user=Depends(require_super_admin()),
    db: AsyncSession = Depends(get_db)


):
    org = Organization(name=payload.organization_name)
    db.add(org)
    await db.flush()

    admin = Employee(
        name=payload.admin_name,
        email=payload.admin_email,
        mobile=payload.admin_mobile,   #NOW IT WILL PASS

        password_hash=hash_password(payload.admin_password),
        designation="ADMIN",
        organization_id=org.id,
        is_active=True
    )
    print(payload.admin_mobile)

    db.add(admin)
    await db.commit()

    return {"message": "Organization and admin created"}



