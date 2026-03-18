"""
User service layer for business logic.
"""
import logging
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from ..db.models import User, StudentProfile, RecruiterProfile
from ..schemas.user import UserCreate, UserUpdate, StudentProfileBase, RecruiterProfileBase

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user-related operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user."""
        try:
            # Hash password
            hashed_password = self._hash_password(user_data.password)

            # Create user
            user = User(
                email=user_data.email,
                password_hash=hashed_password,
                name=user_data.name,
                role=user_data.role
            )

            self.db.add(user)
            await self.db.flush()  # Provide user.id without committing transaction yet

            # Create profile based on role
            if user_data.role == "student":
                profile = StudentProfile(
                    user_id=user.id,
                    university=getattr(user_data, 'university', None),
                    major=getattr(user_data, 'major', None),
                    graduation_year=getattr(user_data, 'graduation_year', None)
                )
                self.db.add(profile)
            elif user_data.role == "recruiter":
                profile = RecruiterProfile(
                    user_id=user.id,
                    company=getattr(user_data, 'company', None) or "Not Provided",
                    position=getattr(user_data, 'position', None)
                )
                self.db.add(profile)

            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Created user: {user.id}")
            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user {user_data.email}: {e}", exc_info=True)
            raise e

    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None

            # Update fields
            for field, value in user_data.dict(exclude_unset=True).items():
                if field == "password" and value:
                    setattr(user, "password_hash", self._hash_password(value))
                elif field != "password":
                    setattr(user, field, value)

            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Updated user: {user_id}")
            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None

            if not self._verify_password(password, user.password_hash):
                return None

            return user

        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None

    async def get_student_profile(self, user_id: UUID) -> Optional[StudentProfile]:
        """Get student profile for user."""
        try:
            result = await self.db.execute(
                select(StudentProfile).where(StudentProfile.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting student profile for user {user_id}: {e}")
            return None

    async def get_recruiter_profile(self, user_id: UUID) -> Optional[RecruiterProfile]:
        """Get recruiter profile for user."""
        try:
            result = await self.db.execute(
                select(RecruiterProfile).where(RecruiterProfile.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting recruiter profile for user {user_id}: {e}")
            return None

    async def update_student_profile(
        self,
        user_id: UUID,
        profile_data: StudentProfileBase
    ) -> Optional[StudentProfile]:
        """Update student profile."""
        try:
            profile = await self.get_student_profile(user_id)
            if not profile:
                return None

            # Update fields
            for field, value in profile_data.dict(exclude_unset=True).items():
                setattr(profile, field, value)

            await self.db.commit()
            await self.db.refresh(profile)

            return profile

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating student profile for user {user_id}: {e}")
            return None

    async def update_recruiter_profile(
        self,
        user_id: UUID,
        profile_data: RecruiterProfileBase
    ) -> Optional[RecruiterProfile]:
        """Update recruiter profile."""
        try:
            profile = await self.get_recruiter_profile(user_id)
            if not profile:
                return None

            # Update fields
            for field, value in profile_data.dict(exclude_unset=True).items():
                setattr(profile, field, value)

            await self.db.commit()
            await self.db.refresh(profile)

            return profile

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating recruiter profile for user {user_id}: {e}")
            return None

    async def _create_student_profile(self, user_id: UUID, user_data: UserCreate) -> None:
        """Create student profile for new user."""
        profile = StudentProfile(
            user_id=user_id,
            university=getattr(user_data, 'university', None),
            major=getattr(user_data, 'major', None),
            graduation_year=getattr(user_data, 'graduation_year', None)
        )
        self.db.add(profile)

    async def _create_recruiter_profile(self, user_id: UUID, user_data: UserCreate) -> None:
        """Create recruiter profile for new user."""
        profile = RecruiterProfile(
            user_id=user_id,
            company=getattr(user_data, 'company', None),
            position=getattr(user_data, 'position', None)
        )
        self.db.add(profile)

    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
