"""
api/exception_handlers.py
─────────────────────────
Global FastAPI Exception Handlers.

Maps all custom domain exceptions (inheriting from MeetingAssistantError)
to consistent ResponseEnvelope.fail() JSON payloads with standard HTTP status codes.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import (
    MeetingAssistantError,
    DuplicateTranscriptError,
    MeetingNotFoundError,
    ActionItemNotFoundError,
    InvalidStateTransitionError,
    InvalidFileError,
    LLMExtractionError,
    LLMValidationError,
    GitHubSyncError,
)
from app.schemas.common import ResponseEnvelope
from app.core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI application."""

    @app.exception_handler(DuplicateTranscriptError)
    async def duplicate_transcript_handler(request: Request, exc: DuplicateTranscriptError):
        logger.warning(f"[HTTP 409] Duplicate transcript: {exc.message}")
        envelope = ResponseEnvelope.fail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=envelope.model_dump(),
        )

    @app.exception_handler(MeetingNotFoundError)
    async def meeting_not_found_handler(request: Request, exc: MeetingNotFoundError):
        logger.warning(f"[HTTP 404] Meeting not found: {exc.message}")
        envelope = ResponseEnvelope.fail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=envelope.model_dump(),
        )

    @app.exception_handler(ActionItemNotFoundError)
    async def action_not_found_handler(request: Request, exc: ActionItemNotFoundError):
        logger.warning(f"[HTTP 404] Action item not found: {exc.message}")
        envelope = ResponseEnvelope.fail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=envelope.model_dump(),
        )

    @app.exception_handler(InvalidStateTransitionError)
    async def invalid_transition_handler(request: Request, exc: InvalidStateTransitionError):
        logger.warning(f"[HTTP 409] Illegal workflow transition: {exc.message}")
        envelope = ResponseEnvelope.fail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=envelope.model_dump(),
        )

    @app.exception_handler(InvalidFileError)
    async def invalid_file_handler(request: Request, exc: InvalidFileError):
        logger.warning(f"[HTTP 400] Invalid upload file: {exc.message}")
        envelope = ResponseEnvelope.fail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=envelope.model_dump(),
        )

    @app.exception_handler(LLMExtractionError)
    async def llm_extraction_handler(request: Request, exc: LLMExtractionError):
        logger.error(f"[HTTP 503] LLM service extraction error: {exc.message}")
        envelope = ResponseEnvelope.fail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=envelope.model_dump(),
        )

    @app.exception_handler(GitHubSyncError)
    async def github_sync_handler(request: Request, exc: GitHubSyncError):
        logger.error(f"[HTTP 502] GitHub sync error: {exc.message}")
        envelope = ResponseEnvelope.fail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=envelope.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"[HTTP 422] Request validation error: {exc}")
        envelope = ResponseEnvelope.fail(
            error_code="ERR_VALIDATION",
            message="Request payload validation failed.",
            details={"errors": exc.errors()},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=envelope.model_dump(),
        )

    @app.exception_handler(MeetingAssistantError)
    async def generic_domain_error_handler(request: Request, exc: MeetingAssistantError):
        logger.error(f"[HTTP 500] Domain error: {exc.message}")
        envelope = ResponseEnvelope.fail(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=envelope.model_dump(),
        )
