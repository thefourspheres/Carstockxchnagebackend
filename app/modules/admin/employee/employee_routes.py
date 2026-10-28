from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.permissions import EMPLOYEES, require_roles

from .employee_schema import EmployeeSignupRequest
from .employee_service import EmployeeService
from .employee_model import Employee
from app.modules.admin.role.role_repository import RoleRepository


router = APIRouter(
    prefix="/admin/employees",
    tags=["Employees"]
)

# -------------------------
# Employee Signup
# -------------------------
@router.post("/signup")
async def signup(
    payload: EmployeeSignupRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_roles(*EMPLOYEES))   # 👈 ADMIN TOKEN
):
    try:
        emp = await EmployeeService.signup(db, payload, admin)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    sent = emp.invite_sent_at is not None
    return {"message": "Employee registered" if sent else "Employee registered, but the welcome email failed",
            "id": str(emp.id), "email_sent": sent}


class ResendInviteRequest(BaseModel):
    employee_id: UUID


@router.post("/resend-invite")
async def resend_invite(payload: ResendInviteRequest, db: AsyncSession = Depends(get_db),
                        admin=Depends(require_roles(*EMPLOYEES))):
    emp = await EmployeeService.resend_invite(db, payload.employee_id, admin)
    return {"message": f"New login details emailed to {emp.email}", "invite_sent_at": emp.invite_sent_at}


# -------------------------
# Employee List (ADMIN / HR)
# -------------------------
# @router.get("/list")
# async def list_employees(
#     user=Depends(require_roles(["ADMIN", "HR"])),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(Employee))
#     employees = result.scalars().all()

#     response = []
#     for emp in employees:
#         roles = await RoleRepository.get_roles(db, emp.id)
#         response.append({
#             "id": str(emp.id),
#             "name": emp.name,
#             "email": emp.email,
#             "designation": emp.designation,
#             "roles": roles,
#             "is_active": emp.is_active
#         })

#     return response

@router.get("/employeelist")
async def get_all_employees(
    admin=Depends(require_roles(*EMPLOYEES)),
    db: AsyncSession = Depends(get_db)
):
    EXCLUDED_ROLES = {"SUPER_ADMIN", "ORGANIZATION_ADMIN", "ADMIN"}

    result = await db.execute(
        select(Employee).where(
            Employee.organization_id == admin.get("organization_id"),
            Employee.is_active == True
        )
    )

    employees = result.scalars().all()

    response = []
    for emp in employees:
        roles = await RoleRepository.get_roles(db, emp.id)

        # 🔹 Remove restricted roles
        filtered_roles = [
            role for role in roles if role not in EXCLUDED_ROLES
        ]

        response.append({
            "id": str(emp.id),
            "name": emp.name,
            "email": emp.email,
            "mobile": emp.mobile,
            "designation": emp.designation,
            "roles": filtered_roles,
            "is_active": emp.is_active,
            "invite_sent_at": emp.invite_sent_at.isoformat() if emp.invite_sent_at else None,
        })

    return response
