"""
Resume analysis API endpoints.

Endpoints:
  POST /resume-analysis/{resume_id}/analyze
       Trigger full comprehensive analysis. Returns immediately
       with cached result if analysis already exists.

  GET  /resume-analysis/{resume_id}/report
       Retrieve stored analysis report. 404 if not yet analyzed.

  POST /resume-analysis/{resume_id}/tailor
       Generate job-specific tailoring suggestions.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models import Resume
from app.schemas.base import APIResponse
from app.schemas.user import UserBase
from app.core.logging_config import get_logger
from app.pipeline.resume_analyzer import (
    analyze_resume_comprehensive,
    tailor_resume_for_job,
)

router = APIRouter()
logger = get_logger(__name__)


async def _get_resume_or_raise(
    resume_id: str,
    current_user: UserBase,
    db: AsyncSession,
) -> Resume:
    """Fetch resume and verify access rights."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    if (current_user.role == "student" and
            str(resume.user_id) != str(current_user.id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )
    return resume


@router.post(
    "/{resume_id}/analyze",
    response_model=APIResponse,
    summary="Run comprehensive resume analysis",
    description=(
        "Analyzes resume across 6 dimensions: content quality, "
        "sections, ATS essentials, design, skills, and tailoring. "
        "Returns cached result if analysis was run within 24 hours."
    ),
    operation_id="analyze_resume_comprehensive",
)
async def run_comprehensive_analysis(
    resume_id: str,
    force_refresh: bool = False,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger comprehensive resume analysis.
    Set force_refresh=true to re-run even if cached result exists.
    """
    resume = await _get_resume_or_raise(resume_id, current_user, db)

    if not resume.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume has not been processed yet. "
                   "Wait for the processing status to show 'completed'.",
        )

    # Return cached analysis if recent and not forcing refresh
    if (resume.full_analysis_report
            and resume.analysis_completed_at
            and not force_refresh):
        logger.info(
            "resume_analysis_cache_hit",
            resume_id=resume_id,
        )
        return APIResponse(
            success=True,
            data=resume.full_analysis_report,
            message="Returning cached analysis.",
        )

    logger.info(
        "resume_analysis_started",
        resume_id=resume_id,
        user_id=str(current_user.id),
    )

    # Run full analysis
    report = await analyze_resume_comprehensive(
        resume_text=resume.extracted_text,
        file_name=getattr(resume, 'file_name', '') or '',
        file_size_bytes=getattr(resume, 'file_size', 0) or 0,
    )

    # Persist results
    resume.analysis_score = report.get("overall_score")
    resume.analysis_score_breakdown = report.get("score_breakdown")
    resume.ats_parse_rate = report.get("content", {}).get(
        "ats_parse_rate"
    )
    resume.repetition_issues = report.get(
        "content", {}
    ).get("repetition", {}).get("issues", [])
    resume.spelling_issues = report.get(
        "content", {}
    ).get("spelling_grammar", {}).get("spelling_errors", [])
    resume.grammar_issues = report.get(
        "content", {}
    ).get("spelling_grammar", {}).get("grammar_errors", [])
    resume.missing_sections = report.get(
        "sections", {}
    ).get("missing", [])
    resume.present_sections = report.get(
        "sections", {}
    ).get("present", [])
    resume.contact_info = report.get(
        "ats_essentials", {}
    ).get("contact_info", {})
    resume.file_analysis = report.get(
        "ats_essentials", {}
    ).get("file_analysis", {})
    resume.design_score = report.get("design", {}).get("score")
    resume.design_feedback = report.get("design", {}).get("feedback", [])
    resume.template_suggestions = report.get(
        "design", {}
    ).get("template_suggestions", [])
    resume.full_analysis_report = report
    resume.analysis_completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(resume)

    logger.info(
        "resume_analysis_complete",
        resume_id=resume_id,
        score=report.get("overall_score"),
    )

    return APIResponse(
        success=True,
        data=report,
        message=f"Analysis complete. Score: {report.get('overall_score')}/100",
    )


@router.get(
    "/{resume_id}/report",
    response_model=APIResponse,
    summary="Get stored resume analysis report",
    operation_id="get_resume_analysis_report",
)
async def get_analysis_report(
    resume_id: str,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve stored analysis. Run /analyze first."""
    resume = await _get_resume_or_raise(resume_id, current_user, db)

    if not resume.full_analysis_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis found. "
                   f"Run POST /resume-analysis/{resume_id}/analyze first.",
        )

    return APIResponse(
        success=True,
        data=resume.full_analysis_report,
    )


@router.post(
    "/{resume_id}/tailor",
    response_model=APIResponse,
    summary="Tailor resume for a specific job description",
    description=(
        "Analyzes how well the resume matches a job description "
        "and provides specific rewrite suggestions, missing keywords, "
        "and a tailored professional summary."
    ),
    operation_id="tailor_resume_for_job_endpoint",
)
async def tailor_resume(
    resume_id: str,
    job_description: str = Body(..., embed=True, min_length=50),
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate job-specific tailoring suggestions."""
    resume = await _get_resume_or_raise(resume_id, current_user, db)

    if not resume.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume must be processed before tailoring.",
        )

    logger.info(
        "resume_tailoring_started",
        resume_id=resume_id,
        jd_length=len(job_description),
    )

    tailoring = await tailor_resume_for_job(
        resume_text=resume.extracted_text,
        job_description=job_description,
        resume_analysis=resume.full_analysis_report,
    )

    return APIResponse(
        success=True,
        data=tailoring,
        message=f"Tailoring complete. "
                f"Fit score: {tailoring.get('tailoring_score', 0)}/100",
    )
