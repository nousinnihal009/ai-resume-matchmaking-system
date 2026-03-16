"""
Authentication API routes.
"""
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..services.user_service import UserService
from ..schemas.user import UserBase, LoginRequest, SignupRequest, AuthResponse
from ..schemas.base import APIResponse
from ..core.security import create_access_token, get_current_user
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=APIResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access token."""
    try:
        user_service = UserService(db)
        user = await user_service.authenticate_user(login_data.email, login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify role matches
        if user.role != login_data.role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect role for this account",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )

        user_data = UserBase.from_orm(user)

        logger.info(f"User {user.email} logged in successfully")

        return APIResponse(
            success=True,
            data=AuthResponse(
                user=user_data,
                access_token=access_token,
                token_type="bearer"
            ).dict(),
            message="Login successful",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {login_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/signup", response_model=APIResponse)
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user account."""
    try:
        # Validate passwords match
        if signup_data.password != signup_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )

        user_service = UserService(db)

        # Check if user already exists
        existing_user = await user_service.get_user_by_email(signup_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user_data = {
            "email": signup_data.email,
            "password": signup_data.password,
            "name": signup_data.name,
            "role": signup_data.role
        }

        user = await user_service.create_user(user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )

        user_response = UserBase.from_orm(user)

        logger.info(f"User {user.email} signed up successfully")

        return APIResponse(
            success=True,
            data=AuthResponse(
                user=user_response,
                access_token=access_token,
                token_type="bearer"
            ).dict(),
            message="Account created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error for {signup_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout", response_model=APIResponse[dict])
async def logout(
    current_user: UserBase = Depends(get_current_user)
) -> APIResponse[dict]:
    """Logout current user."""
    try:
        # In a stateless JWT system, logout is handled client-side
        # by removing the token. We could implement token blacklisting here.

        logger.info(f"User {current_user.email} logged out")

        return APIResponse(
            success=True,
            data={},
            message="Logged out successfully"
        )

    except Exception as e:
        logger.error(f"Logout error for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=APIResponse[UserBase])
async def get_current_user_info(
    current_user: UserBase = Depends(get_current_user)
) -> APIResponse[UserBase]:
    """Get current user information."""
    try:
        return APIResponse(
            success=True,
            data=current_user,
            message="User information retrieved"
        )

    except Exception as e:
        logger.error(f"Get current user error for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
