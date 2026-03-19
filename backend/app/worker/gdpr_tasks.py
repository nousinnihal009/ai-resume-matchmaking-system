"""
Celery task for GDPR cascading data deletion.

This task runs in a Celery worker process and uses a **synchronous**
SQLAlchemy session to cascade-delete all user data across every table.

Deletion order matters — child rows must be deleted before parent
rows to avoid FK constraint violations:
  1. match_history  (references matches.id)
  2. matches        (references resumes.id, jobs.id, users.id)
  3. embeddings     (references entity_id which may be a resume)
  4. resumes        (references users.id) — also deletes files on disk
  5. jobs           (references users.id — if recruiter)
  6. analytics_events (references users.id)
  7. student_profiles / recruiter_profiles (references users.id)
  8. users           (the user row itself)
"""
import logging
import os
from uuid import UUID

from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.worker.celery_app import celery

logger = logging.getLogger(__name__)


def _get_sync_db_url() -> str:
    url = settings.database_url
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "")
    return url


def _make_sync_session() -> Session:
    engine = create_engine(_get_sync_db_url())
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return factory()


@celery.task(
    bind=True,
    name="app.worker.gdpr_tasks.gdpr_delete_user_data_task",
    max_retries=2,
    default_retry_delay=120,
    acks_late=True,
)
def gdpr_delete_user_data_task(self, user_id: str) -> dict:
    """
    Cascade-delete every row and file linked to a user.

    Args:
        user_id: UUID string of the user to erase.

    Returns:
        dict summarising what was deleted.
    """
    from app.db.models import (
        User, Resume, Match, Embedding, AnalyticsEvent,
        MatchHistory, StudentProfile, RecruiterProfile, Job,
    )

    session = _make_sync_session()
    uid = UUID(user_id)
    summary: dict = {"user_id": user_id, "deleted": {}}

    try:
        # ── 1. Match history (via match IDs owned by user) ──────────
        match_ids_q = select(Match.id).where(
            (Match.student_id == uid) | (Match.recruiter_id == uid)
        )
        match_ids = [row[0] for row in session.execute(match_ids_q).all()]
        if match_ids:
            session.execute(
                delete(MatchHistory).where(MatchHistory.match_id.in_(match_ids))
            )
        summary["deleted"]["match_history"] = len(match_ids)

        # ── 2. Matches ─────────────────────────────────────────────
        result = session.execute(
            delete(Match).where(
                (Match.student_id == uid) | (Match.recruiter_id == uid)
            )
        )
        summary["deleted"]["matches"] = result.rowcount

        # ── 3. Embeddings (for user's resumes) ─────────────────────
        resume_ids_q = select(Resume.id).where(Resume.user_id == uid)
        resume_ids = [row[0] for row in session.execute(resume_ids_q).all()]
        if resume_ids:
            session.execute(
                delete(Embedding).where(Embedding.entity_id.in_(resume_ids))
            )
        summary["deleted"]["embeddings"] = len(resume_ids)

        # ── 4. Resumes + files on disk ─────────────────────────────
        resumes = list(
            session.execute(
                select(Resume).where(Resume.user_id == uid)
            ).scalars().all()
        )
        for resume in resumes:
            if resume.file_url and os.path.exists(resume.file_url):
                try:
                    os.remove(resume.file_url)
                except OSError as exc:
                    logger.warning(
                        "gdpr_file_delete_failed",
                        file=resume.file_url,
                        error=str(exc),
                    )
        session.execute(delete(Resume).where(Resume.user_id == uid))
        summary["deleted"]["resumes"] = len(resumes)

        # ── 5. Jobs (if recruiter) ─────────────────────────────────
        result = session.execute(
            delete(Job).where(Job.recruiter_id == uid)
        )
        summary["deleted"]["jobs"] = result.rowcount

        # ── 6. Analytics events ────────────────────────────────────
        result = session.execute(
            delete(AnalyticsEvent).where(AnalyticsEvent.user_id == uid)
        )
        summary["deleted"]["analytics_events"] = result.rowcount

        # ── 7. Profiles ────────────────────────────────────────────
        session.execute(
            delete(StudentProfile).where(StudentProfile.user_id == uid)
        )
        session.execute(
            delete(RecruiterProfile).where(RecruiterProfile.user_id == uid)
        )

        # ── 8. User row ───────────────────────────────────────────
        session.execute(delete(User).where(User.id == uid))
        summary["deleted"]["user"] = 1

        session.commit()
        summary["status"] = "completed"
        logger.info("gdpr_deletion_completed", **summary)
        return summary

    except Exception as exc:
        session.rollback()
        logger.error("gdpr_deletion_failed", user_id=user_id, error=str(exc))
        raise self.retry(exc=exc)

    finally:
        session.close()
