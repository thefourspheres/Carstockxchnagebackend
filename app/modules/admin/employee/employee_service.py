from fastapi import HTTPException

from app.modules.admin.employee.email_service import send_welcome_email
from .employee_model import Employee
from .employee_repository import EmployeeRepository
from app.utils.hashing import hash_password

class EmployeeService:

    @staticmethod
    # async def signup(db, payload,admin_user: dict):
    #     if await EmployeeRepository.get_by_email(db, payload.email):
    #         raise ValueError("Email already exists")
        
    #     organization_id = admin_user.get("organization_id")

    #     employee = Employee(
    #         name=payload.name,
    #         email=payload.email,
    #         mobile=payload.mobile,
    #         address=payload.address,
    #         blood_group=payload.blood_group,
    #         date_of_birth=payload.date_of_birth,
    #         designation=payload.designation,
    #         organization_id=organization_id,
    #         password_hash=hash_password(payload.password)
    #     )

    #     db.add(employee)
    #     await db.commit()
    async def signup(db, payload, admin_user: dict):
        if await EmployeeRepository.get_by_email(db, payload.email):
         raise ValueError("Email already exists")

        organization_id = admin_user.get("organization_id")

        employee = Employee(
        name=payload.name,
        email=payload.email,
        mobile=payload.mobile,
        address=payload.address,
        blood_group=payload.blood_group,
        date_of_birth=payload.date_of_birth,
        designation=payload.designation,
        organization_id=organization_id,
        password_hash=hash_password(payload.password)
    )

        db.add(employee)
        await db.commit()
        await db.refresh(employee)

    # 🔹 Send welcome email
        await send_welcome_email(
        to_email=payload.email,
        name=payload.name,
        username=payload.email,
        password=payload.password
    )

        return employee

    
    @staticmethod
    async def get_all_employees(db, admin_user: dict):
        org_id = admin_user.get("organization_id")
        return await EmployeeRepository.get_all(db, org_id)

    @staticmethod
    async def update_employee(db, employee_id, payload):
        employee = await EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise ValueError("Employee not found")

        update_data = payload.dict(exclude_unset=True)
        await EmployeeRepository.update_employee(db, employee_id, update_data)

    @staticmethod
    async def delete_employee(db, employee_id):
        employee = await EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise ValueError("Employee not found")

        await EmployeeRepository.soft_delete(db, employee_id)

