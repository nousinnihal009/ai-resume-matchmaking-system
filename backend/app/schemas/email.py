"""
Email payload schemas.

These Pydantic models define the data required for each email template.
All email sending goes through app.core.email.EmailService.
"""
from pydantic import BaseModel, EmailStr


class WelcomeEmailPayload(BaseModel):
    """Data required to send a welcome email after signup."""
    to_email: EmailStr
    to_name: str
    role: str


class MatchNotificationPayload(BaseModel):
    """Data required to notify a student of a new match."""
    to_email: EmailStr
    to_name: str
    job_title: str
    company_name: str
    match_score: int
    match_id: str
    dashboard_url: str


class RecruiterMatchPayload(BaseModel):
    """Data required to notify a recruiter of a new candidate match."""
    to_email: EmailStr
    to_name: str
    candidate_name: str
    job_title: str
    match_score: int
    match_id: str
    dashboard_url: str
