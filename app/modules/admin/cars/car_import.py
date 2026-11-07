"""Bulk import of the dealer's stock sheet (.xlsx).

Expected layout (as in "STOCK LIST" Google Sheet export):
  section rows (SUV / SEDAN / HATCHBACK / BOOKING / REFURB) followed by a header row
  NO | MAKE | MODEL | VARIANT | FUEL | <transmission> | REG NUMBER | YEAR | COLOUR | OWNER | INSURANCE | KM | PRICE
Rows whose registration number (or, if unregistered, brand+name+year+colour+km) already exists are skipped.
"""
import io
import re
import zipfile
from decimal import Decimal, InvalidOperation
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .car_model import Car
from .car_schema import CarCreateSchema

MAX_BYTES = 2 * 1024 * 1024
MAX_ROWS = 2000

SECTION_TYPE = {"SUV": "SUV", "SUVS": "SUV", "SEDAN": "Sedan", "SEDANS": "Sedan", "HATCHBACK": "Hatchback",
                "HATCHBACKS": "Hatchback", "MUV": "MUV", "MPV": "MUV", "PICKUP": "Pickup", "VAN": "Van"}
SECTION_STATUS = {"BOOKING": "Reserved", "BOOKED": "Reserved", "REFURB": "Draft", "REFURBISH": "Draft"}
BRANDS = {"MARUTI": "Maruti Suzuki", "MARUTI SUZUKI": "Maruti Suzuki", "MERCEDEZ": "Mercedes-Benz",
          "MERCEDES": "Mercedes-Benz", "MERCEDES-BENZ": "Mercedes-Benz", "MERCEDES BENZ": "Mercedes-Benz",
          "VW": "Volkswagen", "VOLKSWAGEN": "Volkswagen", "MG": "MG", "BMW": "BMW", "KIA": "Kia"}
FUELS = {"PETROL": "Petrol", "PRTROL": "Petrol", "PETRO": "Petrol", "PTR": "Petrol", "DIESEL": "Diesel",
         "DISEL": "Diesel", "DSL": "Diesel", "CNG": "CNG", "PTR+CNG": "CNG", "PETROL+CNG": "CNG",
         "EV": "Electric", "ELECTRIC": "Electric", "HYBRID": "Hybrid"}
GEARS = {"AUTO": "Automatic", "AUTOMATIC": "Automatic", "AT": "Automatic", "MANUAL": "Manual",
         "MANNUAL": "Manual", "MT": "Manual", "AMT": "AMT", "CVT": "CVT", "DCT": "DCT"}
# Fallback body type by the first word of the model, for rows outside a type section (e.g. BOOKING).
KNOWN_TYPES = {
    **dict.fromkeys(["SWIFT", "BALENO", "ALTO", "WAGONR", "WAGNOR", "CELERIO", "IGNIS", "I10", "I-10", "I20", "I-20",
                     "GRAND", "SANTRO", "TIAGO", "ALTROZ", "POLO", "JAZZ", "GLANZA", "KWID", "FABIA", "PUNCH"], "Hatchback"),
    **dict.fromkeys(["CITY", "AMAZE", "VERNA", "CIAZ", "DZIRE", "DESIRE", "RAPID", "SLAVIA", "VENTO", "VIRTUS",
                     "TIGOR", "AURA", "ELANTRA", "SUPERB", "OCTAVIA", "COROLLA", "CAMRY", "E-CLASS", "C-CLASS", "XF"], "Sedan"),
    **dict.fromkeys(["INNOVA", "ERTIGA", "XL6", "MOBILIO", "MOBILO", "CARENS", "MARAZZO", "TRIBER", "RUMION",
                     "CARNIVAL", "HEXA"], "MUV"),
    **dict.fromkeys(["FORTUNER", "CRETA", "SELTOS", "SONET", "VENUE", "NEXON", "BREZZA", "VITARA", "XUV300", "XUV500",
                     "XUV700", "XUV", "SCORPIO", "THAR", "HARRIER", "SAFARI", "COMPASS", "ENDEAVOUR", "ECOSPORT",
                     "ECOSPORTS", "KUSHAQ", "TAIGUN", "HECTOR", "ASTOR", "ZSEV", "KODIAQ", "KODIQ", "Q3", "Q5", "X1",
                     "X3", "X5", "GLA", "GLC", "GLE", "ML", "TUV", "BOLERO", "EXTER", "MAGNITE", "KIGER", "DUSTER"], "SUV"),
}

