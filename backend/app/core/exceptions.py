"""
core/exceptions.py
──────────────────
Domain exceptions hierarchy.

All custom application errors inherit from MeetingAssistantError.
This allows FastAPI exception handlers to cleanly map domain errors
to consistent HTTP status codes and structured error responses.

Rule: Never raise generic Exception in business logic. Always use a typed domain exception.
"""

from typing import Optional, Any, Dict


class MeetingAssistantError(Exception):
    """Base exception for all domain errors in the application."""

    def __init__(
        self,
        message: str,
        error_code: str = "ERR_INTERNAL",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Format as a JSON-serializable dictionary for API error responses."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# ── Workflow & State Machine Errors ──────────────────────────────
class InvalidStateTransitionError(MeetingAssistantError):
    """Raised when an illegal status transition is attempted."""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        current_status: str,
        target_status: str,
        allowed_transitions: list,
    ):
        message = (
            f"Invalid status transition for {entity_type} '{entity_id}': "
            f"cannot move from '{current_status}' to '{target_status}'. "
            f"Allowed target transitions: {allowed_transitions}"
        )
        super().__init__(
            message=message,
            error_code="ERR_ILLEGAL_TRANSITION",
            details={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "current_status": current_status,
                "target_status": target_status,
                "allowed_transitions": allowed_transitions,
            },
        )


# ── Database & Resource Errors ───────────────────────────────────
class DuplicateTranscriptError(MeetingAssistantError):
    """Raised when an uploaded transcript matches an existing SHA-256 hash."""

    def __init__(self, transcript_hash: str, existing_meeting_id: str):
        message = (
            f"Transcript already ingested (SHA-256: {transcript_hash[:12]}...). "
            f"Existing meeting ID: {existing_meeting_id}"
        )
        super().__init__(
            message=message,
            error_code="ERR_DUPLICATE",
            details={
                "transcript_hash": transcript_hash,
                "existing_meeting_id": existing_meeting_id,
            },
        )


class MeetingNotFoundError(MeetingAssistantError):
    """Raised when a requested meeting is not found in the database."""

    def __init__(self, meeting_id: str):
        super().__init__(
            message=f"Meeting '{meeting_id}' not found.",
            error_code="ERR_MEETING_NOT_FOUND",
            details={"meeting_id": meeting_id},
        )


class ActionItemNotFoundError(MeetingAssistantError):
    """Raised when a requested action item is not found in the database."""

    def __init__(self, action_item_id: str):
        super().__init__(
            message=f"Action item '{action_item_id}' not found.",
            error_code="ERR_ACTION_NOT_FOUND",
            details={"action_item_id": action_item_id},
        )


# ── Ingestion & File Validation Errors ────────────────────────────
class InvalidFileError(MeetingAssistantError):
    """Raised when an uploaded file extension is unsupported or file is empty."""

    def __init__(self, message: str, filename: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="ERR_INVALID_FILE",
            details={"filename": filename} if filename else {},
        )


# ── AI & LLM Extraction Errors ────────────────────────────────────
class LLMExtractionError(MeetingAssistantError):
    """Raised when Gemini/Grok API fails or times out."""

    def __init__(self, message: str, provider: str, raw_response: Optional[str] = None):
        super().__init__(
            message=f"[{provider}] LLM Extraction Failed: {message}",
            error_code="ERR_LLM_TIMEOUT" if "timeout" in message.lower() else "ERR_LLM_FAILED",
            details={"provider": provider, "raw_response": raw_response},
        )


class LLMValidationError(MeetingAssistantError):
    """Raised when LLM output violates Pydantic schema validation."""

    def __init__(self, message: str, validation_errors: Optional[dict] = None):
        super().__init__(
            message=f"LLM output validation failed: {message}",
            error_code="ERR_JSON_PARSE",
            details={"validation_errors": validation_errors or {}},
        )


# ── GitHub Integration Errors ─────────────────────────────────────
class GitHubSyncError(MeetingAssistantError):
    """Raised when GitHub API issue creation fails."""

    def __init__(self, message: str, action_item_id: str):
        super().__init__(
            message=f"GitHub Issue creation failed for action item '{action_item_id}': {message}",
            error_code="ERR_GITHUB",
            details={"action_item_id": action_item_id},
        )
