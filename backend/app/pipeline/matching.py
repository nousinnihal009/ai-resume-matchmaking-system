"""
Matching pipeline for resume-job matching.

Upgraded to use real sentence-transformers embeddings for semantic
similarity scoring. Weights: 50% semantic / 30% skill / 20% experience.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from .embeddings import embedding_service
from .skill_extraction import skill_extractor
from app.core.model_manager import cosine_similarity, encode_text

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Engine for matching resumes to jobs using multiple scoring methods."""

    def __init__(self):
        """Initialize the matching engine."""
        self.skill_weights = {
            'required': 0.6,
            'preferred': 0.3,
            'bonus': 0.1
        }

    async def match_resume_to_jobs(
        self,
        resume_data: Dict[str, Any],
        job_data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match a single resume against multiple jobs.

        Args:
            resume_data: Resume data with skills, experience, etc.
            job_data_list: List of job data dictionaries

        Returns:
            List of match results sorted by overall score
        """
        try:
            matches = []

            for job_data in job_data_list:
                match_result = await self._calculate_match_score(resume_data, job_data)
                matches.append(match_result)

            # Sort by overall score (descending)
            matches.sort(key=lambda x: x['overall_score'], reverse=True)

            return matches

        except Exception as e:
            logger.error(f"Error matching resume to jobs: {e}")
            return []

    async def match_job_to_resumes(
        self,
        job_data: Dict[str, Any],
        resume_data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match a single job against multiple resumes.

        Args:
            job_data: Job data with requirements, etc.
            resume_data_list: List of resume data dictionaries

        Returns:
            List of match results sorted by overall score
        """
        try:
            matches = []

            for resume_data in resume_data_list:
                match_result = await self._calculate_match_score(resume_data, job_data)
                matches.append(match_result)

            # Sort by overall score (descending)
            matches.sort(key=lambda x: x['overall_score'], reverse=True)

            return matches

        except Exception as e:
            logger.error(f"Error matching job to resumes: {e}")
            return []

    async def _calculate_match_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score between resume and job.

        Scoring weights (upgraded):
          50% — Semantic similarity (sentence-transformers cosine sim)
          30% — Skill overlap (matched skills / required skills)
          20% — Experience fit (level-based scoring)

        Returns the exact same shape as the previous implementation
        to maintain backward compatibility with all callers.
        """
        try:
            # Extract skills from resume and job
            resume_skills = set(resume_data.get('extracted_skills', []))
            job_required = set(job_data.get('required_skills', []))
            job_preferred = set(job_data.get('preferred_skills', []))

            # Calculate skill-based scores
            skill_score, matched_skills, missing_skills = self._calculate_skill_score(
                resume_skills, job_required, job_preferred
            )

            # Calculate experience score
            experience_score = self._calculate_experience_score(
                resume_data, job_data
            )

            # Calculate semantic similarity score using REAL embeddings
            semantic_score = await self._calculate_semantic_score(
                resume_data, job_data
            )

            # Calculate overall score with NEW weights:
            # 50% semantic + 30% skill + 20% experience
            overall_score = (
                semantic_score * 0.5 +
                skill_score * 0.3 +
                experience_score * 0.2
            )

            # Generate explanation
            explanation = self._generate_explanation(
                skill_score, experience_score, semantic_score,
                matched_skills, missing_skills, resume_data, job_data
            )

            return {
                'resume_id': resume_data.get('id'),
                'job_id': job_data.get('id'),
                'student_id': resume_data.get('user_id'),
                'recruiter_id': job_data.get('recruiter_id'),
                'overall_score': round(overall_score, 4),
                'skill_score': round(skill_score, 4),
                'experience_score': round(experience_score, 4),
                'semantic_score': round(semantic_score, 4),
                'matched_skills': list(matched_skills),
                'missing_skills': list(missing_skills),
                'explanation': explanation
            }

        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return self._create_empty_match_result(resume_data, job_data)

    def _calculate_skill_score(
        self,
        resume_skills: set,
        job_required: set,
        job_preferred: set
    ) -> Tuple[float, set, set]:
        """
        Calculate skill-based matching score.

        Returns:
            Tuple of (score, matched_skills, missing_skills)
        """
        try:
            # Find matched and missing skills
            matched_required = resume_skills & job_required
            matched_preferred = resume_skills & job_preferred
            missing_required = job_required - resume_skills
            missing_preferred = job_preferred - resume_skills

            # Calculate score components
            required_score = len(matched_required) / len(job_required) if job_required else 1.0
            preferred_score = len(matched_preferred) / len(job_preferred) if job_preferred else 1.0

            # Weighted overall skill score
            overall_skill_score = (
                required_score * self.skill_weights['required'] +
                preferred_score * self.skill_weights['preferred']
            )

            # Bonus for having additional relevant skills
            all_job_skills = job_required | job_preferred
            additional_skills = resume_skills - all_job_skills
            if additional_skills:
                overall_skill_score = min(1.0, overall_skill_score + self.skill_weights['bonus'])

            matched_skills = matched_required | matched_preferred
            missing_skills = missing_required | missing_preferred

            return overall_skill_score, matched_skills, missing_skills

        except Exception as e:
            logger.error(f"Error calculating skill score: {e}")
            return 0.0, set(), set()

    def _calculate_experience_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """
        Calculate experience-based matching score.
        This is a placeholder - real implementation would analyze work experience.
        """
        try:
            job_level = job_data.get('experience_level', 'entry')
            level_scores = {
                'internship': 0.2,
                'entry': 0.4,
                'mid': 0.7,
                'senior': 0.9
            }

            # Placeholder: assume moderate experience match
            base_score = level_scores.get(job_level, 0.5)

            return min(1.0, base_score)

        except Exception as e:
            logger.error(f"Error calculating experience score: {e}")
            return 0.5

    async def _calculate_semantic_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """
        Calculate semantic similarity score using real sentence-transformers
        embeddings.

        Uses pre-computed embeddings if available in the data dict,
        otherwise generates them on the fly via model_manager.
        """
        try:
            # Check for pre-computed embeddings first
            resume_vec = resume_data.get('embedding_vector', None)
            job_vec = job_data.get('job_embedding_vector', None)

            if resume_vec and job_vec:
                # Use pre-computed vectors directly
                return cosine_similarity(resume_vec, job_vec)

            # Fall back to generating from text
            resume_text = resume_data.get('extracted_text', '')
            job_text = job_data.get('description', '')

            if not resume_text or not job_text:
                return 0.0

            # Generate real embeddings via sentence-transformers
            resume_embedding = encode_text(resume_text)
            job_embedding = encode_text(job_text)

            if not resume_embedding or not job_embedding:
                return 0.0

            return cosine_similarity(resume_embedding, job_embedding)

        except Exception as e:
            logger.error(f"Error calculating semantic score: {e}")
            return 0.0

    def _generate_explanation(
        self,
        skill_score: float,
        experience_score: float,
        semantic_score: float,
        matched_skills: set,
        missing_skills: set,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate human-readable explanation for the match.
        """
        try:
            # Determine overall assessment using NEW weights
            overall_score = (semantic_score * 0.5 + skill_score * 0.3 + experience_score * 0.2)

            if overall_score >= 0.8:
                summary = "Excellent match! Strong alignment across all criteria."
            elif overall_score >= 0.6:
                summary = "Good match with solid potential."
            elif overall_score >= 0.4:
                summary = "Moderate match with some gaps to address."
            else:
                summary = "Limited match requiring significant development."

            # Generate strengths
            strengths = []
            if skill_score >= 0.7:
                strengths.append("Strong skill alignment")
            if experience_score >= 0.7:
                strengths.append("Good experience level match")
            if semantic_score >= 0.7:
                strengths.append("High semantic similarity")
            if matched_skills:
                strengths.append(f"Matches {len(matched_skills)} key skills")

            # Generate gaps
            gaps = []
            if skill_score < 0.5:
                gaps.append("Skill gaps present")
            if experience_score < 0.5:
                gaps.append("Experience level mismatch")
            if semantic_score < 0.5:
                gaps.append("Limited content alignment")
            if missing_skills:
                gaps.append(f"Missing {len(missing_skills)} required skills")

            # Generate recommendations
            recommendations = []
            if missing_skills:
                recommendations.append(f"Consider learning: {', '.join(list(missing_skills)[:3])}")
            if skill_score < 0.7:
                recommendations.append("Focus on building core technical skills")
            if experience_score < 0.7:
                recommendations.append("Gain more relevant experience")

            # Skill breakdown
            skill_breakdown = {
                'matched': list(matched_skills),
                'missing': list(missing_skills),
                'additional': []  # Could be populated with resume skills not required by job
            }

            return {
                'summary': summary,
                'strengths': strengths,
                'gaps': gaps,
                'recommendations': recommendations,
                'skill_breakdown': skill_breakdown
            }

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return {
                'summary': 'Unable to generate detailed explanation',
                'strengths': [],
                'gaps': [],
                'recommendations': [],
                'skill_breakdown': {'matched': [], 'missing': [], 'additional': []}
            }

    def _create_empty_match_result(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an empty match result for error cases."""
        return {
            'resume_id': resume_data.get('id'),
            'job_id': job_data.get('id'),
            'student_id': resume_data.get('user_id'),
            'recruiter_id': job_data.get('recruiter_id'),
            'overall_score': 0.0,
            'skill_score': 0.0,
            'experience_score': 0.0,
            'semantic_score': 0.0,
            'matched_skills': [],
            'missing_skills': [],
            'explanation': {
                'summary': 'Match calculation failed',
                'strengths': [],
                'gaps': [],
                'recommendations': [],
                'skill_breakdown': {'matched': [], 'missing': [], 'additional': []}
            }
        }


# Global matching engine instance
matching_engine = MatchingEngine()
