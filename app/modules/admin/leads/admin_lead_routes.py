from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.permissions import LEADS, require_roles
from app.modules.admin.leads.admin_lead_schema import (
    CarSalesLeadResponse,
    LeadFilterRequest,
    LeadResponse
)
from app.modules.admin.leads.admin_lead_service import AdminLeadService
from app.modules.admin.leads.lead_model import carsaleslead

router = APIRouter(
    prefix="/admin/leads",
    tags=["Admin Leads"]
)


@router.post("/list", response_model=list[LeadResponse])
async def list_leads(
    payload: LeadFilterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(*LEADS))
):

    return await AdminLeadService.list_leads(db, payload)



@router.get("/callback", response_model=list[LeadResponse])
async def get_callback_leads(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(*LEADS))
):

    organization_id = current_user.get("organization_id")

    return await AdminLeadService.get_leads_by_type(
        db,
        "CALLBACK",
        organization_id
    )

@router.get("/testdrive", response_model=list[LeadResponse])
async def get_testdrive_leads(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(*LEADS))
):

    organization_id = current_user.get("organization_id")

    return await AdminLeadService.get_leads_by_type(
        db,
        "TEST_DRIVE",
        organization_id
    )


@router.get("/carsale", response_model=list[CarSalesLeadResponse])
async def get_carsale_leads(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(*LEADS))
):

    result = await db.execute(select(carsaleslead))
    leads = result.scalars().all()

    return leads
