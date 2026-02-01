"""
Match-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

from .base import BaseSchema


class MatchExplanation(BaseSchema):
    """Match explanation schema."""
    summary: str
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    skill_breakdown: Dict[str, List[str]] = Field(default_factory=dict)


class MatchBase(BaseSchema):
    """Base match schema."""
    id: UUID
    resume_id: UUID
    job_id: UUID
    student_id: UUID
    recruiter_id: UUID
    overall_score: float = Field(..., ge=0, le=1)
    skill_score: float = Field(..., ge=0, le=1)
    experience_score: float = Field(..., ge=0, le=1)
    semantic_score: float = Field(..., ge=0, le=1)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    explanation: MatchExplanation
    status: str  # 'pending' | 'viewed' | 'shortlisted' | 'rejected'
    created_at: datetime
    updated_at: datetime


class MatchCreate(BaseModel):
    """Schema for creating a match."""
    resume_id: UUID
    job_id: UUID
    student_id: UUID
    recruiter_id: UUID
    overall_score: float = Field(..., ge=0, le=1)
    skill_score: float = Field(..., ge=0, le=1)
    experience_score: float = Field(..., ge=0, le=1)
    semantic_score: float = Field(..., ge=0, le=1)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    explanation: MatchExplanation


class MatchUpdate(BaseModel):
    """Schema for updating match status."""
    status: str = Field(..., pattern="^(pending|viewed|shortlisted|rejected)$")


class MatchFilters(BaseModel):
    """Filters for match queries."""
    min_score: Optional[float] = Field(None, ge=0, le=1)
    max_score: Optional[float] = Field(None, ge=0, le=1)
    skills: Optional[List[str]] = None
    experience_level: Optional[List[str]] = None
    location: Optional[List[str]] = None
    status: Optional[List[str]] = None


class SortOptions(BaseModel):
    """Sorting options for matches."""
    field: str = Field("score", pattern="^(score|date|name|company)$")
    order: str = Field("desc", pattern="^(asc|desc)$")
