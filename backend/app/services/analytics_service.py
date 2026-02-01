"""
Analytics service layer for business logic.
"""
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from collections import defaultdict, Counter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from ..db.models import Match, Job, Resume, User
from ..schemas.analytics import (
    MatchAnalytics, RecruiterDashboardStats, StudentDashboardStats, SkillFrequency
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics-related operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def get_student_dashboard_stats(self, student_id: UUID) -> Optional[StudentDashboardStats]:
        """Get dashboard statistics for a student."""
        try:
            # Get resume count
            resume_result = await self.db.execute(
                select(func.count(Resume.id)).where(Resume.user_id == student_id)
            )
            resumes_uploaded = resume_result.scalar() or 0

            # Get match statistics
            match_result = await self.db.execute(
                select(
                    func.count(Match.id),
                    func.avg(Match.overall_score)
                ).where(Match.student_id == student_id)
            )
            matches_found, avg_score = match_result.first()
            matches_found = matches_found or 0
            average_score = float(avg_score) if avg_score else 0.0

            # Get top matched roles (from job titles in matches)
            role_result = await self.db.execute(
                select(Job.title)
                .join(Match, Match.job_id == Job.id)
                .where(Match.student_id == student_id)
                .order_by(desc(Match.overall_score))
                .limit(10)
            )
            top_roles = [row[0] for row in role_result.fetchall()]
            # Remove duplicates while preserving order
            seen = set()
            top_matched_roles = [x for x in top_roles if not (x in seen or seen.add(x))][:5]

            return StudentDashboardStats(
                resumes_uploaded=resumes_uploaded,
                matches_found=matches_found,
                average_score=round(average_score, 2),
                top_matched_roles=top_matched_roles
            )

        except Exception as e:
            logger.error(f"Error getting student dashboard stats for {student_id}: {e}")
            return None

    async def get_recruiter_dashboard_stats(self, recruiter_id: UUID) -> Optional[RecruiterDashboardStats]:
        """Get dashboard statistics for a recruiter."""
        try:
            # Get active jobs count
            job_result = await self.db.execute(
                select(func.count(Job.id)).where(
                    (Job.recruiter_id == recruiter_id) & (Job.status == "active")
                )
            )
            active_jobs = job_result.scalar() or 0

            # Get total candidates (unique students who matched with recruiter's jobs)
            candidate_result = await self.db.execute(
                select(func.count(func.distinct(Match.student_id)))
                .join(Job, Match.job_id == Job.id)
                .where(Job.recruiter_id == recruiter_id)
            )
            total_candidates = candidate_result.scalar() or 0

            # Get shortlisted candidates
            shortlisted_result = await self.db.execute(
                select(func.count(func.distinct(Match.student_id)))
                .join(Job, Match.job_id == Job.id)
                .where(
                    (Job.recruiter_id == recruiter_id) &
                    (Match.status == "shortlisted")
                )
            )
            shortlisted_candidates = shortlisted_result.scalar() or 0

            # Get average match score
            score_result = await self.db.execute(
                select(func.avg(Match.overall_score))
                .join(Job, Match.job_id == Job.id)
                .where(Job.recruiter_id == recruiter_id)
            )
            avg_score = score_result.scalar()
            average_match_score = float(avg_score) if avg_score else 0.0

            return RecruiterDashboardStats(
                active_jobs=active_jobs,
                total_candidates=total_candidates,
                shortlisted_candidates=shortlisted_candidates,
                average_match_score=round(average_match_score, 2)
            )

        except Exception as e:
            logger.error(f"Error getting recruiter dashboard stats for {recruiter_id}: {e}")
            return None

    async def get_match_analytics(self, user_id: UUID, user_role: str) -> Optional[MatchAnalytics]:
        """Get comprehensive match analytics."""
        try:
            # Base query for matches
            if user_role == "student":
                match_query = select(Match).where(Match.student_id == user_id)
            elif user_role == "recruiter":
                match_query = select(Match).join(Job, Match.job_id == Job.id).where(Job.recruiter_id == user_id)
            else:
                return None

            # Get all matches
            result = await self.db.execute(match_query)
            matches = result.scalars().all()

            if not matches:
                return MatchAnalytics(
                    total_matches=0,
                    average_score=0.0,
                    score_distribution={"excellent": 0, "good": 0, "fair": 0, "poor": 0},
                    top_skills=[]
                )

            total_matches = len(matches)
            scores = [match.overall_score for match in matches]
            average_score = sum(scores) / len(scores)

            # Score distribution
            score_distribution = {
                "excellent": sum(1 for s in scores if s >= 0.8),
                "good": sum(1 for s in scores if 0.6 <= s < 0.8),
                "fair": sum(1 for s in scores if 0.4 <= s < 0.6),
                "poor": sum(1 for s in scores if s < 0.4)
            }

            # Top skills analysis
            all_matched_skills = []
            for match in matches:
                if match.matched_skills:
                    all_matched_skills.extend(match.matched_skills)

            skill_counts = Counter(all_matched_skills)
            top_skills = [
                SkillFrequency(skill=skill, frequency=count)
                for skill, count in skill_counts.most_common(10)
            ]

            return MatchAnalytics(
                total_matches=total_matches,
                average_score=round(average_score, 2),
                score_distribution=score_distribution,
                top_skills=top_skills
            )

        except Exception as e:
            logger.error(f"Error getting match analytics for {user_id}: {e}")
            return None
