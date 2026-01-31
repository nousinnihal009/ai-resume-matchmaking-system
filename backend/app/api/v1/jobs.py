"""
Job API endpoints.
"""
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import User
from app.schemas.job import Job, JobCreate, JobUpdate, JobResponse
from app.schemas.base import APIResponse, PaginatedResponse
from app.services.job_service import JobService
from .auth import get_current_user

router = APIRouter()


@router.post("/", response_model=APIResponse[Job])
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Job]:
    """
    Create a new job posting.
    """
    # Only recruiters can create jobs
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can create job postings",
        )

    job_service = JobService(db)

    try:
        job = await job_service.create_job(job_data, current_user.id)

        return APIResponse(
            success=True,
            data=job,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error="Failed to create job",
            timestamp=datetime.utcnow().isoformat(),
        )


@router.get("/", response_model=APIResponse[PaginatedResponse[Job]])
async def get_jobs(
    status_filter: str = None,
    experience_level: str = None,
    location: str = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PaginatedResponse[Job]]:
    """
    Get all jobs with optional filtering and pagination.
    """
    job_service = JobService(db)

    try:
        jobs = await job_service.get_all_jobs(status=status_filter)

        # Simple pagination (in production, use proper pagination)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_jobs = jobs[start_idx:end_idx]

        response_data = {
            "items": paginated_jobs,
            "total": len(jobs),
            "page": page,
            "pageSize": page_size,
            "totalPages": (len(jobs) + page_size - 1) // page_size,
        }

        return APIResponse(
            success=True,
            data=response_data,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error="Failed to retrieve jobs",
            timestamp=datetime.utcnow().isoformat(),
        )


@router.get("/recruiter/{recruiter_id}", response_model=APIResponse[List[Job]])
async def get_recruiter_jobs(
    recruiter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[Job]]:
    """
    Get jobs posted by a recruiter.
    """
    # Recruiters can only see their own jobs
    if current_user.id != recruiter_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these jobs",
        )

    job_service = JobService(db)
    jobs = await job_service.get_jobs_by_recruiter(recruiter_id)

    return APIResponse(
        success=True,
        data=jobs,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/{job_id}", response_model=APIResponse[Job])
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Job]:
    """
    Get a specific job by ID.
    """
    job_service = JobService(db)
    job = await job_service.get_job_by_id(job_id)

    if not job:
        return APIResponse(
            success=False,
            error="Job not found",
            timestamp=datetime.utcnow().isoformat(),
        )

    return APIResponse(
        success=True,
        data=job,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.put("/{job_id}", response_model=APIResponse[Job])
async def update_job(
    job_id: str,
    updates: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Job]:
    """
    Update a job posting.
    """
    job_service = JobService(db)

    # Check if job exists and user has permission
    job = await job_service.get_job_by_id(job_id)
    if not job:
        return APIResponse(
            success=False,
            error="Job not found",
            timestamp=datetime.utcnow().isoformat(),
        )

    if job.recruiter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this job",
        )

    updated_job = await job_service.update_job(job_id, updates)

    if not updated_job:
        return APIResponse(
            success=False,
            error="Failed to update job",
            timestamp=datetime.utcnow().isoformat(),
        )

    return APIResponse(
        success=True,
        data=updated_job,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.delete("/{job_id}", response_model=APIResponse[None])
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    """
    Delete a job posting.
    """
    job_service = JobService(db)

    # Check if job exists and user has permission
    job = await job_service.get_job_by_id(job_id)
    if not job:
        return APIResponse(
            success=False,
            error="Job not found",
            timestamp=datetime.utcnow().isoformat(),
        )

    if job.recruiter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job",
        )

    success = await job_service.delete_job(job_id)

    if not success:
        return APIResponse(
            success=False,
            error="Failed to delete job",
            timestamp=datetime.utcnow().isoformat(),
        )

    return APIResponse(
        success=True,
        timestamp=datetime.utcnow().isoformat(),
    )
