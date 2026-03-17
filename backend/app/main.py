"""
Main FastAPI application.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .core.config import settings
from .api import auth, resumes, jobs, matches, analytics
from .db import engine, Base
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .core.limiter import limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting up FastAPI application...")

    # Schema is managed by Alembic migrations.
    # To apply: alembic upgrade head
    # To create a new migration: alembic revision --autogenerate -m "description"
    # To rollback one step: alembic downgrade -1
    # WARNING: Do not re-enable create_all — it cannot track schema changes.
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    logger.info("Database schema managed by Alembic migrations")

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}


@app.get("/ready")
async def readiness_check():
    """Readiness probe — validates database connectivity before
    accepting traffic. Returns 503 if any critical dependency
    is unavailable."""
    checks = {"api": "ok"}
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "unavailable"
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": checks,
                "version": settings.version
            }
        )
    return {"status": "ready", "checks": checks, "version": settings.version}


# API routes
api_prefix = settings.api_v1_prefix
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
app.include_router(resumes.router, prefix=f"{api_prefix}/resumes", tags=["Resumes"])
app.include_router(jobs.router, prefix=f"{api_prefix}/jobs", tags=["Jobs"])
app.include_router(matches.router, prefix=f"{api_prefix}/matches", tags=["Matches"])
app.include_router(analytics.router, prefix=f"{api_prefix}/analytics", tags=["Analytics"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
