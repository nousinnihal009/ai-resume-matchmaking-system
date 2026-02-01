"""
Resume-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

from .base import BaseSchema


class Education(BaseSchema):
    """Education schema."""
    institution: str
    degree: str
    field_of_study: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None


class Experience(BaseSchema):
    """Experience schema."""
    company: str
    position: str
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    skills: Optional[List[str]] = None


class ResumeBase(BaseSchema):
    """Base resume schema."""
    id: UUID
    user_id: UUID
    file_name: str
    file_url: str
    file_size: int
    uploaded_at: datetime
    extracted_text: Optional[str] = None
    extracted_skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    status: str  # 'processing' | 'completed' | 'failed'
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ResumeCreate(BaseModel):
    """Schema for creating a resume (handled by upload)."""
    pass  # Resume creation is handled by file upload


class ResumeUpdate(BaseModel):
    """Schema for updating a resume."""
    extracted_text: Optional[str] = None
    extracted_skills: Optional[List[str]] = None
    education: Optional[List[Education]] = None
    experience: Optional[List[Experience]] = None
    status: Optional[str] = Field(None, pattern="^(processing|completed|failed)$")
    metadata: Optional[Dict[str, Any]] = None


class ResumeUploadResponse(BaseSchema):
    """Response for resume upload."""
    resume: ResumeBase
    processing_status: str  # 'queued' | 'processing' | 'completed'
