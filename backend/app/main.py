"""
Main FastAPI application for AI Resume Matching Platform
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine
from app.db.base import Base

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    logger.info("Starting AI Resume Matching Platform")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created/verified")

    yield

    logger.info("Shutting down AI Resume Matching Platform")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI-powered resume-job matching platform",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add trusted host middleware
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "1.0.0"}

    return app


app = create_application()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests."""
    logger.info(
        "Request",
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
    )

    response = await call_next(request)

    logger.info(
        "Response",
        status_code=response.status_code,
        headers=dict(response.headers),
    )

    return response
