from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from datetime import datetime
import traceback
import os

LOG_FILE = "startup_health.log"

async def startup_health_check():
    log_lines = []
    log_lines.append(f"[{datetime.utcnow()}] 🚀 Application startup initiated")

    try:
        if not settings.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not configured")

        engine = create_async_engine(settings.DATABASE_URL, echo=False)

        async with engine.connect() as conn:
            await conn.execute("SELECT 1")

        log_lines.append("✅ Database connection successful")

    except Exception as e:
        log_lines.append("❌ Startup failure detected")
        log_lines.append(str(e))
        log_lines.append(traceback.format_exc())

    finally:
        # ✅ UTF-8 FIX
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
