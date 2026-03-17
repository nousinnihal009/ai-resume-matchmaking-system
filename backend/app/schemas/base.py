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


class APIResponse(BaseSchema, Generic[T]):
    """Standard API response format."""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response format."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
