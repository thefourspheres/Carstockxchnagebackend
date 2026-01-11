from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.admin.employee.employee_model import Employee
from app.modules.admin.role.role_repository import RoleRepository
from app.core.security import verify_password, create_access_token
from fastapi import HTTPException

class AuthService:

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str,orgid:str):
        result = await db.execute(
            select(Employee).where(Employee.email == email, Employee.is_active == True,Employee.organization_id==orgid)
        )
        employee = result.scalar_one_or_none()

        if not employee or not verify_password(password, employee.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        roles = await RoleRepository.get_roles(db, employee.id)

        token = create_access_token({
            "sub": str(employee.id),
            "roles": roles,
            "organization_id":orgid

        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "roles": roles,
            "organization_id":orgid
        }

