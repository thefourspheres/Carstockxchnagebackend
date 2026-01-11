from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .auth_schema import LoginRequest
from .auth_service import AuthService

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])

@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login(db, payload.email, payload.password,payload.orgid)
