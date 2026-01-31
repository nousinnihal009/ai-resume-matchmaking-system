"""
Matching service for handling match operations.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.db.models import Match, Resume, Job
from app.pipeline.matching_engine import MatchingEngine

logger = structlog.get_logger(__name__)


class MatchingService:
    """Service for handling matching operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def match_resume_to_jobs(self, resume_id: str, student_id: str) -> List[Match]:
        """
        Find matching jobs for a resume.
        """
        logger.info("Matching resume to jobs", resume_id=resume_id)

        # Get resume data
        resume = await self.get_resume_by_id(resume_id)
        if not resume:
            raise ValueError("Resume not found")

        # Get all active jobs
        stmt = select(Job).where(Job.status == "active")
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()

        if not jobs:
            return []

        # Convert to dict format for matching engine
        resume_data = {
            "id": resume.id,
            "user_id": resume.user_id,
            "extracted_skills": resume.extracted_skills,
            "experience": resume.experience,
            "embedding_vector": resume.embedding_vector,
        }

        jobs_data = [{
            "id": job.id,
            "recruiter_id": job.recruiter_id,
            "required_skills": job.required_skills,
            "experience_level": job.experience_level,
            "embedding_vector": job.embedding_vector,
        } for job in jobs]

        # Calculate matches
        match_results = await MatchingEngine.batch_calculate_matches([resume_data], jobs_data)

        # Convert to Match objects and store
        matches = []
        for result in match_results:
            match = Match(
                id=str(uuid.uuid4()),
                resume_id=result.resume_id,
                job_id=result.job_id,
                student_id=result.student_id,
                recruiter_id=result.recruiter_id,
                overall_score=result.overall_score,
                skill_score=result.skill_score,
                experience_score=result.experience_score,
                semantic_score=result.semantic_score,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
                explanation=result.explanation,
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(match)
            matches.append(match)

        await self.db.commit()

        logger.info("Resume matching completed", matches_found=len(matches))
        return matches

    async def match_job_to_candidates(self, job_id: str, recruiter_id: str) -> List[Match]:
        """
        Find matching candidates for a job.
        """
        logger.info("Matching job to candidates", job_id=job_id)

        # Get job data
        job = await self.get_job_by_id(job_id)
        if not job:
            raise ValueError("Job not found")

        # Get all resumes
        stmt = select(Resume).where(Resume.status == "completed")
        result = await self.db.execute(stmt)
        resumes = result.scalars().all()

        if not resumes:
            return []

        # Convert to dict format for matching engine
        job_data = {
            "id": job.id,
            "recruiter_id": job.recruiter_id,
            "required_skills": job.required_skills,
            "experience_level": job.experience_level,
            "embedding_vector": job.embedding_vector,
        }

        resumes_data = [{
            "id": resume.id,
            "user_id": resume.user_id,
            "extracted_skills": resume.extracted_skills,
            "experience": resume.experience,
            "embedding_vector": resume.embedding_vector,
        } for resume in resumes]

        # Calculate matches
        match_results = await MatchingEngine.batch_calculate_matches(resumes_data, [job_data])

        # Convert to Match objects and store
        matches = []
        for result in match_results:
            match = Match(
                id=str(uuid.uuid4()),
                resume_id=result.resume_id,
                job_id=result.job_id,
                student_id=result.student_id,
                recruiter_id=result.recruiter_id,
                overall_score=result.overall_score,
                skill_score=result.skill_score,
                experience_score=result.experience_score,
                semantic_score=result.semantic_score,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
                explanation=result.explanation,
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(match)
            matches.append(match)

        await self.db.commit()

        logger.info("Job matching completed", matches_found=len(matches))
        return matches

    async def get_matches_by_student(self, student_id: str) -> List[Match]:
        """
        Get all matches for a student.
        """
        stmt = select(Match).where(Match.student_id == student_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_matches_by_recruiter(self, recruiter_id: str) -> List[Match]:
        """
        Get all matches for a recruiter's jobs.
        """
        stmt = select(Match).where(Match.recruiter_id == recruiter_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_matches_by_job(self, job_id: str) -> List[Match]:
        """
        Get all matches for a specific job.
        """
        stmt = select(Match).where(Match.job_id == job_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_match_by_id(self, match_id: str) -> Optional[Match]:
        """
        Get match by ID.
        """
        stmt = select(Match).where(Match.id == match_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_match_status(self, match_id: str, status: str) -> Optional[Match]:
        """
        Update match status.
        """
        match = await self.get_match_by_id(match_id)
        if not match:
            return None

        match.status = status
        match.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(match)

        return match

    async def get_resume_by_id(self, resume_id: str) -> Optional[Resume]:
        """
        Get resume by ID.
        """
        stmt = select(Resume).where(Resume.id == resume_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.
        """
        stmt = select(Job).where(Job.id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
