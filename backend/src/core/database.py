import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from backend.src.core.config import settings

logger = logging.getLogger(__name__)

# Convert sqlite or postgres if needed for testing flexibility
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initializes schema and TimescaleDB extension/hypertables if supported."""
    try:
        async with engine.begin() as conn:
            # Check for TimescaleDB extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            except Exception as e:
                logger.warning(f"TimescaleDB extension creation skipped: {e}")
            
            # Create standard tables
            await conn.run_sync(Base.metadata.create_all)
            
            # Setup Timescale hypertable for price_history if available
            try:
                await conn.execute(text(
                    "SELECT create_hypertable('price_history', 'time', if_not_exists => TRUE, migrate_data => TRUE);"
                ))
            except Exception as e:
                logger.warning(f"Hypertable creation skipped (standard table will be used): {e}")
                
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
