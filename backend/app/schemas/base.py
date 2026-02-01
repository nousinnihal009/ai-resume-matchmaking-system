"""
Base Pydantic schemas with common configurations.
"""
from datetime import datetime
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from uuid import UUID


class BaseSchema(BaseModel):
    """Base schema with common configurations."""
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }


class APIResponse(BaseSchema):
    """Standard API response format."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class PaginatedResponse(BaseSchema):
    """Paginated response format."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
