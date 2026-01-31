"""
Pydantic schemas for match endpoints.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from .base import BaseSchema, TimestampMixin, IDMixin


class MatchExplanation(BaseSchema):
    """Match explanation schema."""
    summary: str
    quality: str
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]
    skill_breakdown: Dict[str, Any]
    score_breakdown: Dict[str, float]


class MatchBase(BaseSchema):
    """Base match schema."""
    resume_id: str
    job_id: str
    student_id: str
    recruiter_id: str
    overall_score: float
    skill_score: float
    experience_score: float
    semantic_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: MatchExplanation
    status: str = "pending"


class Match(MatchBase, IDMixin, TimestampMixin):
    """Full match schema."""
    pass


class MatchResponse(BaseSchema):
    """Response schema for match operations."""
    success: bool
    data: Optional[List[Match]] = None
    error: Optional[str] = None
    timestamp: str


class MatchUpdate(BaseSchema):
    """Schema for updating match status."""
    status: str
