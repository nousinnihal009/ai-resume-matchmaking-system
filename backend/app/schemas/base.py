"""
Base Pydantic schemas and utilities.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class IDMixin(BaseSchema):
    """Mixin for models with ID field."""
    id: str


class TimestampMixin(BaseSchema):
    """Mixin for models with timestamp fields."""
    created_at: datetime
    updated_at: datetime


class APIResponse(BaseSchema):
    """Generic API response schema."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: str


class PaginatedResponse(BaseSchema):
    """Generic paginated response schema."""
    items: list
    total: int
    page: int
    pageSize: int
    totalPages: int
