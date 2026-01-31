"""
Match API endpoints.
"""
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import User
from app.schemas.match import Match, MatchResponse
from app.schemas.base import APIResponse
from app.services.matching_service import MatchingService
from .auth import get_current_user

router = APIRouter()


@router.post("/resume/{resume_id}", response_model=APIResponse[List[Match]])
async def match_resume_to_jobs(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[Match]]:
    """
    Find matching jobs for a resume.
    """
    matching_service = MatchingService(db)

    try:
        matches = await matching_service.match_resume_to_jobs(resume_id, current_user.id)

        return APIResponse(
            success=True,
            data=matches,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error="Failed to find matches",
            timestamp=datetime.utcnow().isoformat(),
        )


@router.post("/job/{job_id}", response_model=APIResponse[List[Match]])
async def match_job_to_candidates(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[Match]]:
    """
    Find matching candidates for a job.
    """
    # Only recruiters can match jobs to candidates
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can match jobs to candidates",
        )

    matching_service = MatchingService(db)

    try:
        matches = await matching_service.match_job_to_candidates(job_id, current_user.id)

        return APIResponse(
            success=True,
            data=matches,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error="Failed to find candidates",
            timestamp=datetime.utcnow().isoformat(),
        )


@router.get("/student/{student_id}", response_model=APIResponse[List[Match]])
async def get_student_matches(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[Match]]:
    """
    Get all matches for a student.
    """
    # Students can only see their own matches
    if current_user.id != student_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these matches",
        )

    matching_service = MatchingService(db)
    matches = await matching_service.get_matches_by_student(student_id)

    return APIResponse(
        success=True,
        data=matches,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/recruiter/{recruiter_id}", response_model=APIResponse[List[Match]])
async def get_recruiter_matches(
    recruiter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[Match]]:
    """
    Get all matches for a recruiter's jobs.
    """
    # Recruiters can only see their own matches
    if current_user.id != recruiter_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these matches",
        )

    matching_service = MatchingService(db)
    matches = await matching_service.get_matches_by_recruiter(recruiter_id)

    return APIResponse(
        success=True,
        data=matches,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/job/{job_id}", response_model=APIResponse[List[Match]])
async def get_job_matches(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[Match]]:
    """
    Get all matches for a specific job.
    """
    matching_service = MatchingService(db)

    # Check if user has permission to view this job's matches
    job = await matching_service.get_job_by_id(job_id)
    if not job:
        return APIResponse(
            success=False,
            error="Job not found",
            timestamp=datetime.utcnow().isoformat(),
        )

    if job.recruiter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these matches",
        )

    matches = await matching_service.get_matches_by_job(job_id)

    return APIResponse(
        success=True,
        data=matches,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.patch("/{match_id}/status", response_model=APIResponse[Match])
async def update_match_status(
    match_id: str,
    status_update: dict,  # {"status": "viewed|shortlisted|rejected"}
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Match]:
    """
    Update match status.
    """
    matching_service = MatchingService(db)

    # Get the match
    match = await matching_service.get_match_by_id(match_id)
    if not match:
        return APIResponse(
            success=False,
            error="Match not found",
            timestamp=datetime.utcnow().isoformat(),
        )

    # Check permissions
    if current_user.role == "student" and match.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this match",
        )
    elif current_user.role == "recruiter" and match.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this match",
        )

    new_status = status_update.get("status")
    if new_status not in ["pending", "viewed", "shortlisted", "rejected"]:
        return APIResponse(
            success=False,
            error="Invalid status",
            timestamp=datetime.utcnow().isoformat(),
        )

    updated_match = await matching_service.update_match_status(match_id, new_status)

    if not updated_match:
        return APIResponse(
            success=False,
            error="Failed to update match status",
            timestamp=datetime.utcnow().isoformat(),
        )

    return APIResponse(
        success=True,
        data=updated_match,
        timestamp=datetime.utcnow().isoformat(),
    )
