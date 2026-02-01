"""
Resume service layer for business logic.
"""
import logging
import os
from typing import Optional, List, Dict, Any
from uuid import UUID
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.models import Resume, User
from ..schemas.resume import ResumeUpdate
from ..pipeline.text_extraction import text_extraction_service
from ..pipeline.skill_extraction import skill_extractor
from ..core.config import settings

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for resume-related operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
        self.upload_dir = Path(settings.upload_directory)
        self.upload_dir.mkdir(exist_ok=True)

    async def upload_resume(
        self,
        file_content: bytes,
        filename: str,
        user_id: UUID
    ) -> Optional[Resume]:
        """Upload and process a resume file."""
        try:
            # Validate user exists and is a student
            user = await self._get_student_by_id(user_id)
            if not user or user.role != "student":
                return None

            # Validate file
            if not self._is_valid_file(filename, len(file_content)):
                return None

            # Save file
            file_path = self.upload_dir / f"{user_id}_{UUID().hex}_{filename}"
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Extract text from file
            extracted_text = await text_extraction_service.extract_text(str(file_path))

            # Extract skills from text
            skill_data = await skill_extractor.extract_skills(extracted_text)

            # Create resume record
            resume = Resume(
                user_id=user_id,
                file_name=filename,
                file_url=str(file_path),
                file_size=len(file_content),
                extracted_text=extracted_text,
                extracted_skills=skill_data["extracted_skills"],
                status="completed",
                metadata={
                    "skill_confidence": skill_data["confidence"],
                    "skill_categories": skill_data["categories"]
                }
            )

            self.db.add(resume)
            await self.db.commit()
            await self.db.refresh(resume)

            logger.info(f"Uploaded and processed resume: {resume.id} for user: {user_id}")
            return resume

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error uploading resume for user {user_id}: {e}")
            return None

    async def get_resume_by_id(self, resume_id: UUID) -> Optional[Resume]:
        """Get resume by ID."""
        try:
            result = await self.db.execute(
                select(Resume).where(Resume.id == resume_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting resume by ID {resume_id}: {e}")
            return None

    async def get_resumes_by_user(self, user_id: UUID) -> List[Resume]:
        """Get all resumes for a user."""
        try:
            result = await self.db.execute(
                select(Resume).where(Resume.user_id == user_id)
                .order_by(Resume.uploaded_at.desc())
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting resumes for user {user_id}: {e}")
            return []

    async def update_resume(
        self,
        resume_id: UUID,
        resume_data: ResumeUpdate
    ) -> Optional[Resume]:
        """Update resume information."""
        try:
            resume = await self.get_resume_by_id(resume_id)
            if not resume:
                return None

            # Update fields
            for field, value in resume_data.dict(exclude_unset=True).items():
                setattr(resume, field, value)

            await self.db.commit()
            await self.db.refresh(resume)

            logger.info(f"Updated resume: {resume_id}")
            return resume

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating resume {resume_id}: {e}")
            return None

    async def delete_resume(self, resume_id: UUID) -> bool:
        """Delete a resume."""
        try:
            resume = await self.get_resume_by_id(resume_id)
            if not resume:
                return False

            # Delete file if it exists
            if os.path.exists(resume.file_url):
                os.remove(resume.file_url)

            await self.db.delete(resume)
            await self.db.commit()

            logger.info(f"Deleted resume: {resume_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting resume {resume_id}: {e}")
            return False

    def _is_valid_file(self, filename: str, file_size: int) -> bool:
        """Validate uploaded file."""
        # Check file size
        if file_size > settings.max_file_size:
            return False

        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in settings.allowed_extensions:
            return False

        return True

    async def _get_student_by_id(self, student_id: UUID) -> Optional[User]:
        """Get student user by ID."""
        try:
            result = await self.db.execute(
                select(User).where(User.id == student_id)
            )
            user = result.scalar_one_or_none()
            return user if user and user.role == "student" else None
        except Exception as e:
            logger.error(f"Error getting student by ID {student_id}: {e}")
            return None
