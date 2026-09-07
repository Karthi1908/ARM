import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from backend.src.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine_args(url: str):
    if "sqlite" in url:
        return {"echo": False}
    return {
        "echo": False,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }

# Initial engine setup
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, **get_engine_args(db_url))

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

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
    """Initializes schema and TimescaleDB extension/hypertables if supported, falling back to SQLite if PostgreSQL is unreachable."""
    global engine, AsyncSessionLocal
    is_postgres = "postgresql" in str(engine.url)

    if is_postgres:
        try:
            async with engine.begin() as conn:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
                except Exception as e:
                    logger.warning(f"TimescaleDB extension creation skipped: {e}")
                
                await conn.run_sync(Base.metadata.create_all)
                
                try:
                    await conn.execute(text(
                        "SELECT create_hypertable('price_history', 'time', if_not_exists => TRUE, migrate_data => TRUE);"
                    ))
                except Exception as e:
                    logger.warning(f"Hypertable creation skipped (standard table will be used): {e}")
            logger.info("PostgreSQL database initialized successfully.")
            return
        except Exception as e:
            logger.warning(
                f"PostgreSQL connection to {engine.url.host}:{engine.url.port} failed ({e}). "
                f"Falling back to local SQLite database (sqlite+aiosqlite:///./risk_manager.db)..."
            )
            sqlite_url = "sqlite+aiosqlite:///./risk_manager.db"
            engine = create_async_engine(sqlite_url, **get_engine_args(sqlite_url))
            AsyncSessionLocal = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

    # Initialize SQLite database
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Local SQLite database initialized successfully (tables ready).")
    except Exception as e:
        logger.error(f"Error during SQLite database initialization: {e}")
