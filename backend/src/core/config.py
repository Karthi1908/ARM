import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agentic Crypto Risk Manager API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
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
    
    # Discovery Indexer Feature Toggles
    ENABLE_THE_GRAPH: bool = os.getenv("ENABLE_THE_GRAPH", "true").lower() in ("true", "1", "yes")
    ENABLE_RPC_DISCOVERY: bool = os.getenv("ENABLE_RPC_DISCOVERY", "true").lower() in ("true", "1", "yes")
    ENABLE_BLOCKSCOUT_DISCOVERY: bool = os.getenv("ENABLE_BLOCKSCOUT_DISCOVERY", "true").lower() in ("true", "1", "yes")
    
    # Quantitative Risk Baseline Defaults
    REFERENCE_BENCHMARK: str = "BTC"
    RISK_FREE_RATE: float = 0.00
    DEFAULT_LOOKBACK_DAYS: int = 90
    MIN_OBSERVATIONS_THRESHOLD: int = 20

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
