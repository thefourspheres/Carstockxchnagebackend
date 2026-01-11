from fastapi import HTTPException
from .employee_model import Employee
from .employee_repository import EmployeeRepository
from app.utils.hashing import hash_password

class EmployeeService:

    @staticmethod
    async def signup(db, payload,admin_user: dict):
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
