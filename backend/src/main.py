import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.src.core.config import settings
from backend.src.core.database import init_db
from backend.src.core.redis_client import redis_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("crypto_risk_manager")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Crypto Risk Manager API...")
    from backend.src.core.config import validate_and_log_config
    validate_and_log_config(logger)
    await init_db()
    await redis_manager.connect()
    yield
    # Shutdown
    logger.info("Shutting down Crypto Risk Manager API...")
    await redis_manager.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred in the risk engine.", "error": str(exc)}
    )

@app.get("/health", tags=["Health"])
async def health_check():
    import os
    from backend.src.core.database import get_db_status
    db_info = get_db_status()
    cache_status = "available" if redis_manager.is_connected else "in-memory"
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "reference_benchmark": settings.REFERENCE_BENCHMARK,
        "risk_free_rate": settings.RISK_FREE_RATE,
        "database": db_info,
        "cache": {
            "status": cache_status,
            "engine": "redis" if redis_manager.is_connected else "in-memory"
        },
        "dependencies": {
            "the_graph": "configured" if bool(settings.THE_GRAPH_API_KEY) else "mock/fallback",
            "coingecko": "configured" if bool(settings.COINGECKO_API_KEY) else "public-tier"
        }
    }

# Dynamic router inclusion with graceful fallbacks
def register_routers():
    try:
        from backend.src.api.auth import router as auth_router
        app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth & Identity"])
    except ImportError:
        pass

    try:
        from backend.src.api.portfolio import router as portfolio_router
        app.include_router(portfolio_router, prefix=f"{settings.API_V1_STR}/portfolio", tags=["Portfolio"])
    except ImportError:
        pass

    try:
        from backend.src.api.blotter import router as blotter_router
        app.include_router(blotter_router, prefix=f"{settings.API_V1_STR}/blotter", tags=["Manual Blotter"])
    except ImportError:
        pass

    try:
        from backend.src.api.risk import router as risk_router
        app.include_router(risk_router, prefix=f"{settings.API_V1_STR}/risk", tags=["Risk Analytics"])
    except ImportError:
        pass

    try:
        from backend.src.api.rebalance import router as rebalance_router
        app.include_router(rebalance_router, prefix=f"{settings.API_V1_STR}/rebalance", tags=["Rebalancing"])
    except ImportError:
        pass

    try:
        from backend.src.api.copilot import router as copilot_router
        app.include_router(copilot_router, prefix=f"{settings.API_V1_STR}/copilot", tags=["Gemini Copilot"])
    except ImportError:
        pass

register_routers()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.src.main:app", host="0.0.0.0", port=8000, reload=True)
