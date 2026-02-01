"""
User-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

from .base import BaseSchema


class UserBase(BaseSchema):
    """Base user schema."""
    id: UUID
    email: str
    name: str
    role: str  # 'student' | 'recruiter' | 'admin'
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    """Schema for creating a user."""
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., pattern="^(student|recruiter|admin)$")
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    company: Optional[str] = None
    position: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=8)


class StudentProfileBase(BaseSchema):
    """Student profile schema."""
    id: UUID
    user_id: UUID
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RecruiterProfileBase(BaseSchema):
    """Recruiter profile schema."""
    id: UUID
    user_id: UUID
    company: str
    position: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    """Login request schema."""
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(student|recruiter|admin)$")


class SignupRequest(BaseModel):
    """Signup request schema."""
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., pattern="^(student|recruiter|admin)$")
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    company: Optional[str] = None
    position: Optional[str] = None
