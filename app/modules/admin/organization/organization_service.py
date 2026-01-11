from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.modules.admin.organization.organization_model import Organization
from app.modules.admin.employee.employee_model import Employee
from app.core.security import hash_password

class OrganizationService:

    @staticmethod
    async def create_org_with_admin(
        db: AsyncSession,
        payload
    ):
        try:
            # 1️⃣ Create Organization
            org = Organization(name=payload.organization_name)
            db.add(org)
            await db.flush()  # get org.id

            # 2️⃣ Create Admin Employee
            admin = Employee(
                name=payload.admin_name,
                email=payload.admin_email,
                password_hash=hash_password(payload.admin_password),
                designation="ADMIN",
                organization_id=org.id,
                is_active=True
            )

            db.add(admin)
            await db.commit()

            return {
                "message": "Organization and Admin created",
                "organization_id": str(org.id),
                "admin_email": admin.email
            }

        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Organization or admin already exists"
            )
