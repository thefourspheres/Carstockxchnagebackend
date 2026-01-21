import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def check_db_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error("❌ Database connection failed")
        logger.error(e)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