HEADERS = {"MAKE": "make", "BRAND": "make", "MODEL": "model", "VERIANT": "variant", "VARIANT": "variant",
           "FUEL": "fuel", "TRANSMISSION": "gear", "GEAR": "gear", "REG NUMBER": "reg", "REG NO": "reg",
           "REGISTRATION": "reg", "YEAR": "year", "COLOUR": "color", "COLOR": "color", "OWNER": "owner",
           "KM": "km", "KMS": "km", "PRICE": "price", "TYPE": "type"}


def _key(v) -> str:
    return " ".join(str(v).upper().split()) if v is not None else ""


def _word(w: str) -> str:
    # Keep codes like XUV500, HTX, EV upper-case; title-case plain words (SELTOS -> Seltos, E-CLASS -> E-Class).
    if len(w) > 3 and re.fullmatch(r"[A-Za-z-]+", w):
        return "-".join(p.capitalize() for p in w.split("-"))
    return w.upper()


def _title(v) -> str:
    return " ".join(_word(w) for w in str(v).split())


def _num(v) -> Optional[Decimal]:
    if v is None or str(v).strip() in ("", "-"):
        return None
    try:
        return Decimal(re.sub(r"[^\d.]", "", str(v)) or "x")
    except InvalidOperation:
        raise ValueError(f"'{v}' is not a number")


def _brand(make: str) -> str:
    return BRANDS.get(_key(make), _title(make))


def _model(brand: str, model) -> str:
    return "" if brand == "Mercedes-Benz" and _key(model) == "BENZ" else _title(model)


def parse_sheet(data: bytes) -> list[dict]:
    """Return raw rows: {"row", "section", "cells": {field: value}}. Raises 400 on unreadable files."""
    import openpyxl  # imported here so the API still starts if the optional dep is missing

    if len(data) > MAX_BYTES:
        raise HTTPException(400, "File is larger than 2 MB")
    try:
        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except (zipfile.BadZipFile, KeyError, ValueError, OSError):
        raise HTTPException(400, "Upload an .xlsx file (Excel / Google Sheets → Download → .xlsx)")

    out, cols, section = [], None, ""
    for i, row in enumerate(wb.worksheets[0].iter_rows(values_only=True), start=1):
        if i > MAX_ROWS:
            raise HTTPException(400, f"Sheet has more than {MAX_ROWS} rows")
        cells = list(row)
        filled = [c for c in cells if c not in (None, "")]
        if not filled:
            continue
        upper = [_key(c) for c in cells]
        if "MAKE" in upper or "BRAND" in upper:
            cols = {}
            for j, h in enumerate(upper):
                if h in HEADERS:
                    cols[HEADERS[h]] = j
            # Gear column has no header in the dealer sheet: it sits right after FUEL.
            if "gear" not in cols and "fuel" in cols:
                cols["gear"] = cols["fuel"] + 1
            continue
        if len(filled) == 1 and isinstance(filled[0], str):
            section = _key(filled[0])
            continue
        if cols is None:
            continue
        out.append({"row": i, "section": section,
                    "cells": {f: cells[j] if j < len(cells) else None for f, j in cols.items()}})
    wb.close()
    return out


