from unittest import result
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.modules.admin.leads.lead_model import CustomerLead, carsaleslead
from app.modules.admin.leads.admin_lead_schema import LeadFilterRequest


class AdminLeadService:

    @staticmethod
    async def list_leads(db: AsyncSession, filters: LeadFilterRequest):
        query = select(CustomerLead)

        if filters.lead_type:
            query = query.where(CustomerLead.lead_type == filters.lead_type)

        if filters.status:
            query = query.where(CustomerLead.status == filters.status)

        if filters.assigned_department:
            query = query.where(
                CustomerLead.assigned_department == filters.assigned_department
            )

        result = await db.execute(
            query.order_by(CustomerLead.created_at.desc())
        )

        return result.scalars().all()
    @staticmethod
    async def update_lead(
        db: AsyncSession,
        lead_id: UUID,
        payload
    ):
        result = await db.execute(
            select(CustomerLead).where(CustomerLead.id == lead_id)
        )

        lead = result.scalar_one_or_none()

        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        update_data = payload.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(lead, key, value)

        await db.commit()
        await db.refresh(lead)

        return lead
    
    @staticmethod
    async def get_leads_by_type(
    db: AsyncSession,
    lead_type: str,
    organization_id
):
        result = await db.execute(
        select(CustomerLead)
        .where(
            CustomerLead.lead_type == lead_type,
            CustomerLead.organization_id == organization_id
        )
        .order_by(CustomerLead.created_at.desc())
    )

        return result.scalars().all()

    @staticmethod
    async def get_car_sales_leads(db: AsyncSession):
        result = await db.execute(select(carsaleslead))
        return {
        "success": True,
        "total_leads": result.rowcount,
        "leads": result.scalars().all()
    }