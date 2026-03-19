"""
Admin dashboard API endpoints.

All endpoints in this router require:
  1. Valid JWT authentication (401 if missing/invalid)
  2. User role == "admin" (403 if student or recruiter)

Endpoints:
  GET  /admin/stats              — Platform-wide statistics
  GET  /admin/users              — Paginated user list
  GET  /admin/users/{user_id}    — Single user detail
  PATCH /admin/users/{user_id}/status — Activate/deactivate user
  GET  /admin/matches            — Match audit log
  GET  /admin/health             — Platform health indicators
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models import User
from app.schemas.base import APIResponse
from app.schemas.admin import (
    SystemStats,
    UserStatusUpdate,
    PlatformHealthResponse,
)
from app.services.admin_service import AdminService
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that enforces admin role.
    Returns the user if admin, raises 403 otherwise.
    Inject this as a dependency on every admin endpoint.
    """
    if current_user.role != "admin":
        logger.warning(
            "admin_access_denied",
            user_id=str(current_user.id),
            role=current_user.role,
            reason="non-admin role attempted admin endpoint",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


@router.get("/stats", response_model=APIResponse)
async def get_system_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Platform-wide statistics for the admin dashboard.
    Returns user counts, content counts, match metrics, and top skills.
    """
    logger.info("admin_stats_requested", admin_id=str(admin.id))
    service = AdminService(db)
    stats = await service.get_system_stats()
    return APIResponse(success=True, data=stats)


@router.get("/users", response_model=APIResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Paginated list of all platform users.
    Supports filtering by role and active status.
    """
    logger.info(
        "admin_users_list_requested",
        admin_id=str(admin.id),
        page=page,
        role=role,
    )
    service = AdminService(db)
    result = await service.get_all_users(
        page=page, limit=limit, role=role, is_active=is_active
    )
    return APIResponse(success=True, data=result)


@router.patch("/users/{user_id}/status", response_model=APIResponse)
async def update_user_status(
    user_id: str,
    update: UserStatusUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate or deactivate a user account.
    Deactivated users cannot log in or access any endpoint.
    """
    logger.info(
        "admin_user_status_update",
        admin_id=str(admin.id),
        target_user_id=user_id,
        new_status=update.is_active,
    )
    try:
        service = AdminService(db)
        updated_user = await service.update_user_status(
            user_id=user_id,
            is_active=update.is_active,
            reason=update.reason,
        )
        return APIResponse(
            success=True,
            data=updated_user,
            message=f"User {'activated' if update.is_active else 'deactivated'} successfully.",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get("/matches", response_model=APIResponse)
async def get_match_audit_log(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Paginated match audit log with full context.
    Shows all matches across all users for oversight and debugging.
    """
    logger.info(
        "admin_match_audit_requested",
        admin_id=str(admin.id),
        page=page,
    )
    service = AdminService(db)
    result = await service.get_match_audit_log(page=page, limit=limit)
    return APIResponse(success=True, data=result)


@router.get("/health", response_model=APIResponse)
async def get_platform_health(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Real-time platform health indicators.
    Checks database, Redis, and Celery worker connectivity.
    """
    logger.info(
        "admin_health_check_requested", admin_id=str(admin.id)
    )
    service = AdminService(db)
    health = await service.get_platform_health()
    return APIResponse(success=True, data=health)
