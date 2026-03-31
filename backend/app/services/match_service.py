"""
Match service layer for business logic.
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_
from sqlalchemy import text as sql_text

from ..db.models import Match, Resume, Job, User
from ..schemas.match import MatchCreate, MatchUpdate, MatchFilters
from ..pipeline.matching import matching_engine

logger = logging.getLogger(__name__)


class MatchService:
    """Service for match-related operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def find_similar_jobs(
        self,
        resume_embedding: list[float],
        limit: int = 20,
        min_similarity: float = 0.3,
    ) -> list[dict]:
        """
        Find jobs semantically similar to a resume using pgvector
        cosine similarity search.

        Uses IVFFlat index for sub-second search over large job pools.
        Only returns active jobs above the minimum similarity threshold.

        Args:
            resume_embedding: 384-dimensional embedding vector
            limit: Maximum number of jobs to return
            min_similarity: Minimum cosine similarity (0.0 to 1.0)

        Returns:
            List of dicts with job_id and similarity_score, ranked
            by similarity descending.
        """
        # pgvector cosine distance operator: <=>
        # cosine similarity = 1 - cosine distance
        result = await self.db.execute(
            sql_text("""
                SELECT
                    id::text as job_id,
                    title,
                    company,
                    1 - (job_embedding_vector <=> :embedding) as similarity
                FROM jobs
                WHERE
                    status = 'active'
                    AND job_embedding_vector IS NOT NULL
                    AND 1 - (job_embedding_vector <=> :embedding) >= :min_sim
                ORDER BY job_embedding_vector <=> :embedding
                LIMIT :limit
            """).bindparams(
                embedding=str(resume_embedding),
                min_sim=min_similarity,
                limit=limit,
            )
        )

        rows = result.mappings().all()
        return [
            {
                "job_id": row["job_id"],
                "title": row["title"],
                "company": row["company"],
                "similarity_score": float(row["similarity"]),
            }
            for row in rows
        ]

    async def create_match(self, match_data: MatchCreate) -> Optional[Match]:
        """Create a new match record."""
        try:
            # Validate that resume and job exist
            resume = await self._get_resume_by_id(match_data.resume_id)
            job = await self._get_job_by_id(match_data.job_id)

            if not resume or not job:
                return None

            # Validate student and recruiter
            student = await self._get_user_by_id(match_data.student_id)
            recruiter = await self._get_user_by_id(match_data.recruiter_id)

            if not student or not recruiter:
                return None

            if student.role != "student" or recruiter.role != "recruiter":
                return None

            # Create match
            match = Match(
                resume_id=match_data.resume_id,
                job_id=match_data.job_id,
                student_id=match_data.student_id,
                recruiter_id=match_data.recruiter_id,
                overall_score=match_data.overall_score,
                skill_score=match_data.skill_score,
                experience_score=match_data.experience_score,
                semantic_score=match_data.semantic_score,
                matched_skills=match_data.matched_skills,
                missing_skills=match_data.missing_skills,
                explanation=match_data.explanation.dict()
            )

            self.db.add(match)
            await self.db.commit()
            await self.db.refresh(match)

            logger.info(f"Created match: {match.id}")
            return match

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating match: {e}")
            return None

    async def match_resume_to_jobs(self, resume_id: UUID) -> List[Match]:
        """Find and create matches between a resume and all available jobs."""
        try:
            # Get resume data
            resume = await self._get_resume_by_id(resume_id)
            if not resume:
                return []

            # Get all active jobs
            jobs = await self._get_all_active_jobs()
            if not jobs:
                return []

            # Convert to dict format for matching engine
            resume_data = {
                'id': str(resume.id),
                'user_id': str(resume.user_id),
                'extracted_text': resume.extracted_text or '',
                'extracted_skills': resume.extracted_skills or []
            }

            job_data_list = [{
                'id': str(job.id),
                'recruiter_id': str(job.recruiter_id),
                'title': job.title,
                'description': job.description,
                'required_skills': job.required_skills or [],
                'preferred_skills': job.preferred_skills or [],
                'experience_level': job.experience_level
            } for job in jobs]

            # Perform matching
            match_results = await matching_engine.match_resume_to_jobs(resume_data, job_data_list)

            # Create match records
            created_matches = []
            for result in match_results:
                match_data = MatchCreate(
                    resume_id=UUID(result['resume_id']),
                    job_id=UUID(result['job_id']),
                    student_id=UUID(result['student_id']),
                    recruiter_id=UUID(result['recruiter_id']),
                    overall_score=result['overall_score'],
                    skill_score=result['skill_score'],
                    experience_score=result['experience_score'],
                    semantic_score=result['semantic_score'],
                    matched_skills=result['matched_skills'],
                    missing_skills=result['missing_skills'],
                    explanation=result['explanation']
                )

                match = await self.create_match(match_data)
                if match:
                    created_matches.append(match)

            logger.info(f"Created {len(created_matches)} matches for resume {resume_id}")
            return created_matches

        except Exception as e:
            logger.error(f"Error matching resume {resume_id} to jobs: {e}")
            return []

    async def match_job_to_candidates(self, job_id: UUID) -> List[Match]:
        """Find and create matches between a job and all available resumes."""
        try:
            # Get job data
            job = await self._get_job_by_id(job_id)
            if not job:
                return []

            # Get all resumes
            resumes = await self._get_all_resumes()
            if not resumes:
                return []

            # Convert to dict format for matching engine
            job_data = {
                'id': str(job.id),
                'recruiter_id': str(job.recruiter_id),
                'title': job.title,
                'description': job.description,
                'required_skills': job.required_skills or [],
                'preferred_skills': job.preferred_skills or [],
                'experience_level': job.experience_level
            }

            resume_data_list = [{
                'id': str(resume.id),
                'user_id': str(resume.user_id),
                'extracted_text': resume.extracted_text or '',
                'extracted_skills': resume.extracted_skills or []
            } for resume in resumes]

            # Perform matching
            match_results = await matching_engine.match_job_to_resumes(job_data, resume_data_list)

            # Create match records
            created_matches = []
            for result in match_results:
                match_data = MatchCreate(
                    resume_id=UUID(result['resume_id']),
                    job_id=UUID(result['job_id']),
                    student_id=UUID(result['student_id']),
                    recruiter_id=UUID(result['recruiter_id']),
                    overall_score=result['overall_score'],
                    skill_score=result['skill_score'],
                    experience_score=result['experience_score'],
                    semantic_score=result['semantic_score'],
                    matched_skills=result['matched_skills'],
                    missing_skills=result['missing_skills'],
                    explanation=result['explanation']
                )

                match = await self.create_match(match_data)
                if match:
                    created_matches.append(match)

            logger.info(f"Created {len(created_matches)} matches for job {job_id}")
            return created_matches

        except Exception as e:
            logger.error(f"Error matching job {job_id} to candidates: {e}")
            return []

    async def get_match_by_id(self, match_id: UUID) -> Optional[Match]:
        """Get match by ID."""
        try:
            result = await self.db.execute(
                select(Match).where(Match.id == match_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting match by ID {match_id}: {e}")
            return None

    async def get_matches_by_student(self, student_id: UUID) -> List[Match]:
        """Get all matches for a student."""
        try:
            result = await self.db.execute(
                select(Match).where(Match.student_id == student_id)
                .order_by(desc(Match.overall_score))
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting matches for student {student_id}: {e}")
            return []

    async def get_matches_by_recruiter(self, recruiter_id: UUID) -> List[Match]:
        """Get all matches for a recruiter's jobs."""
        try:
            result = await self.db.execute(
                select(Match).where(Match.recruiter_id == recruiter_id)
                .order_by(desc(Match.overall_score))
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting matches for recruiter {recruiter_id}: {e}")
            return []

    async def get_matches_by_job(self, job_id: UUID) -> List[Match]:
        """Get all matches for a specific job."""
        try:
            result = await self.db.execute(
                select(Match).where(Match.job_id == job_id)
                .order_by(desc(Match.overall_score))
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting matches for job {job_id}: {e}")
            return []

    async def update_match_status(self, match_id: UUID, status: str) -> Optional[Match]:
        """Update match status."""
        try:
            match = await self.get_match_by_id(match_id)
            if not match:
                return None

            match.status = status
            await self.db.commit()
            await self.db.refresh(match)

            logger.info(f"Updated match {match_id} status to {status}")
            return match

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating match {match_id} status: {e}")
            return None

    async def _get_resume_by_id(self, resume_id: UUID) -> Optional[Resume]:
        """Get resume by ID."""
        try:
            result = await self.db.execute(
                select(Resume).where(Resume.id == resume_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting resume by ID {resume_id}: {e}")
            return None

    async def _get_job_by_id(self, job_id: UUID) -> Optional[Job]:
        """Get job by ID."""
        try:
            result = await self.db.execute(
                select(Job).where(Job.id == job_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting job by ID {job_id}: {e}")
            return None

    async def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    async def _get_all_active_jobs(self) -> List[Job]:
        """Get all active jobs."""
        try:
            result = await self.db.execute(
                select(Job).where(Job.status == "active")
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all active jobs: {e}")
            return []

    async def _get_all_resumes(self) -> List[Resume]:
        """Get all resumes."""
        try:
            result = await self.db.execute(select(Resume))
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all resumes: {e}")
            return []
