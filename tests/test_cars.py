"""Car API tests. Needs a throwaway Postgres in DATABASE_URL (tables are dropped)."""
import importlib
import pathlib
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

for f in sorted(pathlib.Path("app/modules").rglob("*_model.py")):
    importlib.import_module(".".join(f.with_suffix("").parts))

from app.core.database import Base, engine  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.main import app  # noqa: E402

ORG_A, ORG_B = str(uuid.uuid4()), str(uuid.uuid4())
CAR = {
    "name": "City ZX", "brand": "Honda", "car_type": "Sedan", "condition": "Used",
    "year": 2021, "fuel_type": "Petrol", "transmission": "Manual", "color": "White",
    "owner": 1, "kilometer": 42000,
    "description": "Single owner", "actual_price": 850000, "discounted_price": 799000,
    "status": "Available",
}


def auth(*roles, org=ORG_A):
    token = create_access_token({"sub": str(uuid.uuid4()), "roles": list(roles), "organization_id": org})
    return {"Authorization": f"Bearer {token}"}


ADMIN, PURCHASE, SALES, HR = auth("ORGANIZATION_ADMIN"), auth("PURCHASE"), auth("SALES"), auth("HR")
OTHER_ORG = auth("ORGANIZATION_ADMIN", org=ORG_B)


@pytest.fixture
async def client():
    async with engine.begin() as c:
        await c.run_sync(Base.metadata.drop_all)
        await c.run_sync(Base.metadata.create_all)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        yield c
    await engine.dispose()


async def create(client, headers=ADMIN, **over):
    return await client.post("/cars/create", json=CAR | over, headers=headers)


async def test_create_list_get(client):
    r = await create(client)
    assert r.status_code == 201, r.text
    car_id = r.json()["car_id"]
    cars = (await client.post("/cars/list", headers=SALES)).json()["cars"]
    assert [c["id"] for c in cars] == [car_id]
    got = (await client.post("/cars/get-car-by-id", json={"car_id": car_id}, headers=PURCHASE)).json()["data"]
    assert got["condition"] == "Used" and float(got["discounted_price"]) == 799000


@pytest.mark.parametrize("bad", [
    {"discounted_price": 850000},          # not below actual
    {"actual_price": 0},
    {"car_type": "Truck"},
    {"fuel_type": "petrol"},               # exact enum values only
    {"year": 1970},
    {"name": " "},
    {"kilometer": -1},
    {"owner": 0},
    {"owner": 11},
    {"mileage": 10000},                    # unknown field is rejected
    {"description": "x" * 2001},
])
async def test_validation(client, bad):
    r = await create(client, **bad)
    assert r.status_code == 422, (bad, r.text)


async def test_optional_fields_and_whitespace(client):
    body = {k: v for k, v in CAR.items() if k not in ("color", "description", "discounted_price", "status")}
    r = await client.post("/cars/create", json=body | {"name": "  City   ZX "}, headers=ADMIN)
    assert r.status_code == 201
    got = (await client.post("/cars/get-car-by-id", json={"car_id": r.json()["car_id"]}, headers=ADMIN)).json()["data"]
    assert got["name"] == "City ZX" and got["status"] == "Available"


async def test_roles(client):
    assert (await create(client, headers=SALES)).status_code == 403
    assert (await create(client, headers=PURCHASE)).status_code == 201
    assert (await client.post("/cars/list", headers=HR)).status_code == 403
    assert (await client.get("/cars/options", headers=SALES)).json()["status"][0] == "Available"
    assert (await client.get("/admin/leads/callback", headers=ADMIN)).status_code == 200
    assert (await client.get("/admin/leads/callback", headers=PURCHASE)).status_code == 403


async def test_org_isolation(client):
    car_id = (await create(client)).json()["car_id"]
    assert (await client.post("/cars/get-car-by-id", json={"car_id": car_id}, headers=OTHER_ORG)).status_code == 404
    r = await client.put("/cars/update", json={"car_id": car_id, "name": "Hacked"}, headers=OTHER_ORG)
    assert r.status_code == 404
    assert (await client.post("/cars/list", headers=OTHER_ORG)).json()["total"] == 0


async def test_update_rules(client):
    car_id = (await create(client)).json()["car_id"]
    ok = await client.put("/cars/update", json={"car_id": car_id, "status": "Sold"}, headers=PURCHASE)
    assert ok.status_code == 200
    r = await client.put("/cars/update", json={"car_id": car_id, "discounted_price": 900000}, headers=ADMIN)
    assert r.status_code == 422
    r = await client.put("/cars/update", json={"car_id": car_id, "name": None}, headers=ADMIN)
    assert r.status_code == 422
    r = await client.put("/cars/update", json={"car_id": car_id, "discounted_price": None}, headers=ADMIN)
    assert r.status_code == 200


async def test_list_filter_and_delete(client):
    a = (await create(client)).json()["car_id"]
    await create(client, name="Creta", brand="Hyundai", status="Draft")
    assert (await client.post("/cars/list", json={"status": "Draft"}, headers=ADMIN)).json()["total"] == 1
    assert (await client.post("/cars/list", json={"search": "hyun"}, headers=ADMIN)).json()["total"] == 1
    assert (await client.post("/cars/delete", json={"car_id": a}, headers=SALES)).status_code == 403
    assert (await client.post("/cars/delete", json={"car_id": a}, headers=ADMIN)).status_code == 200
    assert (await client.post("/cars/list", headers=ADMIN)).json()["total"] == 1


