"""
Admin dashboard request and response schemas.

All schemas in this module are for admin-only endpoints.
They must never be exposed to student or recruiter roles.
"""
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class UserSummary(BaseModel):
    """Lightweight user record for admin list views."""
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime | None = None
    resume_count: int = 0
    match_count: int = 0


class SystemStats(BaseModel):
    """Platform-wide statistics for the admin dashboard."""
    total_users: int
    total_students: int
    total_recruiters: int
    total_resumes: int
    total_jobs: int
    total_matches: int
    active_jobs: int
    matches_this_week: int
    avg_match_score: float
    top_skills: list[str]


class UserStatusUpdate(BaseModel):
    """Request to activate or deactivate a user account."""
    is_active: bool
    reason: str | None = None


class AdminMatchAudit(BaseModel):
    """Match record with full context for admin audit view."""
    id: str
    student_email: str
    job_title: str
    company: str
    overall_score: float
    status: str
    created_at: datetime | None = None


class PlatformHealthResponse(BaseModel):
    """Real-time platform health indicators."""
    api_status: str
    database_status: str
    redis_status: str
    celery_worker_status: str
    pending_resume_tasks: int
    failed_tasks_last_hour: int
    uptime_seconds: float
