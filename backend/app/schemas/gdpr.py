"""
GDPR/CCPA compliance Pydantic schemas.

Defines request/response models for:
  - Consent tracking (record and query user consent)
  - Data export (right of access — Article 15 GDPR)
  - Data deletion (right to erasure — Article 17 GDPR)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

from .base import BaseSchema


# ── Consent ────────────────────────────────────────────────────────────

class ConsentRecord(BaseSchema):
    """Represents a single consent record for a user."""
    user_id: UUID
    consent_type: str  # 'data_processing' | 'email_marketing' | 'analytics'
    granted: bool
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    ip_address: Optional[str] = None


class ConsentUpdateRequest(BaseModel):
    """Request to grant or revoke a specific consent type."""
    consent_type: str = Field(
        ...,
        pattern="^(data_processing|email_marketing|analytics)$",
        description="Type of consent to update",
    )
    granted: bool = Field(..., description="True to grant, False to revoke")


class ConsentStatusResponse(BaseSchema):
    """Current consent status for all consent types."""
    user_id: UUID
    consents: Dict[str, bool] = Field(default_factory=dict)
    last_updated: Optional[datetime] = None


# ── Data Export ────────────────────────────────────────────────────────

class DataExportResponse(BaseSchema):
    """Full data export for a user (right of access)."""
    user_id: UUID
    email: str
    name: str
    role: str
    created_at: datetime
    resumes: List[Dict[str, Any]] = Field(default_factory=list)
    matches: List[Dict[str, Any]] = Field(default_factory=list)
    analytics_events: List[Dict[str, Any]] = Field(default_factory=list)
    consents: Dict[str, bool] = Field(default_factory=dict)
    exported_at: datetime


# ── Data Deletion ──────────────────────────────────────────────────────

class DeletionRequest(BaseModel):
    """Request to delete all user data (right to erasure)."""
    confirm: bool = Field(
        ...,
        description="Must be True to confirm deletion",
    )
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional reason for deletion",
    )


class DeletionResponse(BaseSchema):
    """Acknowledgement that a deletion request has been accepted."""
    user_id: UUID
    status: str  # 'queued' | 'processing' | 'completed'
    task_id: Optional[str] = None
    message: str
    requested_at: datetime
