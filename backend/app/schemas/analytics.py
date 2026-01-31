"""
Pydantic schemas for analytics endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel

from .base import BaseSchema


class StudentAnalytics(BaseSchema):
    """Analytics data for students."""
    resumes_uploaded: int
    matches_found: int
    average_score: float
    top_matched_roles: List[str]


class RecruiterAnalytics(BaseSchema):
    """Analytics data for recruiters."""
    active_jobs: int
    total_candidates: int
    shortlisted_candidates: int
    average_match_score: float


class AnalyticsResponse(BaseSchema):
    """Response schema for analytics."""
    success: bool
    data: Optional[StudentAnalytics | RecruiterAnalytics] = None
    error: Optional[str] = None
    timestamp: str
