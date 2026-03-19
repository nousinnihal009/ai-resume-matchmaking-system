"""
GDPR/CCPA compliance API routes.

Endpoints:
  GET  /gdpr/export        — Right of access (Article 15 GDPR)
  POST /gdpr/delete        — Right to erasure (Article 17 GDPR)
  GET  /gdpr/consent       — Query current consent status
  POST /gdpr/consent       — Grant or revoke consent

All endpoints require authentication. Data export and deletion
operate only on the authenticated user's own data (no admin
override for privacy reasons).
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.base import APIResponse
from app.schemas.gdpr import (
    ConsentStatusResponse,
    ConsentUpdateRequest,
    DataExportResponse,
    DeletionRequest,
    DeletionResponse,
)
from app.schemas.user import UserBase
from app.services.gdpr_service import GDPRService

logger = get_logger(__name__)
router = APIRouter()


# ── Right of Access ────────────────────────────────────────────────────

@router.get("/export", response_model=APIResponse[DataExportResponse])
async def export_my_data(
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DataExportResponse]:
    """Download all personal data held by the system (GDPR Article 15)."""
    gdpr = GDPRService(db)
    data = await gdpr.export_user_data(current_user.id)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User data not found",
        )

    response = DataExportResponse(**data)

    logger.info("gdpr_data_exported", user_id=str(current_user.id))

    return APIResponse(
        success=True,
        data=response,
        message="Your data has been exported",
    )


# ── Right to Erasure ──────────────────────────────────────────────────

@router.post("/delete", response_model=APIResponse[DeletionResponse], status_code=202)
async def delete_my_data(
    body: DeletionRequest,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DeletionResponse]:
    """Request deletion of all personal data (GDPR Article 17).

    Deletion is performed asynchronously by a Celery worker.
    The response includes a task_id to poll for completion.
    """
    if not body.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must set confirm=true to request data deletion",
        )

    gdpr = GDPRService(db)
    task_id = await gdpr.delete_user_data(current_user.id)

    logger.info(
        "gdpr_deletion_requested",
        user_id=str(current_user.id),
        reason=body.reason or "none",
        task_id=task_id,
    )

    response = DeletionResponse(
        user_id=current_user.id,
        status="queued",
        task_id=task_id,
        message="Your data deletion request has been accepted and is being processed",
        requested_at=datetime.now(timezone.utc),
    )

    return APIResponse(
        success=True,
        data=response,
        message="Deletion request accepted",
    )


# ── Consent Management ───────────────────────────────────────────────

@router.get("/consent", response_model=APIResponse[ConsentStatusResponse])
async def get_my_consent(
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConsentStatusResponse]:
    """Query current consent status for all tracked types."""
    gdpr = GDPRService(db)
    consents = await gdpr.get_consent_status(current_user.id)

    response = ConsentStatusResponse(
        user_id=current_user.id,
        consents=consents,
        last_updated=datetime.now(timezone.utc),
    )

    return APIResponse(
        success=True,
        data=response,
        message="Consent status retrieved",
    )


@router.post("/consent", response_model=APIResponse[ConsentStatusResponse])
async def update_my_consent(
    body: ConsentUpdateRequest,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ConsentStatusResponse]:
    """Grant or revoke a specific consent type."""
    gdpr = GDPRService(db)

    try:
        consents = await gdpr.update_consent(
            user_id=current_user.id,
            consent_type=body.consent_type,
            granted=body.granted,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    action = "granted" if body.granted else "revoked"
    logger.info(
        "gdpr_consent_updated",
        user_id=str(current_user.id),
        consent_type=body.consent_type,
        action=action,
    )

    response = ConsentStatusResponse(
        user_id=current_user.id,
        consents=consents,
        last_updated=datetime.now(timezone.utc),
    )

    return APIResponse(
        success=True,
        data=response,
        message=f"Consent for '{body.consent_type}' has been {action}",
    )
