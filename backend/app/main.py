"""
Main FastAPI application.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .core.config import settings
from .api import auth, resumes, jobs, matches, analytics, gdpr
from .db import engine, Base
import sentry_sdk
# from slowapi import _rate_limit_exceeded_handler
# from slowapi.errors import RateLimitExceeded
from .core.limiter import limiter

from app.core.logging_config import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup validation for critical production secrets
    if not settings.debug:
        if settings.secret_key == "supersecretkey" or len(settings.secret_key) < 32:
            logger.critical("startup_failed_insecure_secret_key")
            raise ValueError("CRITICAL: Insecure SECRET_KEY in production.")
            
        if "*" in settings.cors_origins:
            logger.critical("startup_failed_insecure_cors")
            raise ValueError("CRITICAL: Wildcard CORS allowed in production.")

    # Startup
    configure_logging()
    logger.info(
        "application_startup",
        version=settings.version,
        debug=settings.debug,
        environment="development" if settings.debug else "production",
    )
    from app.core.sentry import initialize_sentry
    initialize_sentry(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
    )

    # Warm up embedding model on startup
    # Downloads ~90MB model on first run, loads from cache thereafter
    # This prevents 30-60 second delay on the first API request
    try:
        logger.info("embedding_model_warmup_started")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: __import__(
                'app.core.model_manager',
                fromlist=['get_embedding_model']
            ).get_embedding_model()
        )
        logger.info("embedding_model_warmup_complete")
    except Exception as exc:
        logger.error(
            "embedding_model_warmup_failed",
            error=str(exc),
            note="API will still start but first embedding "
                 "request will be slow",
        )

    # Schema is managed by Alembic migrations.
    # To apply: alembic upgrade head
    # To create a new migration: alembic revision --autogenerate -m "description"
    # To rollback one step: alembic downgrade -1
    # WARNING: Do not re-enable create_all — it cannot track schema changes.
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    logger.info("db_schema_managed_by_alembic")

    yield

    # Shutdown
    logger.info("application_shutdown")


# Create FastAPI application
app = FastAPI(
    title="AI Resume Matchmaking API",
    description=(
        "Production API for the AI-powered resume-to-job matching platform. "
        "Supports student resume management, recruiter job postings, "
        "ML-driven match scoring, and GDPR-compliant data operations."
    ),
    version=settings.version,
    contact={
        "name": "Platform Engineering",
        "email": "engineering@resumematcher.com",
    },
    license_info={
        "name": "MIT",
    },
    # Disable interactive docs in production
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """
    Applies production security headers to all HTTP responses.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log every HTTP request with method, path, and response status."""
    import time
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        client_ip=request.client.host if request.client else "unknown",
    )
    return response


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
app.include_router(gdpr.router, prefix=f"{api_prefix}/gdpr", tags=["GDPR"])

from .api import admin as admin_router
app.include_router(
    admin_router.router,
    prefix=f"{api_prefix}/admin",
    tags=["Admin"],
)

from .api import resume_analysis
app.include_router(
    resume_analysis.router,
    prefix=f"{api_prefix}/resume-analysis",
    tags=["Resume Analysis"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error("unhandled_exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Internal server error: {str(exc)}",
            "detail": f"Internal server error: {str(exc)}",
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
