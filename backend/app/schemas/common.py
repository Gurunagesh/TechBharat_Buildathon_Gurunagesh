"""
schemas/common.py
─────────────────
Common API Response Envelopes & Schemas.

Enforces a single, consistent response envelope across all API endpoints:

Success Envelope:
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... },
    "error": null
}

Error Envelope:
{
    "success": false,
    "message": "Human readable error message",
    "data": null,
    "error": {
        "error_code": "ERR_DUPLICATE",
        "message": "...",
        "details": { ... }
    }
}
"""

from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetails(BaseModel):
    """Detailed error object contained in an error response envelope."""
    error_code: str = Field(description="Structured error code (e.g. ERR_DUPLICATE, ERR_ILLEGAL_TRANSITION)")
    message: str = Field(description="Human readable explanation of the error.")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional contextual key-value pairs.")


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standard generic API response envelope."""
    success: bool = Field(description="True if request succeeded, False if error occurred.")
    message: str = Field(default="Operation completed successfully.", description="Status message.")
    data: Optional[T] = Field(default=None, description="Response payload data when success=True.")
    error: Optional[ErrorDetails] = Field(default=None, description="Error payload when success=False.")

    @classmethod
    def ok(cls, data: T, message: str = "Operation completed successfully.") -> "ResponseEnvelope[T]":
        """Factory for successful response envelopes."""
        return cls(success=True, message=message, data=data, error=None)

    @classmethod
    def fail(cls, error_code: str, message: str, details: Optional[Dict[str, Any]] = None) -> "ResponseEnvelope[None]":
        """Factory for error response envelopes."""
        return cls(
            success=False,
            message=message,
            data=None,
            error=ErrorDetails(error_code=error_code, message=message, details=details or {}),
        )


class HealthResponse(BaseModel):
    """Health check endpoint payload schema."""
    status: str
    version: str
    database: str
    gemini_configured: bool
    github_configured: bool
    github_enabled: bool
