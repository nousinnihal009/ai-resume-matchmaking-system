"""
Match API routes.
"""
import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..services.match_service import MatchService
from ..services.resume_service import ResumeService
from ..services.job_service import JobService
from ..schemas.match import MatchBase, MatchUpdate
from ..schemas.user import UserBase
from ..schemas.base import APIResponse
from ..core.security import get_current_user

from app.core.logging_config import get_logger
logger = get_logger(__name__)
router = APIRouter()


@router.post("/resume/{resume_id}", response_model=APIResponse[dict])
async def match_resume_to_jobs(
    resume_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[dict]:
    """Dispatch matching for a resume against all active jobs.

    The actual matching is performed asynchronously by a Celery worker.
    Returns the Celery task ID so the client can poll for status.
    """
    try:
        # Validate user permissions (students can match their own resumes, admins can match any)
        if current_user.role not in ["admin", "student"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform matching"
            )

        # If student, check if they own the resume
        if current_user.role == "student":
            resume_service = ResumeService(db)
            resumes = await resume_service.get_resumes_by_user(current_user.id)
            resume_ids = [str(r.id) for r in resumes]
            if str(resume_id) not in resume_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to match this resume"
                )

        # Dispatch to Celery worker
        from app.worker.tasks import batch_match_task
        task = batch_match_task.delay(resume_id=str(resume_id))

        logger.info(
            "batch_match_dispatched",
            resume_id=str(resume_id),
            user_id=str(current_user.id),
            celery_task_id=task.id,
        )

        return APIResponse(
            success=True,
            data={"task_id": task.id, "status": "queued"},
            message="Matching dispatched — results will be available shortly"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("match_resume_to_jobs_failed", resume_id=str(resume_id), user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/job/{job_id}", response_model=APIResponse[dict])
async def match_job_to_candidates(
    job_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[dict]:
    """Dispatch matching for a job against all available resumes.

    The actual matching is performed asynchronously by a Celery worker.
    Returns the Celery task ID so the client can poll for status.
    """
    try:
        # Validate user permissions (recruiters can match their own jobs, admins can match any)
        if current_user.role not in ["admin", "recruiter"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform matching"
            )

        # If recruiter, check if they own the job
        if current_user.role == "recruiter":
            from ..services.job_service import JobService
            job_service = JobService(db)
            jobs = await job_service.get_jobs_by_recruiter(current_user.id)
            job_ids = [str(j.id) for j in jobs]
            if str(job_id) not in job_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to match this job"
                )

        # Dispatch to Celery worker
        from app.worker.tasks import batch_match_task
        task = batch_match_task.delay(job_id=str(job_id))

        logger.info(
            "batch_match_dispatched",
            job_id=str(job_id),
            user_id=str(current_user.id),
            celery_task_id=task.id,
        )

        return APIResponse(
            success=True,
            data={"task_id": task.id, "status": "queued"},
            message="Matching dispatched — results will be available shortly"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("match_job_to_candidates_failed", job_id=str(job_id), user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/task/{task_id}", response_model=APIResponse[dict])
async def get_task_status(
    task_id: str,
    current_user: UserBase = Depends(get_current_user),
) -> APIResponse[dict]:
    """Poll for the status of a Celery matching task.

    Returns the task state and result (if completed).
    """
    from app.worker.celery_app import celery
    result = celery.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": result.state,
    }

    if result.ready():
        response["result"] = result.result
    elif result.failed():
        response["error"] = str(result.result)

    return APIResponse(
        success=True,
        data=response,
        message=f"Task status: {result.state}"
    )


@router.get("/student/{student_id}", response_model=APIResponse[List[MatchBase]])
async def get_student_matches(
    student_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[List[MatchBase]]:
    """Get all matches for a student."""
    try:
        # Check permissions (students can only see their own matches, admins can see all)
        if current_user.role not in ["admin"] and current_user.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these matches"
            )

        match_service = MatchService(db)
        matches = await match_service.get_matches_by_student(student_id)

        match_data = [MatchBase.model_validate(match) for match in matches]

        return APIResponse(
            success=True,
            data=match_data,
            message=f"Found {len(match_data)} matches"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_student_matches_failed", student_id=str(student_id), user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/recruiter/{recruiter_id}", response_model=APIResponse[List[MatchBase]])
async def get_recruiter_matches(
    recruiter_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[List[MatchBase]]:
    """Get all matches for a recruiter's jobs."""
    try:
        # Check permissions (recruiters can only see their own matches, admins can see all)
        if current_user.role not in ["admin"] and current_user.id != recruiter_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these matches"
            )

        match_service = MatchService(db)
        matches = await match_service.get_matches_by_recruiter(recruiter_id)

        match_data = [MatchBase.model_validate(match) for match in matches]

        return APIResponse(
            success=True,
            data=match_data,
            message=f"Found {len(match_data)} matches"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_recruiter_matches_failed", recruiter_id=str(recruiter_id), user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/job/{job_id}", response_model=APIResponse[List[MatchBase]])
async def get_job_matches(
    job_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[List[MatchBase]]:
    """Get all matches for a specific job."""
    try:
        match_service = MatchService(db)
        matches = await match_service.get_matches_by_job(job_id)

        match_data = [MatchBase.model_validate(match) for match in matches]

        return APIResponse(
            success=True,
            data=match_data,
            message=f"Found {len(match_data)} matches"
        )

    except Exception as e:
        logger.error("get_job_matches_failed", job_id=str(job_id), user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch("/{match_id}/status", response_model=APIResponse[MatchBase])
async def update_match_status(
    match_id: UUID,
    status_data: MatchUpdate,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[MatchBase]:
    """Update match status."""
    try:
        match_service = MatchService(db)
        match = await match_service.get_match_by_id(match_id)

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )

        # Check permissions (students can update their own matches, recruiters can update matches for their jobs, admins can update all)
        can_update = (
            current_user.role == "admin" or
            (current_user.role == "student" and match.student_id == current_user.id) or
            (current_user.role == "recruiter" and match.recruiter_id == current_user.id)
        )

        if not can_update:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this match"
            )

        updated_match = await match_service.update_match_status(match_id, status_data.status)
        if not updated_match:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update match status"
            )

        return APIResponse(
            success=True,
            data=MatchBase.model_validate(updated_match),
            message="Match status updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_match_status_failed", match_id=str(match_id), user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
