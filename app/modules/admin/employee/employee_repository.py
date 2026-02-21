from sqlalchemy import update
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

    @staticmethod
    async def get_all(db, organization_id):
        result = await db.execute(
            select(Employee).where(
                Employee.organization_id == organization_id,
                Employee.is_active == True
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db, employee_id):
        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_employee(db, employee_id, data: dict):
        await db.execute(
            update(Employee)
            .where(Employee.id == employee_id)
            .values(**data)
        )
        await db.commit()

    @staticmethod
    async def soft_delete(db, employee_id):
        await db.execute(
            update(Employee)
            .where(Employee.id == employee_id)
            .values(is_active=False)
        )
        await db.commit()

    @staticmethod
    async def hard_delete(db, employee_id):
        employee = await EmployeeRepository.get_by_id(db, employee_id)
        if employee:
            await db.delete(employee)
            await db.commit()
