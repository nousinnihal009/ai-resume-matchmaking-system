"""
Resume API endpoints.
"""
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import User
from app.schemas.resume import Resume, ResumeResponse
from app.schemas.base import APIResponse, PaginatedResponse
from app.services.resume_service import ResumeService
from .auth import get_current_user

router = APIRouter()


@router.post("/upload", response_model=APIResponse[Resume])
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Resume]:
    """
    Upload and process a resume file.
    """
    # Validate file type
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return APIResponse(
            success=False,
            error="Only PDF and DOCX files are supported",
            timestamp=datetime.utcnow().isoformat(),
        )

    # Validate file size (5MB limit)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        return APIResponse(
            success=False,
            error="File size must be less than 5MB",
            timestamp=datetime.utcnow().isoformat(),
        )

    resume_service = ResumeService(db)

    try:
        resume = await resume_service.process_resume(
            file_content=file_content,
            filename=file.filename,
            user_id=current_user.id,
        )

        return APIResponse(
            success=True,
            data=resume,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error="Failed to process resume",
            timestamp=datetime.utcnow().isoformat(),
        )


@router.get("/user/{user_id}", response_model=APIResponse[List[Resume]])
async def get_user_resumes(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[Resume]]:
    """
    Get all resumes for a user.
    """
    # Users can only see their own resumes
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these resumes",
        )

    resume_service = ResumeService(db)
    resumes = await resume_service.get_resumes_by_user(user_id)

    return APIResponse(
        success=True,
        data=resumes,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/{resume_id}", response_model=APIResponse[Resume])
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[Resume]:
    """
    Get a specific resume by ID.
    """
    resume_service = ResumeService(db)
    resume = await resume_service.get_resume_by_id(resume_id)

    if not resume:
        return APIResponse(
            success=False,
            error="Resume not found",
            timestamp=datetime.utcnow().isoformat(),
        )

    # Users can only see their own resumes
    if resume.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this resume",
        )

    return APIResponse(
        success=True,
        data=resume,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.delete("/{resume_id}", response_model=APIResponse[None])
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    """
    Delete a resume.
    """
    resume_service = ResumeService(db)
    resume = await resume_service.get_resume_by_id(resume_id)

    if not resume:
        return APIResponse(
            success=False,
            error="Resume not found",
            timestamp=datetime.utcnow().isoformat(),
        )

    # Users can only delete their own resumes
    if resume.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this resume",
        )

    success = await resume_service.delete_resume(resume_id)

    if not success:
        return APIResponse(
            success=False,
            error="Failed to delete resume",
            timestamp=datetime.utcnow().isoformat(),
        )

    return APIResponse(
        success=True,
        timestamp=datetime.utcnow().isoformat(),
    )
