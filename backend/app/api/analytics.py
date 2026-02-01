"""
Analytics API routes.
"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..services.analytics_service import AnalyticsService
from ..services.user_service import UserService
from ..schemas.analytics import MatchAnalytics, RecruiterDashboardStats, StudentDashboardStats
from ..schemas.user import UserBase
from ..schemas.base import APIResponse
from ..core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/student/{student_id}", response_model=APIResponse[StudentDashboardStats])
async def get_student_analytics(
    student_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[StudentDashboardStats]:
    """Get dashboard statistics for a student."""
    try:
        # Check permissions (students can only see their own analytics, admins can see all)
        if current_user.role not in ["admin"] and current_user.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these analytics"
            )

        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_student_dashboard_stats(student_id)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve analytics"
            )

        return APIResponse(
            success=True,
            data=stats,
            message="Student analytics retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get student analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/recruiter/{recruiter_id}", response_model=APIResponse[RecruiterDashboardStats])
async def get_recruiter_analytics(
    recruiter_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[RecruiterDashboardStats]:
    """Get dashboard statistics for a recruiter."""
    try:
        # Check permissions (recruiters can only see their own analytics, admins can see all)
        if current_user.role not in ["admin"] and current_user.id != recruiter_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these analytics"
            )

        analytics_service = AnalyticsService(db)
        stats = await analytics_service.get_recruiter_dashboard_stats(recruiter_id)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve analytics"
            )

        return APIResponse(
            success=True,
            data=stats,
            message="Recruiter analytics retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recruiter analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/matches/{user_id}", response_model=APIResponse[MatchAnalytics])
async def get_match_analytics(
    user_id: UUID,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[MatchAnalytics]:
    """Get comprehensive match analytics for a user."""
    try:
        # Check permissions (users can only see their own analytics, admins can see all)
        if current_user.role not in ["admin"] and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these analytics"
            )

        # Get user role
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_match_analytics(user_id, user.role)

        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve analytics"
            )

        return APIResponse(
            success=True,
            data=analytics,
            message="Match analytics retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get match analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
