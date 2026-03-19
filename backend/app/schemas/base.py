"""
Base Pydantic schemas with common configurations.
"""
from datetime import datetime
from typing import Optional, Any, Dict, List, Generic, TypeVar
from pydantic import BaseModel, Field
from uuid import UUID

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configurations."""
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
    }


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response envelope used by all endpoints.

    All responses from this API follow this shape regardless of
    the data type returned. Check `success` first, then read
    `data` on success or `error` on failure.

    Example success:
        {"success": true, "data": {...}, "message": "Done"}

    Example failure:
        {"success": false, "error": "Not found", "data": null}
    """
    success: bool = Field(
        description="True if the request succeeded, false otherwise"
    )
    data: T | None = Field(
        default=None,
        description="Response payload. Shape varies by endpoint."
    )
    error: str | None = Field(
        default=None,
        description="Error message. Only present when success is false."
    )
    message: str | None = Field(
        default=None,
        description="Human-readable status message."
    )
    timestamp: str | None = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO 8601 timestamp of the response."
    )


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response format."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
