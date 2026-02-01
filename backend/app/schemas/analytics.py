"""
Analytics-related Pydantic schemas.
"""
from typing import List
from pydantic import BaseModel, Field

from .base import BaseSchema


class SkillFrequency(BaseModel):
    """Skill frequency data."""
    skill: str
    frequency: int


class MatchAnalytics(BaseSchema):
    """Match analytics data."""
    total_matches: int
    average_score: float
    score_distribution: dict = Field(default_factory=dict)  # 'excellent', 'good', 'fair', 'poor'
    top_skills: List[SkillFrequency] = Field(default_factory=list)


class RecruiterDashboardStats(BaseSchema):
    """Recruiter dashboard statistics."""
    active_jobs: int
    total_candidates: int
    shortlisted_candidates: int
    average_match_score: float


class StudentDashboardStats(BaseSchema):
    """Student dashboard statistics."""
    resumes_uploaded: int
    matches_found: int
    average_score: float
    top_matched_roles: List[str] = Field(default_factory=list)
