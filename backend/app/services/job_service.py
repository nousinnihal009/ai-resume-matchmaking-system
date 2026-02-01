"""
Job service layer for business logic.
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_

from ..db.models import Job, User
from ..schemas.job import JobCreate, JobUpdate, JobFilters
from ..pipeline.skill_extraction import skill_extractor

logger = logging.getLogger(__name__)


class JobService:
    """Service for job-related operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def create_job(self, job_data: JobCreate, recruiter_id: UUID) -> Optional[Job]:
        """Create a new job posting."""
        try:
            # Validate recruiter exists and is a recruiter
            recruiter = await self._get_recruiter_by_id(recruiter_id)
            if not recruiter or recruiter.role != "recruiter":
                return None

            # Create job
            job = Job(
                recruiter_id=recruiter_id,
                title=job_data.title,
                company=job_data.company,
                description=job_data.description,
                required_skills=job_data.required_skills,
                preferred_skills=job_data.preferred_skills,
                experience_level=job_data.experience_level,
                location=job_data.location,
                location_type=job_data.location_type,
                salary_min=job_data.salary_min,
                salary_max=job_data.salary_max,
                salary_currency=job_data.salary_currency,
                status="active"
            )

            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)

            logger.info(f"Created job: {job.id} for recruiter: {recruiter_id}")
            return job

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating job for recruiter {recruiter_id}: {e}")
            return None

    async def get_job_by_id(self, job_id: UUID) -> Optional[Job]:
        """Get job by ID."""
        try:
            result = await self.db.execute(
                select(Job).where(Job.id == job_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting job by ID {job_id}: {e}")
            return None

    async def get_jobs_by_recruiter(self, recruiter_id: UUID) -> List[Job]:
        """Get all jobs posted by a recruiter."""
        try:
            result = await self.db.execute(
                select(Job).where(Job.recruiter_id == recruiter_id)
                .order_by(desc(Job.posted_at))
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting jobs for recruiter {recruiter_id}: {e}")
            return []

    async def get_all_jobs(self, filters: Optional[JobFilters] = None) -> List[Job]:
        """Get all active jobs with optional filters."""
        try:
            query = select(Job).where(Job.status == "active")

            if filters:
                # Apply filters
                if filters.experience_level:
                    query = query.where(Job.experience_level.in_(filters.experience_level))

                if filters.location:
                    # Simple location matching - could be enhanced with geocoding
                    location_conditions = [Job.location.ilike(f"%{loc}%") for loc in filters.location]
                    query = query.where(or_(*location_conditions))

            result = await self.db.execute(
                query.order_by(desc(Job.posted_at))
            )
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error getting all jobs: {e}")
            return []

    async def update_job(self, job_id: UUID, job_data: JobUpdate) -> Optional[Job]:
        """Update job information."""
        try:
            job = await self.get_job_by_id(job_id)
            if not job:
                return None

            # Update fields
            for field, value in job_data.dict(exclude_unset=True).items():
                setattr(job, field, value)

            await self.db.commit()
            await self.db.refresh(job)

            logger.info(f"Updated job: {job_id}")
            return job

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating job {job_id}: {e}")
            return None

    async def delete_job(self, job_id: UUID) -> bool:
        """Delete a job posting."""
        try:
            job = await self.get_job_by_id(job_id)
            if not job:
                return False

            await self.db.delete(job)
            await self.db.commit()

            logger.info(f"Deleted job: {job_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting job {job_id}: {e}")
            return False

    async def _get_recruiter_by_id(self, recruiter_id: UUID) -> Optional[User]:
        """Get recruiter user by ID."""
        try:
            result = await self.db.execute(
                select(User).where(
                    and_(User.id == recruiter_id, User.role == "recruiter")
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting recruiter by ID {recruiter_id}: {e}")
            return None
