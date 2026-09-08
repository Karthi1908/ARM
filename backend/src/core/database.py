import socket
import logging
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from backend.src.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def is_port_reachable(host: str, port: int, timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

# Determine database URL with automatic SQLite fallback if PostgreSQL is unreachable
raw_url = settings.DATABASE_URL
if raw_url.startswith("postgresql://"):
    raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

active_db_url = raw_url
if "postgresql" in raw_url:
    parsed = urlparse(raw_url.replace("postgresql+asyncpg://", "http://"))
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    if host in ["localhost", "127.0.0.1", "::1"] and not is_port_reachable(host, port):
        logger.info(
            f"PostgreSQL port {port} is unreachable on {host}. "
            f"Using local SQLite database (sqlite+aiosqlite:///./risk_manager.db)."
        )
        active_db_url = "sqlite+aiosqlite:///./risk_manager.db"

def get_engine_args(url: str):
    if "sqlite" in url:
        return {"echo": False}
    return {
        "echo": False,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }

engine = create_async_engine(active_db_url, **get_engine_args(active_db_url))

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
    """Initializes schema and TimescaleDB extension/hypertables if supported."""
    try:
        async with engine.begin() as conn:
            if "postgresql" in str(engine.url):
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
                except Exception as e:
                    logger.warning(f"TimescaleDB extension creation skipped: {e}")

            await conn.run_sync(Base.metadata.create_all)

            if "postgresql" in str(engine.url):
                try:
                    await conn.execute(text(
                        "SELECT create_hypertable('price_history', 'time', if_not_exists => TRUE, migrate_data => TRUE);"
                    ))
                except Exception as e:
                    logger.warning(f"Hypertable creation skipped: {e}")

        logger.info(f"Database initialized successfully ({'PostgreSQL' if 'postgresql' in str(engine.url) else 'SQLite'}).")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
