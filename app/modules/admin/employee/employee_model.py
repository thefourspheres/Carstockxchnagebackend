from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100))
    email = Column(String(150), unique=True)
    mobile = Column(String(15))
    address = Column(String)
    blood_group = Column(String(5))
    date_of_birth = Column(Date)
    designation = Column(String(100))
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False
    )

    # ✅ MUST MATCH Organization.employees
    organization = relationship(
        "Organization",
        back_populates="employees"
    )

    