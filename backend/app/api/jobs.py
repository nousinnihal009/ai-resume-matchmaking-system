"""
Jobs API routes.
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..services.job_service import JobService
from ..services.user_service import UserService
from ..schemas.job import JobBase, JobCreate, JobUpdate, JobPostingForm, JobFilters
from ..schemas.user import UserBase
from ..schemas.base import APIResponse, PaginatedResponse
from ..core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=APIResponse[JobBase])
async def create_job(
    job_data: JobPostingForm,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[JobBase]:
    """Create a new job posting."""
    try:
        # Validate user is a recruiter
        if current_user.role != "recruiter":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only recruiters can create job postings"
            )

        job_service = JobService(db)
        job = await job_service.create_job(job_data, current_user.id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create job posting"
            )

        # Dispatch embedding task for new job
        # This makes the job searchable via semantic similarity immediately
        try:
            from app.worker.tasks import embed_job
            embed_job.delay(str(job.id))
            logger.info(f"job_embedding_dispatched, job_id={str(job.id)}")
        except Exception as embed_err:
            logger.error(f"job_embedding_dispatch_failed, job_id={str(job.id)}, error={embed_err}")

        return APIResponse(
            success=True,
            data=JobBase.model_validate(job),
            message="Job posting created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create job error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=APIResponse[PaginatedResponse[JobBase]])
async def get_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    experience_level: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    skills: Optional[str] = Query(None),
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[PaginatedResponse[JobBase]]:
    """Get all active jobs with optional filters."""
    try:
        # Build filters
        filters = JobFilters()
        if status_filter:
            filters.status = [status_filter]
        if experience_level:
            filters.experience_level = [experience_level]
        if location:
            filters.location = [location]
        if skills:
            filters.skills = skills.split(",")

        job_service = JobService(db)
        jobs = await job_service.get_all_jobs(filters)

        # Simple pagination (in production, you'd use proper database pagination)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_jobs = jobs[start_idx:end_idx]

        job_data = [JobBase.model_validate(job) for job in paginated_jobs]

        response_data = PaginatedResponse(
            items=job_data,
            total=len(jobs),
            page=page,
            page_size=page_size,
            total_pages=(len(jobs) + page_size - 1) // page_size
        )

        return APIResponse(
            success=True,
            data=response_data,
            message=f"Found {len(job_data)} jobs"
        )

    except Exception as e:
        logger.error(f"Get jobs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/recruiter/{recruiter_id}", response_model=APIResponse[List[JobBase]])
async def get_recruiter_jobs(
    recruiter_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[List[JobBase]]:
    """Get all jobs posted by a recruiter."""
    try:
        # Check permissions (recruiters can only see their own jobs, admins can see all)
        if current_user.role not in ["admin"] and current_user.id != recruiter_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these jobs"
            )

        job_service = JobService(db)
        jobs = await job_service.get_jobs_by_recruiter(recruiter_id)

        job_data = [JobBase.model_validate(job) for job in jobs]

        return APIResponse(
            success=True,
            data=job_data,
            message=f"Found {len(job_data)} jobs"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recruiter jobs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{job_id}", response_model=APIResponse[JobBase])
async def get_job(
    job_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[JobBase]:
    """Get a specific job by ID."""
    try:
        job_service = JobService(db)
        job = await job_service.get_job_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        return APIResponse(
            success=True,
            data=JobBase.model_validate(job),
            message="Job retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get job error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{job_id}", response_model=APIResponse[JobBase])
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[JobBase]:
    """Update a job posting."""
    try:
        job_service = JobService(db)
        job = await job_service.get_job_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Check permissions (only the recruiter who created the job can update it, or admins)
        if current_user.role not in ["admin"] and job.recruiter_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this job"
            )

        updated_job = await job_service.update_job(job_id, job_data)
        if not updated_job:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update job"
            )

        return APIResponse(
            success=True,
            data=JobBase.model_validate(updated_job),
            message="Job updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update job error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{job_id}", response_model=APIResponse[dict])
async def delete_job(
    job_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[dict]:
    """Delete a job posting."""
    try:
        job_service = JobService(db)
        job = await job_service.get_job_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Check permissions (only the recruiter who created the job can delete it, or admins)
        if current_user.role not in ["admin"] and job.recruiter_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this job"
            )

        success = await job_service.delete_job(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete job"
            )

        return APIResponse(
            success=True,
            data={},
            message="Job deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete job error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
