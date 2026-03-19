"""
Celery tasks for resume processing and batch matching.

These tasks run in a separate worker process and use **synchronous**
SQLAlchemy sessions because Celery workers run their own event loop
(or none at all). The async pipeline services are called via
asyncio.run() to bridge the gap.

Task results are stored in Redis so the FastAPI endpoint can poll
for status using the task ID.
"""
import asyncio
import logging
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.worker.celery_app import celery

logger = logging.getLogger(__name__)


def _get_sync_db_url() -> str:
    """Convert async DB URL to synchronous for Celery workers."""
    url = settings.database_url
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "")
    return url


def _make_sync_session() -> Session:
    """Create a one-off synchronous SQLAlchemy session."""
    engine = create_engine(_get_sync_db_url())
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return factory()


@celery.task(
    bind=True,
    name="app.worker.tasks.process_resume_task",
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def process_resume_task(self, resume_id: str, file_path: str) -> dict:
    """
    Background task: extract text + skills from a saved resume file
    and update the database record.

    Args:
        resume_id: UUID string of the Resume row (already persisted
                   with status='processing').
        file_path: Absolute path to the uploaded file on disk.

    Returns:
        dict with 'status' and 'extracted_skills' on success.
    """
    from app.db.models import Resume
    from app.pipeline.text_extraction import text_extraction_service
    from app.pipeline.skill_extraction import skill_extractor

    session = _make_sync_session()
    try:
        # ── 1. Load the resume row ──────────────────────────────────
        resume = session.execute(
            select(Resume).where(Resume.id == UUID(resume_id))
        ).scalar_one_or_none()

        if not resume:
            logger.error("process_resume_task: resume %s not found", resume_id)
            return {"status": "failed", "error": "Resume not found"}

        # ── 2. Extract text (async pipeline → sync bridge) ──────────
        extracted_text = asyncio.run(
            text_extraction_service.extract_text(file_path)
        )

        # ── 3. Extract skills ───────────────────────────────────────
        skill_data = asyncio.run(
            skill_extractor.extract_skills(extracted_text)
        )

        # ── 4. Update the row ───────────────────────────────────────
        resume.extracted_text = extracted_text
        resume.extracted_skills = skill_data["extracted_skills"]
        resume.extra_metadata = {
            "skill_confidence": skill_data["confidence"],
            "skill_categories": skill_data["categories"],
        }
        resume.status = "completed"

        session.commit()
        logger.info("process_resume_task: completed for resume %s", resume_id)

        return {
            "status": "completed",
            "resume_id": resume_id,
            "extracted_skills": skill_data["extracted_skills"],
        }

    except Exception as exc:
        session.rollback()
        logger.error("process_resume_task failed for %s: %s", resume_id, exc)

        # Mark as failed in DB so the UI can show the error
        try:
            resume = session.execute(
                select(Resume).where(Resume.id == UUID(resume_id))
            ).scalar_one_or_none()
            if resume:
                resume.status = "failed"
                session.commit()
        except Exception:
            session.rollback()

        # Retry with exponential backoff
        raise self.retry(exc=exc)

    finally:
        session.close()


@celery.task(
    bind=True,
    name="app.worker.tasks.batch_match_task",
    max_retries=2,
    default_retry_delay=120,
    acks_late=True,
)
def batch_match_task(self, resume_id: str | None = None, job_id: str | None = None) -> dict:
    """
    Background task: run the matching engine for a resume or a job
    and persist the resulting Match rows.

    Exactly one of resume_id or job_id must be provided.

    Returns:
        dict with 'status' and 'match_count'.
    """
    from app.db.models import Resume, Job, Match, User
    from app.pipeline.matching import matching_engine
    from app.schemas.match import MatchCreate

    if not resume_id and not job_id:
        return {"status": "failed", "error": "Must provide resume_id or job_id"}

    session = _make_sync_session()
    try:
        created_count = 0

        if resume_id:
            # ── Match resume → jobs ─────────────────────────────────
            resume = session.execute(
                select(Resume).where(Resume.id == UUID(resume_id))
            ).scalar_one_or_none()
            if not resume:
                return {"status": "failed", "error": "Resume not found"}

            jobs = list(
                session.execute(
                    select(Job).where(Job.status == "active")
                ).scalars().all()
            )
            if not jobs:
                return {"status": "completed", "match_count": 0}

            resume_data = {
                "id": str(resume.id),
                "user_id": str(resume.user_id),
                "extracted_text": resume.extracted_text or "",
                "extracted_skills": resume.extracted_skills or [],
            }
            job_data_list = [
                {
                    "id": str(j.id),
                    "recruiter_id": str(j.recruiter_id),
                    "title": j.title,
                    "description": j.description,
                    "required_skills": j.required_skills or [],
                    "preferred_skills": j.preferred_skills or [],
                    "experience_level": j.experience_level,
                }
                for j in jobs
            ]

            results = asyncio.run(
                matching_engine.match_resume_to_jobs(resume_data, job_data_list)
            )

        else:
            # ── Match job → resumes ─────────────────────────────────
            job = session.execute(
                select(Job).where(Job.id == UUID(job_id))
            ).scalar_one_or_none()
            if not job:
                return {"status": "failed", "error": "Job not found"}

            resumes = list(
                session.execute(select(Resume)).scalars().all()
            )
            if not resumes:
                return {"status": "completed", "match_count": 0}

            job_data = {
                "id": str(job.id),
                "recruiter_id": str(job.recruiter_id),
                "title": job.title,
                "description": job.description,
                "required_skills": job.required_skills or [],
                "preferred_skills": job.preferred_skills or [],
                "experience_level": job.experience_level,
            }
            resume_data_list = [
                {
                    "id": str(r.id),
                    "user_id": str(r.user_id),
                    "extracted_text": r.extracted_text or "",
                    "extracted_skills": r.extracted_skills or [],
                }
                for r in resumes
            ]

            results = asyncio.run(
                matching_engine.match_job_to_resumes(job_data, resume_data_list)
            )

        # ── Persist match rows ──────────────────────────────────────
        for result in results:
            match_obj = Match(
                resume_id=UUID(result["resume_id"]),
                job_id=UUID(result["job_id"]),
                student_id=UUID(result["student_id"]),
                recruiter_id=UUID(result["recruiter_id"]),
                overall_score=result["overall_score"],
                skill_score=result["skill_score"],
                experience_score=result["experience_score"],
                semantic_score=result["semantic_score"],
                matched_skills=result["matched_skills"],
                missing_skills=result["missing_skills"],
                explanation=result["explanation"],
            )
            session.add(match_obj)
            created_count += 1

        session.commit()
        logger.info(
            "batch_match_task: created %d matches (resume=%s, job=%s)",
            created_count,
            resume_id,
            job_id,
        )

        return {
            "status": "completed",
            "match_count": created_count,
            "resume_id": resume_id,
            "job_id": job_id,
        }

    except Exception as exc:
        session.rollback()
        logger.error("batch_match_task failed: %s", exc)
        raise self.retry(exc=exc)

    finally:
        session.close()
