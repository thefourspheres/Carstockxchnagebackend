from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    employee_id = Column(UUID, ForeignKey("employees.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
