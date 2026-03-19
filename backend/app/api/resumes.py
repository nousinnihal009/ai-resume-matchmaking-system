"""
Resume API routes.
"""
import logging
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..services.resume_service import ResumeService
from ..services.user_service import UserService
from ..schemas.resume import ResumeBase, ResumeUploadResponse
from ..schemas.user import UserBase
from ..schemas.base import APIResponse
from ..core.security import get_current_user
from ..core.config import settings

from app.core.logging_config import get_logger
logger = get_logger(__name__)
router = APIRouter()


@router.post("/upload", response_model=APIResponse[ResumeUploadResponse])
async def upload_resume(
    file: UploadFile = File(...),
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[ResumeUploadResponse]:
    """Upload and process a resume file.

    The file is saved to disk and a database row is created with
    status='processing'. Actual text/skill extraction is dispatched
    to a Celery background worker so the HTTP response returns
    immediately.
    """
    try:
        # Validate user is a student
        if current_user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can upload resumes"
            )

        # Read file content
        file_content = await file.read()

        resume_service = ResumeService(db)

        # Validate file before saving
        if not resume_service._is_valid_file(file.filename, len(file_content)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type or file too large"
            )

        # Save file to disk
        from pathlib import Path
        upload_dir = Path(settings.upload_directory)
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / f"{current_user.id}_{uuid4().hex}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Create resume record with status='processing'
        from ..db.models import Resume
        resume = Resume(
            user_id=current_user.id,
            file_name=file.filename,
            file_url=str(file_path),
            file_size=len(file_content),
            status="processing",
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)

        # Dispatch to Celery worker for async processing
        from app.worker.tasks import process_resume_task
        task = process_resume_task.delay(
            resume_id=str(resume.id),
            file_path=str(file_path),
        )

        logger.info(
            "resume_upload_queued",
            resume_id=str(resume.id),
            user_id=str(current_user.id),
            celery_task_id=task.id,
        )

        # Create response
        response_data = ResumeUploadResponse(
            resume=ResumeBase.model_validate(resume),
            processing_status="queued"
        )

        return APIResponse(
            success=True,
            data=response_data,
            message="Resume uploaded — processing in background"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("resume_upload_failed", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/user/{user_id}", response_model=APIResponse[List[ResumeBase]])
async def get_user_resumes(
    user_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[List[ResumeBase]]:
    """Get all resumes for a user."""
    try:
        # Check permissions (users can only see their own resumes, admins can see all)
        if current_user.role not in ["admin"] and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these resumes"
            )

        resume_service = ResumeService(db)
        resumes = await resume_service.get_resumes_by_user(user_id)

        resume_data = [ResumeBase.model_validate(resume) for resume in resumes]

        return APIResponse(
            success=True,
            data=resume_data,
            message=f"Found {len(resume_data)} resumes"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_user_resumes_failed", user_id=str(user_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{resume_id}", response_model=APIResponse[ResumeBase])
async def get_resume(
    resume_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[ResumeBase]:
    """Get a specific resume by ID."""
    try:
        resume_service = ResumeService(db)
        resume = await resume_service.get_resume_by_id(resume_id)

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        # Check permissions
        if current_user.role not in ["admin"] and resume.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this resume"
            )

        return APIResponse(
            success=True,
            data=ResumeBase.model_validate(resume),
            message="Resume retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_resume_failed", resume_id=str(resume_id), user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{resume_id}", response_model=APIResponse[dict])
async def delete_resume(
    resume_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[dict]:
    """Delete a resume."""
    try:
        resume_service = ResumeService(db)
        resume = await resume_service.get_resume_by_id(resume_id)

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        # Check permissions
        if current_user.role not in ["admin"] and resume.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this resume"
            )

        success = await resume_service.delete_resume(resume_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete resume"
            )

        return APIResponse(
            success=True,
            data={},
            message="Resume deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_resume_failed", resume_id=str(resume_id), user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
