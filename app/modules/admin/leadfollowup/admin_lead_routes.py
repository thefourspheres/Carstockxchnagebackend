from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.permissions import LEADS, require_roles
from app.modules.admin.leadfollowup.admin_lead_schema import FollowUpCreateRequest, FollowUpResponse, LeadFollowupFilter
from app.modules.admin.leadfollowup.lead_followup_model import LeadFollowUp
# from app.modules.admin.leadfollowup.admin_lead_service import admin_lead_service, AdminLeadService, add_followup, get_followups, get_leads_by_type 
from app.modules.admin.leadfollowup.admin_lead_service import AdminLeadService

router = APIRouter(
    prefix="/admin/leads",
    tags=["Admin Leads"]
)

@router.post("/followup", response_model=FollowUpResponse)
async def add_followup(
    payload: FollowUpCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(*LEADS))
):

    return await AdminLeadService.add_followup(
        db,
        payload.lead_id,
        payload
    )
@router.post("/followups", response_model=list[FollowUpResponse])
async def get_followups(
    payload: LeadFollowupFilter,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles(*LEADS))
):

    return await AdminLeadService.get_followups(
        db,
        payload.lead_id
    )