async def test_public_hides_drafts_and_internal_fields(client):
    await create(client, name="Live Car")
    await create(client, name="Hidden Draft", status="Draft")
    await create(client, name="Gone", status="Sold")
    cars = (await client.get("/public/cars/all")).json()
    assert [c["name"] for c in cars] == ["Live Car"]
    assert cars[0]["price"] == 799000 and "organization_id" not in cars[0] and "created_by" not in cars[0]
    assert len((await client.get("/public/cars/homepage")).json()) == 1


async def test_upload_rejects_bad_type_and_traversal(client):
    car_id = (await create(client)).json()["car_id"]
    files = {"files": ("a.webp", b"RIFF0000WEBP", "image/webp")}
    r = await client.post("/cars/upload-images", data={"car_id": car_id, "image_type": "../../etc"},
                          files=files, headers=ADMIN)
    assert r.status_code == 400
    r = await client.post("/cars/upload-images", data={"car_id": car_id, "image_type": "banner"},
                          files={"files": ("a.php", b"<?php", "application/x-php")}, headers=ADMIN)
    assert r.status_code == 400


async def test_role_assign_is_org_scoped_and_no_escalation(client):
    from app.core.database import AsyncSessionLocal
    from app.modules.admin.employee.employee_model import Employee
    from app.modules.admin.organization.organization_model import Organization
    from app.modules.admin.role.role_model import Role
    async with AsyncSessionLocal() as db:
        db.add_all([Organization(id=uuid.UUID(ORG_A), name="A"), Organization(id=uuid.UUID(ORG_B), name="B")])
        await db.flush()
        mine = Employee(name="m", email="m@a.in", organization_id=uuid.UUID(ORG_A))
        theirs = Employee(name="t", email="t@b.in", organization_id=uuid.UUID(ORG_B))
        sales, sup = Role(name="SALES"), Role(name="SUPER_ADMIN")
        db.add_all([mine, theirs, sales, sup])
        await db.commit()
        ids = dict(mine=str(mine.id), theirs=str(theirs.id), sales=sales.id, sup=sup.id)
    post = lambda e, r, h=ADMIN: client.post("/admin/roles/assign", json={"employee_id": ids[e], "role_id": ids[r]}, headers=h)
    assert (await post("theirs", "sales")).status_code == 404
    assert (await post("mine", "sup")).status_code == 403
    assert (await post("mine", "sales", HR)).status_code == 403
    assert (await post("mine", "sales")).status_code == 200


async def test_public_leads_reach_admin(client):
    from app.core.config import settings
    admin = auth("ORGANIZATION_ADMIN", org=str(settings.ORG_ID))
    r = await client.post("/public/leads/callback", json={"name": "Ravi", "mobile": "+91 98765 43210"})
    assert r.status_code == 200, r.text
    r = await client.post("/public/leads/test-drive", json={"name": "Ravi", "mobile": "9876543210",
                                                             "car_brand": "Honda", "car_model": "City"})
    assert r.status_code == 200, r.text
    calls = (await client.get("/admin/leads/callback", headers=admin)).json()
    assert [c["mobile"] for c in calls] == ["9876543210"]
    assert len((await client.get("/admin/leads/testdrive", headers=admin)).json()) == 1
    for bad in ["12345", "5876543210", "98765432101"]:
        r = await client.post("/public/leads/callback", json={"name": "Ravi", "mobile": bad})
        assert r.status_code == 422, bad


async def test_sold_purges_images_and_hides_car(client, tmp_path, monkeypatch):
    from sqlalchemy import func, select
    from app.core.config import settings
    from app.core.database import AsyncSessionLocal
    from app.modules.admin.cars.car_image_model import CarImage
    monkeypatch.setattr(settings, "LOCAL_STORAGE_PATH", str(tmp_path))

    car_id = (await create(client)).json()["car_id"]
    got = (await client.post("/cars/get-car-by-id", json={"car_id": car_id}, headers=ADMIN)).json()["data"]
    assert (got["owner"], got["kilometer"]) == (1, 42000)
    up = lambda: client.post("/cars/upload-images", data={"car_id": car_id, "image_type": "banner"},
                             files={"files": ("a.webp", b"RIFF0000WEBP", "image/webp")}, headers=ADMIN)
    imgs = [(await up()).json()["images"][0] for _ in range(2)]
    await client.post("/cars/delete-image", json={"image_id": imgs[0]["id"]}, headers=ADMIN)  # soft-deleted one
    files = list(tmp_path.rglob("*.webp"))
    assert len(files) == 2

    r = await client.put("/cars/update", json={"car_id": car_id, "status": "Sold"}, headers=PURCHASE)
    assert r.status_code == 200, r.text
    async with AsyncSessionLocal() as db:
        assert await db.scalar(select(func.count()).select_from(CarImage)) == 0
    assert not any(f.exists() for f in files) and tmp_path.exists()
    assert (await client.post("/cars/list", headers=ADMIN)).json()["total"] == 0
    assert (await client.post("/cars/list", json={"status": "Sold"}, headers=ADMIN)).json()["total"] == 1
    assert (await client.get("/public/cars/all")).json() == []
    assert (await up()).status_code == 409
