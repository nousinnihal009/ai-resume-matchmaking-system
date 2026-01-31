"""
Main API router for version 1 endpoints.
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .resumes import router as resume_router
from .jobs import router as job_router
from .matches import router as match_router
from .analytics import router as analytics_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(resume_router, prefix="/resumes", tags=["resumes"])
api_router.include_router(job_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(match_router, prefix="/matches", tags=["matches"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
