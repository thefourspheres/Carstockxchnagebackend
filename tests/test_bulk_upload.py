"""Bulk upload of the dealer stock sheet: preview, import only new rows, skip duplicates."""
import io

import openpyxl

from tests.test_cars import ADMIN, CAR, SALES, client  # noqa: F401  (fixture)

HEAD = ["NO", "MAKE", "MODEL", "VERIANT", "FUEL", None, "REG NUMBER", "YEAR", "COLOUR", "OWNER", "INSURANCE", "KM", "PRICE"]


def sheet(*rows) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in rows:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


STOCK = sheet(
    ["STOCK"], ["SUV"], HEAD,
    [1, "KIA", "SELTOS", "HTX", "PETROL", "AUTO", "MH12TD7995", 2021, "WHITE", 1, "EXPIRED", 81000, "12,25,000"],
    [2, "TATA", "SAFARI", "DK", "DISEL", "AUTO", "UNRG", 2025, "BLACK", "-", "-", 3387, 3056680],
    ["SEDAN"],
    [3, "HONDA", "CITY", "V", "PETROL", "MANUAL", "MH 14 FG 9447", 2016, "WHITE", 2, "EXPIRED", 131000, 575000],
    [4, "HONDA", "CITY", "V", "KEROSENE", "MANUAL", "MH14FG0001", 2016, "WHITE", 2, "EXPIRED", 1000, 575000],
    ["BOOKING"], HEAD,
    [5, "TOYOTA", "FORTUNER", "SIGMA 4X4", "DIESEL", "AUTO", "MH12UU0111", 2022, "WHITE", 1, "x", 222615, 4250000],
)


def post(client, data=STOCK, dry_run=True, headers=ADMIN):  # noqa: F811
    return client.post("/cars/bulk-upload", headers=headers, data={"dry_run": str(dry_run).lower()},
                       files={"file": ("stock.xlsx", data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})


async def test_preview_import_and_skip_duplicates(client):  # noqa: F811
    # One car already exists (same registration, typed differently).
    r = await client.post("/cars/create", json=CAR | {"registration_number": "mh-12-td-7995"}, headers=ADMIN)
    assert r.status_code == 201, r.text

    prev = (await post(client)).json()
    assert prev["summary"] == {"total": 5, "new": 3, "duplicate": 1, "error": 1}, prev
    assert prev["added"] == 0 and (await client.post("/cars/list", headers=ADMIN)).json()["total"] == 1
    err = next(x for x in prev["rows"] if x["status"] == "error")
    assert err["row"] == 8 and "KEROSENE" in err["reason"]

    done = (await post(client, dry_run=False)).json()
    assert done["added"] == 3
    cars = {c["registration_number"]: c for c in (await client.post("/cars/list", headers=ADMIN)).json()["cars"]}
    city = cars["MH14FG9447"]
    assert (city["brand"], city["name"], city["car_type"], city["owner"], float(city["actual_price"])) == \
        ("Honda", "City V", "Sedan", 2, 575000)
    assert cars["MH12UU0111"]["status"] == "Reserved" and cars["MH12UU0111"]["car_type"] == "SUV"
    assert cars[None]["name"] == "Safari DK" and cars[None]["owner"] is None

    again = (await post(client, dry_run=False)).json()
    assert again["added"] == 0 and again["summary"]["duplicate"] == 4


async def test_guards(client):  # noqa: F811
    assert (await post(client, headers=SALES)).status_code == 403
    assert (await post(client, data=b"not excel")).status_code == 400
    assert (await post(client, data=sheet(["hello"]))).status_code == 400


async def test_registration_is_unique(client):  # noqa: F811
    assert (await client.post("/cars/create", json=CAR | {"registration_number": "MH12AB1234"}, headers=ADMIN)).status_code == 201
    r = await client.post("/cars/create", json=CAR | {"registration_number": "mh12 ab 1234"}, headers=ADMIN)
    assert r.status_code == 409
    assert (await client.post("/cars/create", json=CAR | {"registration_number": "AB"}, headers=ADMIN)).status_code == 422
