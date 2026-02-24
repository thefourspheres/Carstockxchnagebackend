import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ SINGLE ENGINE (ONLY HERE)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,)

# ✅ SINGLE SESSION FACTORY
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()


async def check_db_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        current_database() AS db,
                        current_user AS user,
                        current_schema() AS schema,
                        current_setting('search_path') AS search_path
                """)
            )
            row = result.fetchone()

            logger.info("✅ Database connected successfully")
            logger.info(
                f"DB INFO → database={row.db}, user={row.user}, "
                f"schema={row.schema}, search_path={row.search_path}"
            )

    except Exception as e:
        logger.error("❌ Database connection failed")
        logger.error(e)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
