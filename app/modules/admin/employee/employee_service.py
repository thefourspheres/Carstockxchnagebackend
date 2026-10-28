import logging
import secrets
import string
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from app.modules.admin.employee.email_service import send_welcome_email
from .employee_model import Employee
from .employee_repository import EmployeeRepository
from app.utils.hashing import hash_password

log = logging.getLogger(__name__)


def _temp_password(n: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "@$!%*?&"
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(n))
        if any(c.isupper() for c in pw) and any(c.isdigit() for c in pw) and any(c in "@$!%*?&" for c in pw):
            return pw


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

        # The employee is created even if the email fails; HR can resend from the list.
        if await EmployeeService._send_invite(employee, payload.password):
            employee.invite_sent_at = datetime.now(timezone.utc)
            await db.commit()
        return employee

    @staticmethod
    async def _send_invite(employee, password: str) -> bool:
        try:
            await send_welcome_email(to_email=employee.email, name=employee.name,
                                     username=employee.email, password=password)
            return True
        except Exception:
            log.exception("Welcome email to %s failed", employee.email)
            return False

    @staticmethod
    async def resend_invite(db, employee_id: UUID, admin_user: dict):
        employee = await EmployeeRepository.get_by_id(db, employee_id)
        if not employee or str(employee.organization_id) != str(admin_user.get("organization_id")):
            raise HTTPException(404, "Employee not found")
        # Only the hash is stored, so a resend issues a new temporary password.
        # Email first: if it fails the old password keeps working.
        temp = _temp_password()
        if not await EmployeeService._send_invite(employee, temp):
            raise HTTPException(502, "Email could not be sent. Check SMTP settings and try again.")
        employee.password_hash = hash_password(temp)
        employee.invite_sent_at = datetime.now(timezone.utc)
        await db.commit()
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

