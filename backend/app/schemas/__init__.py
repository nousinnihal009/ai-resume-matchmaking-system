"""
Schemas package initialization.
"""
from .base import APIResponse, PaginatedResponse
from .user import (
    UserBase, UserCreate, UserUpdate, LoginRequest, SignupRequest,
    StudentProfileBase, RecruiterProfileBase
)
from .resume import ResumeBase, ResumeCreate, ResumeUpdate, ResumeUploadResponse, Education, Experience
from .job import JobBase, JobCreate, JobUpdate, JobPostingForm
from .match import (
    MatchBase, MatchCreate, MatchUpdate, MatchExplanation,
    MatchFilters, SortOptions
)
from .analytics import MatchAnalytics, RecruiterDashboardStats, StudentDashboardStats

__all__ = [
    "APIResponse", "PaginatedResponse",
    "UserBase", "UserCreate", "UserUpdate", "LoginRequest", "SignupRequest",
    "StudentProfileBase", "RecruiterProfileBase",
    "ResumeBase", "ResumeCreate", "ResumeUpdate", "ResumeUploadResponse", "Education", "Experience",
    "JobBase", "JobCreate", "JobUpdate", "JobPostingForm",
    "MatchBase", "MatchCreate", "MatchUpdate", "MatchExplanation",
    "MatchFilters", "SortOptions",
    "MatchAnalytics", "RecruiterDashboardStats", "StudentDashboardStats",
]
