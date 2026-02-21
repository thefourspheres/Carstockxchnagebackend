from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.permissions import require_admin, require_roles

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
    admin=Depends(require_admin())   # 👈 ADMIN TOKEN
):
    try:
        await EmployeeService.signup(db, payload,admin)
        return {"message": "Employee registered"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    admin=Depends(require_admin()),
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
            "is_active": emp.is_active
        })

    return response
