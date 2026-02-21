from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class LeadFollowUp(Base):
    __tablename__ = "lead_followups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customer_leads.id"),
        nullable=False
    )

    note = Column(Text, nullable=False)

    next_followup_date = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    lead = relationship("CustomerLead", back_populates="followups")

