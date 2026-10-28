"""Employee invite: create survives email failure, resend issues a new password."""
import uuid

import pytest

from tests.test_cars import ADMIN, ORG_A, OTHER_ORG, SALES, client  # noqa: F401  (fixture)
from app.modules.admin.employee import employee_service as svc

EMP = {"name": "Asha", "email": "asha@x.in", "mobile": "9876543210", "designation": "Sales",
       "password": "Start@123", "is_active": True}


@pytest.fixture
async def org(client):  # noqa: F811
    from app.core.database import AsyncSessionLocal
    from app.modules.admin.organization.organization_model import Organization
    async with AsyncSessionLocal() as db:
        db.add(Organization(id=uuid.UUID(ORG_A), name="A"))
        await db.commit()
    return client


def mail(monkeypatch, ok=True):
    sent = []

    async def fake(**kw):
        if not ok:
            raise OSError("smtp down")
        sent.append(kw)
    monkeypatch.setattr(svc, "send_welcome_email", fake)
    return sent


async def emp_row(email="asha@x.in"):
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.modules.admin.employee.employee_model import Employee
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(Employee).where(Employee.email == email))).scalar_one()


async def test_signup_keeps_employee_when_email_fails(org, monkeypatch):
    mail(monkeypatch, ok=False)
    r = await org.post("/admin/employees/signup", json=EMP, headers=ADMIN)
    assert r.status_code == 200, r.text
    assert r.json()["email_sent"] is False
    lst = (await org.get("/admin/employees/employeelist", headers=ADMIN)).json()
    rows = lst if isinstance(lst, list) else lst.get("data", lst)
    assert [e["invite_sent_at"] for e in rows] == [None]


async def test_resend(org, monkeypatch):
    from app.utils.hashing import verify_password
    mail(monkeypatch, ok=False)
    emp_id = (await org.post("/admin/employees/signup", json=EMP, headers=ADMIN)).json()["id"]
    body = {"employee_id": emp_id}

    # Email still failing: 502 and the old password keeps working.
    assert (await org.post("/admin/employees/resend-invite", json=body, headers=ADMIN)).status_code == 502
    assert verify_password("Start@123", (await emp_row()).password_hash)

    assert (await org.post("/admin/employees/resend-invite", json=body, headers=SALES)).status_code == 403
    assert (await org.post("/admin/employees/resend-invite", json=body, headers=OTHER_ORG)).status_code == 404

    sent = mail(monkeypatch)
    r = await org.post("/admin/employees/resend-invite", json=body, headers=ADMIN)
    assert r.status_code == 200, r.text
    row = await emp_row()
    assert row.invite_sent_at is not None
    assert verify_password(sent[0]["password"], row.password_hash)
    assert not verify_password("Start@123", row.password_hash)
