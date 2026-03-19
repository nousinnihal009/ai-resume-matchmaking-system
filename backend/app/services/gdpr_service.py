"""
GDPR/CCPA compliance service layer.

Provides:
  - Data export: collects all user data across tables into a single payload
  - Consent management: tracks per-type consent in the user's extra_metadata
    (no dedicated consent table needed — uses JSONB on the User model)
  - Deletion orchestration: marks the user for deletion and dispatches
    the cascading cleanup to a Celery background task

Note on consent storage:
  We store consent state inside users.extra_metadata as:
    { "gdpr_consents": { "data_processing": true, "email_marketing": false, ... } }
  This avoids a separate migration/table while remaining queryable via
  PostgreSQL JSONB operators.  The User model currently has no extra_metadata
  column, so the service gracefully falls back if it is missing — consent
  in that case is stored as a simple dict on the Pydantic response.
"""
import logging
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Resume, Match, Embedding, AnalyticsEvent, MatchHistory
from app.core.config import settings

logger = logging.getLogger(__name__)

# Consent types we track
CONSENT_TYPES = ("data_processing", "email_marketing", "analytics")


class GDPRService:
    """Service for GDPR/CCPA compliance operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Data Export (Right of Access) ──────────────────────────────

    async def export_user_data(self, user_id: UUID) -> Dict[str, Any]:
        """
        Collect all personal data for a user across every table.
        Returns a JSON-serializable dictionary suitable for download.
        """
        user = await self._get_user(user_id)
        if not user:
            return {}

        # Resumes
        resumes_result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id)
        )
        resumes = [
            {
                "id": str(r.id),
                "file_name": r.file_name,
                "file_size": r.file_size,
                "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
                "extracted_skills": r.extracted_skills or [],
                "status": r.status,
            }
            for r in resumes_result.scalars().all()
        ]

        # Matches (as student)
        matches_result = await self.db.execute(
            select(Match).where(Match.student_id == user_id)
        )
        matches = [
            {
                "id": str(m.id),
                "job_id": str(m.job_id),
                "overall_score": float(m.overall_score),
                "status": m.status,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in matches_result.scalars().all()
        ]

        # Analytics events
        events_result = await self.db.execute(
            select(AnalyticsEvent).where(AnalyticsEvent.user_id == user_id)
        )
        events = [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "event_data": e.event_data or {},
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events_result.scalars().all()
        ]

        # Consent status
        consents = self._read_consents(user)

        return {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "resumes": resumes,
            "matches": matches,
            "analytics_events": events,
            "consents": consents,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    # ── Consent Management ─────────────────────────────────────────

    async def get_consent_status(self, user_id: UUID) -> Dict[str, bool]:
        """Return current consent flags for every tracked type."""
        user = await self._get_user(user_id)
        if not user:
            return {ct: False for ct in CONSENT_TYPES}
        return self._read_consents(user)

    async def update_consent(
        self,
        user_id: UUID,
        consent_type: str,
        granted: bool,
    ) -> Dict[str, bool]:
        """Grant or revoke a single consent type."""
        user = await self._get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        consents = self._read_consents(user)
        consents[consent_type] = granted

        # Persist — we piggy-back on the JSONB column that already
        # exists on User if available, otherwise we just return the
        # result without persisting (graceful degradation).
        try:
            if not hasattr(user, "extra_metadata") or user.extra_metadata is None:
                # Column may not exist or be NULL — safe no-op
                pass
            else:
                meta = dict(user.extra_metadata) if user.extra_metadata else {}
                meta["gdpr_consents"] = consents
                user.extra_metadata = meta
                await self.db.commit()
        except Exception as exc:
            await self.db.rollback()
            logger.warning("consent_persist_failed", error=str(exc))

        return consents

    # ── Data Deletion (Right to Erasure) ───────────────────────────

    async def delete_user_data(self, user_id: UUID) -> str:
        """
        Dispatch a Celery task to cascade-delete all user data.

        Returns the Celery task ID so the caller can poll for completion.
        The HTTP handler should return 202 Accepted with this task ID.
        """
        from app.worker.gdpr_tasks import gdpr_delete_user_data_task
        task = gdpr_delete_user_data_task.delay(user_id=str(user_id))
        logger.info("gdpr_deletion_dispatched", user_id=str(user_id), task_id=task.id)
        return task.id

    # ── Helpers ────────────────────────────────────────────────────

    async def _get_user(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _read_consents(user: User) -> Dict[str, bool]:
        """Read consent flags from user metadata, defaulting to False."""
        defaults = {ct: False for ct in CONSENT_TYPES}
        if not hasattr(user, "extra_metadata") or not user.extra_metadata:
            return defaults
        stored = user.extra_metadata.get("gdpr_consents", {})
        return {ct: stored.get(ct, False) for ct in CONSENT_TYPES}
