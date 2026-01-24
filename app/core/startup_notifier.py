# app/core/startup_health_check.py

from app.core.database import engine
from sqlalchemy import text
from datetime import datetime
import traceback

LOG_FILE = "startup_health.log"

async def startup_health_check():
    log_lines = []
    log_lines.append(f"[{datetime.utcnow()}] 🚀 Application startup initiated")

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        log_lines.append("✅ Database connection successful")

    except Exception as e:
        log_lines.append("❌ Startup failure detected")
        log_lines.append(str(e))
        log_lines.append(traceback.format_exc())

    finally:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
