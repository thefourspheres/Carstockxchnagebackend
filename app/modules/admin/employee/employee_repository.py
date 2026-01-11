from sqlalchemy.future import select
from .employee_model import Employee
from app.modules.admin.role.role_model import Role
from app.modules.admin.role.employee_role_model import EmployeeRole

class EmployeeRepository:

    @staticmethod
    async def get_by_email(db, email):
        result = await db.execute(select(Employee).where(Employee.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_roles(db, employee_id):
        result = await db.execute(
            select(Role.name)
            .join(EmployeeRole, Role.id == EmployeeRole.role_id)
            .where(EmployeeRole.employee_id == employee_id)
        )
        return [r[0] for r in result.all()]
