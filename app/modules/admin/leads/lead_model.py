from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from sqlalchemy.orm import relationship


class CustomerLead(Base):
    __tablename__ = "customer_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    lead_type = Column(String(50), nullable=False)
    organization_id = Column(UUID(as_uuid=True), nullable=False)  # Added organization_id field
    name = Column(String(150), nullable=False)
    mobile = Column(String(15), nullable=False)
    email = Column(String(150))

    description = Column(Text)

    car_brand = Column(String(100))
    car_model = Column(String(100))
    car_id = Column(UUID(as_uuid=True))

    whatsapp_opt_in = Column(Boolean, default=True)

    status = Column(String(50), default="NEW")
    assigned_department = Column(String(50))

    created_at = Column(TIMESTAMP, server_default=func.now())

    followups = relationship(
    "LeadFollowUp",
    back_populates="lead",
    cascade="all, delete"
    )

class carsaleslead(Base):
    __tablename__ = "carsales_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ownername = Column(String(150), nullable=False)
    carregisteryear = Column(Integer, nullable=False)
    mobile = Column(String(15), nullable=False)
    email = Column(String(150))
    car_model = Column(String(100))
    expected_price = Column(Integer, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
