from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.permissions import require_roles
from app.modules.admin.leads.lead_model import CustomerLead

router = APIRouter(
    prefix="/admin/leads",
    tags=["Admin Leads"]
)


@router.get("")
async def get_all_leads(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("ADMIN", "SUPER_ADMIN"))
):
    result = await db.execute(
        select(CustomerLead).order_by(CustomerLead.created_at.desc())
    )
    return result.scalars().all()
@router.patch("/{lead_id}")
async def update_lead_status(
    lead_id: str,
    status: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles("ADMIN", "SUPER_ADMIN"))
):
    result = await db.execute(
        select(CustomerLead).where(CustomerLead.id == lead_id)
    )
    lead = result.scalar_one()

    lead.status = status
    await db.commit()

    return {"message": "Lead updated"}
