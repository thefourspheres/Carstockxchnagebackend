from sqlalchemy import Column, String, Integer, SmallInteger, Boolean, Numeric, DateTime, Text, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class Car(Base):
    __tablename__ = "cars"
    __table_args__ = (
        Index("ix_cars_org_status", "organization_id", "status"),
        CheckConstraint("status IN ('Available','Reserved','Sold','Draft')", name="cars_status_chk"),
        CheckConstraint("actual_price > 0 AND (discounted_price IS NULL OR discounted_price < actual_price)",
                        name="cars_price_chk"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(100), nullable=False)
    brand = Column(String(50), nullable=False)
    car_type = Column(String(30), nullable=False)
    condition = Column(String(30), nullable=False)
    year = Column(Integer, nullable=False)
    fuel_type = Column(String(20), nullable=False)
    transmission = Column(String(20), nullable=False)
    color = Column(String(30), nullable=True)
    owner = Column(SmallInteger, nullable=True)  # 1 = first owner
    kilometer = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    actual_price = Column(Numeric(12, 2), nullable=False)
    discounted_price = Column(Numeric(12, 2), nullable=True)
    status = Column(String(20), nullable=False, default="Available")

    created_by = Column(UUID(as_uuid=True), nullable=False)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)  # soft delete

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    images = relationship("CarImage", back_populates="car", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Car(id={self.id}, name={self.name}, brand={self.brand}, year={self.year})>"
