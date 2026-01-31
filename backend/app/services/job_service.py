"""
Job service for handling job operations.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.db.models import Job, User
from app.schemas.job import JobCreate, JobUpdate
from app.pipeline.text_extraction import extract_text_from_job_description
from app.pipeline.skill_extraction import extract_skills_from_job
from app.pipeline.embeddings import generate_embedding

logger = structlog.get_logger(__name__)


class JobService:
    """Service for handling job operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, job_data: JobCreate, recruiter_id: str) -> Job:
        """
        Create a new job posting.
        """
        logger.info("Creating job", title=job_data.title, recruiter_id=recruiter_id)

        # Generate unique ID for job
        job_id = str(uuid.uuid4())

        # Combine title and description for processing
        full_text = f"{job_data.title} {job_data.description}"

        # Extract skills from job description
        skills = await extract_skills_from_job(full_text)

        # Generate embedding
        embedding = await generate_embedding(full_text)

        # Create salary dict if provided
        salary_data = None
        if job_data.salary:
            salary_data = {
                "min": job_data.salary.min,
                "max": job_data.salary.max,
                "currency": job_data.salary.currency,
            }

        # Create job record
        job = Job(
            id=job_id,
            recruiter_id=recruiter_id,
            title=job_data.title,
            company=job_data.company,
            description=job_data.description,
            required_skills=job_data.required_skills,
            preferred_skills=job_data.preferred_skills,
            experience_level=job_data.experience_level,
            location=job_data.location,
            location_type=job_data.location_type,
            salary_min=salary_data.get("min") if salary_data else None,
            salary_max=salary_data.get("max") if salary_data else None,
            salary_currency=salary_data.get("currency") if salary_data else "USD",
            posted_at=datetime.utcnow(),
            status=job_data.status,
            embedding_vector=embedding,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        logger.info("Job created successfully", job_id=job_id)
        return job

    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.
        """
        stmt = select(Job).where(Job.id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_jobs_by_recruiter(self, recruiter_id: str) -> List[Job]:
        """
        Get all jobs for a recruiter.
        """
        stmt = select(Job).where(Job.recruiter_id == recruiter_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_all_jobs(self, status: Optional[str] = None) -> List[Job]:
        """
        Get all jobs, optionally filtered by status.
        """
        stmt = select(Job)
        if status:
            stmt = stmt.where(Job.status == status)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_job(self, job_id: str, updates: JobUpdate) -> Optional[Job]:
        """
        Update job information.
        """
        job = await self.get_job_by_id(job_id)
        if not job:
            return None

        update_data = updates.dict(exclude_unset=True)

        # Handle salary updates
        if "salary" in update_data and update_data["salary"]:
            salary = update_data.pop("salary")
            job.salary_min = salary.get("min")
            job.salary_max = salary.get("max")
            job.salary_currency = salary.get("currency", "USD")

        for field, value in update_data.items():
            setattr(job, field, value)

        job.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(job)

        return job

    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.
        """
        logger.info("Deleting job", job_id=job_id)

        job = await self.get_job_by_id(job_id)
        if not job:
            return False

        await self.db.delete(job)
        await self.db.commit()

        logger.info("Job deleted successfully", job_id=job_id)
        return True
