"""
Job-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID

from .base import BaseSchema


class JobBase(BaseSchema):
    """Base job schema."""
    id: UUID
    recruiter_id: UUID
    title: str
    company: str
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: str  # 'internship' | 'entry' | 'mid' | 'senior'
    location: str
    location_type: str  # 'onsite' | 'remote' | 'hybrid'
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    posted_at: datetime
    expires_at: Optional[datetime] = None
    status: str  # 'active' | 'closed' | 'draft'
    extra_metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class JobCreate(BaseModel):
    """Schema for creating a job."""
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: str = Field(..., pattern="^(internship|entry|mid|senior)$")
    location: str = Field(..., min_length=1, max_length=255)
    location_type: str = Field(..., pattern="^(onsite|remote|hybrid)$")
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    salary_currency: str = Field(default="USD", min_length=3, max_length=3)


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_level: Optional[str] = Field(None, pattern="^(internship|entry|mid|senior)$")
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    location_type: Optional[str] = Field(None, pattern="^(onsite|remote|hybrid)$")
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    salary_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    status: Optional[str] = Field(None, pattern="^(active|closed|draft)$")
    expires_at: Optional[datetime] = None
    extra_metadata: Optional[dict] = None


class JobPostingForm(BaseModel):
    """Job posting form schema (matches frontend)."""
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: str = Field(..., pattern="^(internship|entry|mid|senior)$")
    location: str = Field(..., min_length=1, max_length=255)
    location_type: str = Field(..., pattern="^(onsite|remote|hybrid)$")
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    salary_currency: str = Field(default="USD", min_length=3, max_length=3)


class JobFilters(BaseModel):
    """Filters for job queries."""
    status: Optional[List[str]] = None
    experience_level: Optional[List[str]] = None
    location: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    company: Optional[str] = None
