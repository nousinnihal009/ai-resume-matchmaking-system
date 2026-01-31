"""
Analytics service for generating dashboard statistics.
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from app.db.models import User, Resume, Job, Match

logger = structlog.get_logger(__name__)


class AnalyticsService:
    """Service for generating analytics data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_student_analytics(self, student_id: str) -> Dict[str, Any]:
        """
        Get analytics data for a student dashboard.
        """
        logger.info("Generating student analytics", student_id=student_id)

        # Count resumes uploaded
        stmt = select(func.count(Resume.id)).where(Resume.user_id == student_id)
        result = await self.db.execute(stmt)
        resumes_uploaded = result.scalar() or 0

        # Count matches found
        stmt = select(func.count(Match.id)).where(Match.student_id == student_id)
        result = await self.db.execute(stmt)
        matches_found = result.scalar() or 0

        # Calculate average match score
        stmt = select(func.avg(Match.overall_score)).where(Match.student_id == student_id)
        result = await self.db.execute(stmt)
        avg_score = result.scalar() or 0.0

        # Get top matched roles
        stmt = (
            select(Job.title, func.count(Match.id).label("match_count"))
            .select_from(Match)
            .join(Job, Match.job_id == Job.id)
            .where(Match.student_id == student_id)
            .group_by(Job.title)
            .order_by(func.count(Match.id).desc())
            .limit(5)
        )
        result = await self.db.execute(stmt)
        top_roles = [row[0] for row in result.fetchall()]

        return {
            "resumes_uploaded": resumes_uploaded,
            "matches_found": matches_found,
            "average_score": float(avg_score),
            "top_matched_roles": top_roles,
        }

    async def get_recruiter_analytics(self, recruiter_id: str) -> Dict[str, Any]:
        """
        Get analytics data for a recruiter dashboard.
        """
        logger.info("Generating recruiter analytics", recruiter_id=recruiter_id)

        # Count active jobs
        stmt = select(func.count(Job.id)).where(
            Job.recruiter_id == recruiter_id,
            Job.status == "active"
        )
        result = await self.db.execute(stmt)
        active_jobs = result.scalar() or 0

        # Count total candidates (unique students who matched with recruiter's jobs)
        stmt = select(func.count(func.distinct(Match.student_id))).where(
            Match.recruiter_id == recruiter_id
        )
        result = await self.db.execute(stmt)
        total_candidates = result.scalar() or 0

        # Count shortlisted candidates
        stmt = select(func.count(Match.id)).where(
            Match.recruiter_id == recruiter_id,
            Match.status == "shortlisted"
        )
        result = await self.db.execute(stmt)
        shortlisted_candidates = result.scalar() or 0

        # Calculate average match score for recruiter's jobs
        stmt = select(func.avg(Match.overall_score)).where(
            Match.recruiter_id == recruiter_id
        )
        result = await self.db.execute(stmt)
        avg_score = result.scalar() or 0.0

        return {
            "active_jobs": active_jobs,
            "total_candidates": total_candidates,
            "shortlisted_candidates": shortlisted_candidates,
            "average_match_score": float(avg_score),
        }
