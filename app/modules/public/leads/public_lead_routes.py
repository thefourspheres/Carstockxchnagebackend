from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.admin.leads.lead_model import CustomerLead
from .public_lead_schema import (
    CallbackRequest,
    TestDriveRequest,
    CarReportRequest
)

router = APIRouter(
    prefix="/public/leads",
    tags=["Public Leads"]
)


@router.post("/callback")
async def request_callback(payload: CallbackRequest, db: AsyncSession = Depends(get_db)):
    lead = CustomerLead(
        lead_type="CALLBACK",
        name=payload.name,
        mobile=payload.mobile,
        description=payload.description,
        whatsapp_opt_in=payload.whatsapp_opt_in,
        assigned_department="SALES"
    )
    db.add(lead)
    await db.commit()

    return {"message": "Callback request submitted successfully"}


@router.post("/test-drive")
async def request_test_drive(payload: TestDriveRequest, db: AsyncSession = Depends(get_db)):
    lead = CustomerLead(
        lead_type="TEST_DRIVE",
        name=payload.name,
        mobile=payload.mobile,
        car_brand=payload.car_brand,
        car_model=payload.car_model,
        whatsapp_opt_in=payload.whatsapp_opt_in,
        assigned_department="SALES"
    )
    db.add(lead)
    await db.commit()

    return {"message": "Test drive request submitted successfully"}


@router.post("/car-report")
async def request_car_report(payload: CarReportRequest, db: AsyncSession = Depends(get_db)):
    lead = CustomerLead(
        lead_type="CAR_REPORT",
        name=payload.name,
        mobile=payload.mobile,
        email=payload.email,
        car_id=payload.car_id,
        whatsapp_opt_in=payload.whatsapp_opt_in,
        assigned_department="PURCHASE"
    )
    db.add(lead)
    await db.commit()

    return {"message": "Car report request submitted successfully"}
