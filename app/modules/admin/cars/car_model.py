# app/modules/cars/car_model.py
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import json


class Car(Base):
    __tablename__ = "cars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # car_id = Column(UUID(as_uuid=True), ForeignKey("id"), nullable=False)    
    # Basic Information
    name = Column(String(100), nullable=True)
    brand = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    kilometer = Column(Integer, nullable=True)
    fuel_type = Column(String(20), nullable=False)
    transmission = Column(String(20), nullable=False)
    price = Column(Integer, nullable=True)
    




    # JSONB fields
    engine_specs = Column(JSONB, nullable=True)
    dimensions = Column(JSONB, nullable=True)
    capacity_fuel = Column(JSONB, nullable=True)
    suspension = Column(JSONB, nullable=True)
    tyres = Column(JSONB, nullable=True)
    features = Column(JSONB, nullable=True)
    
    # Additional fields
    color = Column(String(30), nullable=True)
    registration_number = Column(String(20), nullable=True)
    registration_year = Column(Integer, nullable=True)
    insurance_valid_until = Column(String(10), nullable=True)
    ownership = Column(String(10), nullable=True)
    rto = Column(String(50), nullable=True)
    
    # Status & Metadata - CHANGED TO UUID
    created_by = Column(UUID(as_uuid=True), nullable=False)  # Changed from String(100)
    organization_id = Column(UUID(as_uuid=True), nullable=False)  # Changed from String(100)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    images = relationship("CarImage", back_populates="car", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Car(id={self.id}, name={self.name}, brand={self.brand}, year={self.year})>"