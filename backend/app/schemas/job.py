"""
Pydantic schemas for job endpoints.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from .base import BaseSchema, TimestampMixin, IDMixin


class SalaryInfo(BaseSchema):
    """Salary information schema."""
    min: Optional[float] = None
    max: Optional[float] = None
    currency: str = "USD"


class JobBase(BaseSchema):
    """Base job schema."""
    title: str
    company: str
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: Literal["internship", "entry", "mid", "senior"]
    location: str
    location_type: Literal["onsite", "remote", "hybrid"]
    salary: Optional[SalaryInfo] = None
    status: str = "active"


class JobCreate(JobBase):
    """Schema for creating a new job."""
    pass


class JobUpdate(BaseSchema):
    """Schema for updating job information."""
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_level: Optional[Literal["internship", "entry", "mid", "senior"]] = None
    location: Optional[str] = None
    location_type: Optional[Literal["onsite", "remote", "hybrid"]] = None
    salary: Optional[SalaryInfo] = None
    status: Optional[str] = None


class Job(JobBase, IDMixin, TimestampMixin):
    """Full job schema."""
    recruiter_id: str
    posted_at: str
    embedding_vector: Optional[List[float]] = None


class JobListResponse(BaseSchema):
    """Response schema for job list with pagination."""
    success: bool
    data: dict  # Paginated response
    timestamp: str


class JobResponse(BaseSchema):
    """Response schema for single job."""
    success: bool
    data: Optional[Job] = None
    error: Optional[str] = None
    timestamp: str
