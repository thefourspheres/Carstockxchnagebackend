from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.admin.role.role_model import Role
from app.modules.admin.role.employee_role_model import EmployeeRole

class RoleRepository:

    @staticmethod
    async def get_roles(db: AsyncSession, employee_id):
        result = await db.execute(
            select(Role.name)
            .join(EmployeeRole, Role.id == EmployeeRole.role_id)
            .where(EmployeeRole.employee_id == employee_id)
        )
        return result.scalars().all()
