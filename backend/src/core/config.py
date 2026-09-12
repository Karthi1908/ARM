import os
import json
from typing import List, Union, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agentic Crypto Risk Manager API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://agentic-risk-frontend-718889497518.us-central1.run.app",
        "https://agentic-risk-frontend-n7lmyqxwca-uc.a.run.app",
        "*"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # Database (PostgreSQL + TimescaleDB)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/risk_manager")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # External API Keys & Endpoints
    PRIVY_APP_ID: str = os.getenv("PRIVY_APP_ID", "mock-privy-app-id")
    PRIVY_APP_SECRET: str = os.getenv("PRIVY_APP_SECRET", "mock-privy-secret")
    THE_GRAPH_API_KEY: str = os.getenv("THE_GRAPH_API_KEY", "")
    ONEINCH_API_KEY: str = os.getenv("ONEINCH_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    
    # Discovery Indexer Feature Toggles
    ENABLE_THE_GRAPH: bool = os.getenv("ENABLE_THE_GRAPH", "true").lower() in ("true", "1", "yes")
    ENABLE_RPC_DISCOVERY: bool = os.getenv("ENABLE_RPC_DISCOVERY", "true").lower() in ("true", "1", "yes")
    ENABLE_BLOCKSCOUT_DISCOVERY: bool = os.getenv("ENABLE_BLOCKSCOUT_DISCOVERY", "true").lower() in ("true", "1", "yes")
    
    # Quantitative Risk Baseline Defaults
    REFERENCE_BENCHMARK: str = "BTC"
    RISK_FREE_RATE: float = 0.00
    DEFAULT_LOOKBACK_DAYS: int = 90
    MIN_OBSERVATIONS_THRESHOLD: int = 20
    MATH_ENGINE_VERSION: str = "v1.1.0"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()

def validate_and_log_config(logger=None):
    """Logs runtime configuration status safely without leaking secrets."""
    import logging
    log = logger or logging.getLogger("crypto_risk_manager.config")
    
    privy_status = "configured" if settings.PRIVY_APP_ID and settings.PRIVY_APP_ID != "mock-privy-app-id" else "mock"
    graph_status = "configured" if bool(settings.THE_GRAPH_API_KEY) else "mock/fallback"
    coingecko_status = "configured" if bool(settings.COINGECKO_API_KEY) else "public-tier"
    db_type = "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite"
    redis_status = "configured" if bool(settings.REDIS_URL) else "in-memory-fallback"
    
    log.info(
        f"Config status: Auth={privy_status}, DB={db_type}, "
        f"MarketFeeds={coingecko_status}, Indexer={graph_status}, Cache={redis_status}"
    )
