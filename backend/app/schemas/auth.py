"""
Pydantic schemas for authentication endpoints.
"""
from typing import Literal
from pydantic import BaseModel, EmailStr, Field

from .base import BaseSchema, TimestampMixin, IDMixin


class UserBase(BaseSchema):
    """Base user schema."""
    email: EmailStr
    name: str
    role: Literal["student", "recruiter", "admin"]


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseSchema):
    """Schema for updating user information."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase, IDMixin, TimestampMixin):
    """Full user schema."""
    pass


class StudentProfileBase(BaseSchema):
    """Base student profile schema."""
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None


class StudentProfile(StudentProfileBase, IDMixin, TimestampMixin):
    """Full student profile schema."""
    user_id: str


class RecruiterProfileBase(BaseSchema):
    """Base recruiter profile schema."""
    company: str
    position: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None


class RecruiterProfile(RecruiterProfileBase, IDMixin, TimestampMixin):
    """Full recruiter profile schema."""
    user_id: str


class LoginRequest(BaseSchema):
    """Login request schema."""
    email: EmailStr
    password: str
    role: Literal["student", "recruiter"]


class SignupRequest(UserCreate):
    """Signup request schema."""
    pass


class TokenData(BaseSchema):
    """JWT token data."""
    user_id: str
    email: str
    role: str
    exp: int
