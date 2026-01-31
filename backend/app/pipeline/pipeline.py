"""
ML Pipeline orchestrator for processing resumes and jobs.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

from .text_extraction import extract_text_from_file, extract_text_from_job_description
from .skill_extraction import extract_skills_from_resume, extract_skills_from_job
from .embeddings import generate_embedding

logger = structlog.get_logger(__name__)


class ProcessingResult:
    """Result of processing a document."""

    def __init__(
        self,
        status: str = "pending",
        resume_id: Optional[str] = None,
        job_id: Optional[str] = None,
        extracted_text: Optional[str] = None,
        skills: Optional[list] = None,
        education: Optional[list] = None,
        experience: Optional[list] = None,
        embedding: Optional[list] = None,
        error: Optional[str] = None,
    ):
        self.status = status
        self.resume_id = resume_id
        self.job_id = job_id
        self.extracted_text = extracted_text
        self.skills = skills or []
        self.education = education or []
        self.experience = experience or []
        self.embedding = embedding or []
        self.error = error


async def process_resume(
    file_content: bytes,
    filename: str,
    user_id: str
) -> ProcessingResult:
    """
    Process a resume file through the complete ML pipeline.

    Args:
        file_content: Raw file bytes
        filename: Original filename
        user_id: User ID who uploaded the resume

    Returns:
        ProcessingResult with extracted data
    """
    logger.info("Starting resume processing", filename=filename, user_id=user_id)

    result = ProcessingResult()
    result.resume_id = str(uuid.uuid4())

    try:
        # Step 1: Extract text from file
        logger.info("Extracting text from resume")
        extracted_text = await extract_text_from_file(file_content, filename)

        if not extracted_text:
            result.status = "failed"
            result.error = "No text could be extracted from the file"
            return result

        result.extracted_text = extracted_text

        # Step 2: Extract skills
        logger.info("Extracting skills from resume")
        skills = await extract_skills_from_resume(extracted_text)
        result.skills = skills

        # Step 3: Generate embedding
        logger.info("Generating embedding for resume")
        embedding = await generate_embedding(extracted_text)
        result.embedding = embedding

        # Step 4: Extract additional metadata (simplified)
        # In a full implementation, this would use more sophisticated NLP
        result.education = []  # Would extract education info
        result.experience = []  # Would extract experience info

        result.status = "completed"
        logger.info("Resume processing completed successfully", resume_id=result.resume_id)

    except Exception as e:
        logger.error("Resume processing failed", error=str(e), filename=filename)
        result.status = "failed"
        result.error = str(e)

    return result


async def process_job_description(job_data: Dict[str, Any]) -> ProcessingResult:
    """
    Process a job description through the ML pipeline.

    Args:
        job_data: Job data including title, description, skills

    Returns:
        ProcessingResult with extracted data
    """
    logger.info("Starting job processing", title=job_data.get("title"))

    result = ProcessingResult()
    result.job_id = str(uuid.uuid4())

    try:
        # Combine title and description for processing
        full_text = f"{job_data.get('title', '')} {job_data.get('description', '')}"

        # Step 1: Clean text
        logger.info("Cleaning job description text")
        cleaned_text = await extract_text_from_job_description(full_text)
        result.extracted_text = cleaned_text

        # Step 2: Extract skills (use provided skills or extract from text)
        provided_skills = job_data.get("requiredSkills", [])
        if provided_skills:
            result.skills = provided_skills
        else:
            logger.info("Extracting skills from job description")
            skills = await extract_skills_from_job(cleaned_text)
            result.skills = skills

        # Step 3: Generate embedding
        logger.info("Generating embedding for job")
        embedding = await generate_embedding(cleaned_text)
        result.embedding = embedding

        result.status = "completed"
        logger.info("Job processing completed successfully", job_id=result.job_id)

    except Exception as e:
        logger.error("Job processing failed", error=str(e), title=job_data.get("title"))
        result.status = "failed"
        result.error = str(e)

    return result


async def execute_resume_matching(
    resume_data: Dict[str, Any],
    jobs_data: list
) -> list:
    """
    Execute matching between a resume and multiple jobs.

    Args:
        resume_data: Resume data with skills, embedding, etc.
        jobs_data: List of job data

    Returns:
        List of match results
    """
    from .matching_engine import MatchingEngine

    logger.info(
        "Executing resume-job matching",
        resume_id=resume_data.get("id"),
        job_count=len(jobs_data)
    )

    return await MatchingEngine.batch_calculate_matches([resume_data], jobs_data)


async def execute_job_matching(
    job_data: Dict[str, Any],
    resumes_data: list
) -> list:
    """
    Execute matching between a job and multiple resumes.

    Args:
        job_data: Job data with skills, embedding, etc.
        resumes_data: List of resume data

    Returns:
        List of match results
    """
    from .matching_engine import MatchingEngine

    logger.info(
        "Executing job-resume matching",
        job_id=job_data.get("id"),
        resume_count=len(resumes_data)
    )

    return await MatchingEngine.batch_calculate_matches(resumes_data, [job_data])