def build_car(raw: dict, type_hint: dict) -> dict:
    """Map one sheet row to CarCreateSchema fields. Raises ValueError with a readable reason."""
    c, section = raw["cells"], raw["section"]
    if not c.get("make") or not c.get("model"):
        raise ValueError("MAKE and MODEL are required")
    brand = _brand(c["make"])
    name = " ".join(p for p in (_model(brand, c["model"]), _key(c.get("variant"))) if p)
    fuel = FUELS.get(_key(c.get("fuel")).replace(" ", ""))
    if not fuel:
        raise ValueError(f"Unknown fuel '{c.get('fuel')}'")
    gear = GEARS.get(_key(c.get("gear")))
    if not gear:
        raise ValueError(f"Unknown transmission '{c.get('gear')}'")
    model_key = _key(c["model"])
    car_type = (SECTION_TYPE.get(_key(c.get("type"))) or SECTION_TYPE.get(section)
                or type_hint.get((brand, model_key)) or type_hint.get((brand, model_key.split()[0]))
                or KNOWN_TYPES.get(model_key.split()[0].replace(" ", "")))
    if not car_type:
        raise ValueError("Car type unknown (not under SUV/SEDAN/HATCHBACK); add it manually")
    reg = _key(c.get("reg"))
    owner, km, price, year = _num(c.get("owner")), _num(c.get("km")), _num(c.get("price")), _num(c.get("year"))
    if price is None:
        raise ValueError("PRICE is required")
    if year is None:
        raise ValueError("YEAR is required")
    return {
        "name": name, "brand": brand, "car_type": car_type, "condition": "Used",
        "year": int(year), "fuel_type": fuel, "transmission": gear,
        "color": str(c["color"]).strip().title() if c.get("color") else None,
        "owner": int(owner) if owner else None, "kilometer": int(km) if km is not None else None,
        "registration_number": None if reg in ("", "-", "UNRG", "UNREG", "NEW") else reg,
        "actual_price": price, "status": SECTION_STATUS.get(section, "Available"),
    }


def _fingerprint(d: dict) -> tuple:
    if d.get("registration_number"):
        return ("reg", d["registration_number"])
    return ("car", d["brand"].lower(), d["name"].lower(), d["year"], (d.get("color") or "").lower(), d.get("kilometer"))


async def import_cars(db: AsyncSession, data: bytes, user: dict, dry_run: bool) -> dict:
    user_id, org_id = UUID(str(user["sub"])), UUID(str(user["organization_id"]))
    raws = parse_sheet(data)
    if not raws:
        raise HTTPException(400, "No car rows found. The sheet needs a header row with MAKE, MODEL, PRICE…")

    existing = (await db.execute(select(Car).where(Car.organization_id == org_id, Car.is_active.is_(True)))).scalars().all()
    seen = {_fingerprint({"registration_number": c.registration_number, "brand": c.brand, "name": c.name,
                          "year": c.year, "color": c.color, "kilometer": c.kilometer}) for c in existing}
    # Model -> type learned from rows under a type section (used for BOOKING/REFURB rows).
    type_hint = {(_brand(r["cells"].get("make") or ""), _key(r["cells"].get("model"))): SECTION_TYPE[r["section"]]
                 for r in raws if r["section"] in SECTION_TYPE}

    for c in existing:
        type_hint.setdefault((c.brand, _key(c.name).split(" ")[0]), c.car_type)

    rows, to_add = [], []
    for raw in raws:
        item = {"row": raw["row"], "section": raw["section"]}
        try:
            fields = build_car(raw, type_hint)
            car = CarCreateSchema(**fields)
        except ValidationError as e:
            err = e.errors()[0]
            where = ".".join(str(x) for x in err.get("loc", ()))
            rows.append(item | {"status": "error", "reason": f"{where}: {err['msg']}".strip(": ")})
            continue
        except ValueError as e:
            rows.append(item | {"status": "error", "reason": str(e)})
            continue
        item |= {"brand": car.brand, "name": car.name, "year": car.year, "registration_number": car.registration_number,
                 "kilometer": car.kilometer, "price": float(car.actual_price), "car_status": car.status}
        fp = _fingerprint(car.model_dump())
        if fp in seen:
            rows.append(item | {"status": "duplicate", "reason": "Already in stock"})
            continue
        seen.add(fp)
        rows.append(item | {"status": "new"})
        to_add.append(car)

    if not dry_run and to_add:
        db.add_all(Car(**c.model_dump(), created_by=user_id, organization_id=org_id) for c in to_add)
        await db.commit()
    count = lambda s: sum(r["status"] == s for r in rows)
    return {"dry_run": dry_run, "added": 0 if dry_run else len(to_add),
            "summary": {"total": len(rows), "new": count("new"), "duplicate": count("duplicate"), "error": count("error")},
            "rows": rows}
