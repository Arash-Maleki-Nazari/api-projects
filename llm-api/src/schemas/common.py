"""Common response schemas."""
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response."""

    status: str = "error"
    message: str
    trace_id: Optional[str] = None
    timestamp: datetime = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Invalid product price",
                "trace_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response wrapper."""

    status: str = "success"
    data: Any
    trace_id: Optional[str] = None
    timestamp: datetime = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {"primary_category": "mid-range"},
                "trace_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
