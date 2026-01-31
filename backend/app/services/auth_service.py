"""
Authentication service for user management.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.security import verify_password, get_password_hash, create_access_token
from app.db.models import User, StudentProfile, RecruiterProfile
from app.schemas.auth import UserCreate, LoginRequest
from app.core.config import settings

logger = structlog.get_logger(__name__)


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, credentials: LoginRequest) -> Optional[User]:
        """
        Authenticate user with email and password.
        """
        logger.info("Authenticating user", email=credentials.email)

        # Find user by email and role
        stmt = select(User).where(
            User.email == credentials.email,
            User.role == credentials.role
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("User not found", email=credentials.email)
            return None

        if not verify_password(credentials.password, user.password_hash):
            logger.warning("Invalid password", email=credentials.email)
            return None

        logger.info("User authenticated successfully", user_id=user.id)
        return user

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user account.
        """
        logger.info("Creating new user", email=user_data.email)

        # Check if user already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Email already registered")

        # Create user
        user = User(
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            password_hash=get_password_hash(user_data.password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(user)
        await self.db.flush()  # Get user ID

        # Create profile based on role
        if user_data.role == "student":
            profile = StudentProfile(
                user_id=user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(profile)
        elif user_data.role == "recruiter":
            profile = RecruiterProfile(
                user_id=user.id,
                company="Company Name",  # Default, can be updated later
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(profile)

        await self.db.commit()
        await self.db.refresh(user)

        logger.info("User created successfully", user_id=user.id)
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_access_token(self, user: User) -> str:
        """
        Create JWT access token for user.
        """
        return create_access_token(subject=user.id)

    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from JWT token.
        """
        from app.core.security import verify_token

        user_id = verify_token(token)
        if not user_id:
            return None

        return await self.get_user_by_id(user_id)
