from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.admin.leadfollowup.lead_followup_model import LeadFollowUp
from uuid import UUID


class AdminLeadService:

    # other existing methods...

    @staticmethod
    async def add_followup(
        db: AsyncSession,
        lead_id: UUID,
        payload
    ):
        followup = LeadFollowUp(
            lead_id=lead_id,
            note=payload.note,
            next_followup_date=payload.next_followup_date
        )

        db.add(followup)
        await db.commit()
        await db.refresh(followup)

        return followup
    @staticmethod
    async def get_followups(
        db: AsyncSession,
        lead_id: UUID
    ):
        result = await db.execute(
            select(LeadFollowUp)
            .where(LeadFollowUp.lead_id == lead_id)
            .order_by(LeadFollowUp.created_at.desc())
        )

        return result.scalars().all()

