"""
Authentication API routes.
"""
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..services.user_service import UserService
from ..schemas.user import UserBase, UserCreate, LoginRequest, SignupRequest, AuthResponse
from ..schemas.base import APIResponse
from ..core.security import create_access_token, get_current_user
from ..core.config import settings
from ..core.limiter import limiter

from app.core.logging_config import get_logger
logger = get_logger(__name__)
router = APIRouter()


@limiter.limit("5/minute")
@router.post("/login", response_model=APIResponse)
async def login(
    request: Request,
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

        # Return user data with token (in a real app, you'd return token separately)
        user_data = UserBase.model_validate(user)

        logger.info("user_login_success", email=user.email, user_id=str(user.id), role=user.role)

        return APIResponse(
            success=True,
            data=AuthResponse(
                user=user_data,
                access_token=access_token,
                token_type="bearer"
            ).model_dump(),
            message="Login successful",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("user_login_failed", email=login_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@limiter.limit("3/minute")
@router.post("/signup", response_model=APIResponse)
async def signup(
    request: Request,
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
        user_create = UserCreate(
            email=signup_data.email,
            password=signup_data.password,
            name=signup_data.name,
            role=signup_data.role,
            university=getattr(signup_data, 'university', None),
            major=getattr(signup_data, 'major', None),
            graduation_year=getattr(signup_data, 'graduation_year', None),
            company=getattr(signup_data, 'company', None),
            position=getattr(signup_data, 'position', None),
        )

        user = await user_service.create_user(user_create)
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

        user_response = UserBase.model_validate(user)

        logger.info("user_signup_success", email=user.email, user_id=str(user.id), role=user.role)

        try:
            from app.core.email import EmailService
            from app.schemas.email import WelcomeEmailPayload
            import asyncio
            asyncio.create_task(
                EmailService.send_welcome_email(
                    WelcomeEmailPayload(
                        to_email=user.email,
                        to_name=user.name,
                        role=user.role,
                    )
                )
            )
        except Exception as exc:
            logger.error("welcome_email_dispatch_failed", user_id=str(user.id), error=str(exc))

        return APIResponse(
            success=True,
            data=AuthResponse(
                user=user_response,
                access_token=access_token,
                token_type="bearer"
            ).model_dump(),
            message="Account created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("user_signup_failed", email=signup_data.email, error=str(e))
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

        logger.info("user_logout_success", email=current_user.email, user_id=str(current_user.id))

        return APIResponse(
            success=True,
            data={},
            message="Logged out successfully"
        )

    except Exception as e:
        logger.error("user_logout_failed", user_id=str(current_user.id), error=str(e))
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
        logger.error("get_user_info_failed", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
