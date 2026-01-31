"""
Matching engine for calculating job-resume compatibility scores.
"""
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import structlog

from .skill_extraction import calculate_skill_match
from .embeddings import calculate_cosine_similarity

logger = structlog.get_logger(__name__)


@dataclass
class MatchResult:
    """Result of a single match calculation."""
    resume_id: str
    job_id: str
    student_id: str
    recruiter_id: str
    overall_score: float
    skill_score: float
    experience_score: float
    semantic_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: Dict[str, Any]


class MatchingEngine:
    """Engine for calculating match scores between resumes and jobs."""

    @staticmethod
    async def calculate_match_score(
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> MatchResult:
        """
        Calculate comprehensive match score between a resume and job.

        Args:
            resume_data: Resume information including skills, experience, embedding
            job_data: Job information including requirements, embedding

        Returns:
            MatchResult with detailed scoring
        """
        logger.info(
            "Calculating match score",
            resume_id=resume_data.get("id"),
            job_id=job_data.get("id")
        )

        # Extract data
        resume_skills = resume_data.get("extracted_skills", [])
        job_skills = job_data.get("required_skills", [])
        resume_embedding = resume_data.get("embedding_vector", [])
        job_embedding = job_data.get("embedding_vector", [])
        resume_experience = resume_data.get("experience", [])
        job_level = job_data.get("experience_level", "entry")

        # Calculate skill score
        skill_match = calculate_skill_match(resume_skills, job_skills)
        skill_score = skill_match["match_score"]

        # Calculate semantic score (embedding similarity)
        semantic_score = 0.0
        if resume_embedding and job_embedding:
            semantic_score = await calculate_cosine_similarity(
                resume_embedding, job_embedding
            )

        # Calculate experience score
        experience_score = _calculate_experience_score(resume_experience, job_level)

        # Calculate overall score (weighted combination)
        overall_score = _calculate_overall_score(
            skill_score, semantic_score, experience_score
        )

        # Generate explanation
        explanation = _generate_match_explanation(
            skill_match, semantic_score, experience_score, overall_score
        )

        return MatchResult(
            resume_id=resume_data["id"],
            job_id=job_data["id"],
            student_id=resume_data["user_id"],
            recruiter_id=job_data["recruiter_id"],
            overall_score=overall_score,
            skill_score=skill_score,
            experience_score=experience_score,
            semantic_score=semantic_score,
            matched_skills=skill_match["matched"],
            missing_skills=skill_match["missing"],
            explanation=explanation,
        )

    @staticmethod
    async def batch_calculate_matches(
        resumes: List[Dict[str, Any]],
        jobs: List[Dict[str, Any]]
    ) -> List[MatchResult]:
        """
        Calculate match scores for multiple resume-job pairs.

        Args:
            resumes: List of resume data
            jobs: List of job data

        Returns:
            List of match results
        """
        logger.info(
            "Calculating batch matches",
            resume_count=len(resumes),
            job_count=len(jobs)
        )

        results = []

        for resume in resumes:
            for job in jobs:
                try:
                    result = await MatchingEngine.calculate_match_score(resume, job)
                    results.append(result)
                except Exception as e:
                    logger.error(
                        "Failed to calculate match",
                        resume_id=resume.get("id"),
                        job_id=job.get("id"),
                        error=str(e)
                    )

        # Sort by overall score (descending)
        results.sort(key=lambda x: x.overall_score, reverse=True)

        logger.info("Batch matching completed", total_matches=len(results))
        return results


def _calculate_experience_score(resume_experience: List[Dict], job_level: str) -> float:
    """
    Calculate experience compatibility score.

    Args:
        resume_experience: List of experience entries
        job_level: Required experience level

    Returns:
        Experience score (0-1)
    """
    if not resume_experience:
        return 0.0

    # Map job levels to years of experience
    level_requirements = {
        "internship": 0,
        "entry": 0,
        "mid": 2,
        "senior": 5,
    }

    required_years = level_requirements.get(job_level, 0)

    # Calculate total years of experience
    total_years = 0
    for exp in resume_experience:
        # Simple calculation - can be enhanced with date parsing
        duration = exp.get("duration_years", 0)
        total_years += duration

    # Score based on meeting requirements
    if total_years >= required_years:
        if total_years >= required_years + 3:  # Overqualified
            return 0.9
        return 1.0
    elif total_years >= required_years * 0.5:  # Partial match
        return 0.6
    else:
        return 0.2


def _calculate_overall_score(
    skill_score: float,
    semantic_score: float,
    experience_score: float
) -> float:
    """
    Calculate weighted overall score.

    Weights:
    - Skills: 40%
    - Semantic similarity: 35%
    - Experience: 25%
    """
    return (
        skill_score * 0.4 +
        semantic_score * 0.35 +
        experience_score * 0.25
    )


def _generate_match_explanation(
    skill_match: Dict,
    semantic_score: float,
    experience_score: float,
    overall_score: float
) -> Dict[str, Any]:
    """
    Generate human-readable explanation for the match.
    """
    # Determine match quality
    if overall_score >= 0.8:
        quality = "excellent"
        summary = "Excellent match! Strong alignment across all criteria."
    elif overall_score >= 0.6:
        quality = "good"
        summary = "Good match with solid qualifications."
    elif overall_score >= 0.4:
        quality = "moderate"
        summary = "Moderate match with some alignment."
    else:
        quality = "poor"
        summary = "Limited match, significant gaps present."

    # Generate strengths
    strengths = []
    if skill_match["match_score"] >= 0.7:
        strengths.append("Strong skill alignment")
    if semantic_score >= 0.7:
        strengths.append("High semantic similarity")
    if experience_score >= 0.8:
        strengths.append("Excellent experience match")

    # Generate gaps
    gaps = []
    if skill_match["missing"]:
        gaps.append(f"Missing {len(skill_match['missing'])} required skills")
    if semantic_score < 0.5:
        gaps.append("Limited semantic alignment")
    if experience_score < 0.5:
        gaps.append("Experience level mismatch")

    # Generate recommendations
    recommendations = []
    if skill_match["missing"]:
        recommendations.append(f"Consider learning: {', '.join(skill_match['missing'][:3])}")
    if experience_score < 0.7:
        recommendations.append("Gain more relevant experience")
    if semantic_score < 0.6:
        recommendations.append("Tailor resume to highlight relevant keywords")

    return {
        "summary": summary,
        "quality": quality,
        "strengths": strengths,
        "gaps": gaps,
        "recommendations": recommendations,
        "skill_breakdown": {
            "matched": skill_match["matched"],
            "missing": skill_match["missing"],
            "additional": skill_match["additional"],
        },
        "score_breakdown": {
            "skills": skill_match["match_score"],
            "semantic": semantic_score,
            "experience": experience_score,
            "overall": overall_score,
        },
    }
