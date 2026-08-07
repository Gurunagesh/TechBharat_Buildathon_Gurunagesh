"""
api/meetings.py
───────────────
Versioned Meetings REST Router (/api/v1/meetings).

Endpoints:
- POST /api/v1/meetings/upload: Upload transcript file (.txt, .vtt, .srt) & run extraction
- GET  /api/v1/meetings: List all meetings
- GET  /api/v1/meetings/{id}: Get single meeting detail
- GET  /api/v1/meetings/{id}/actions: Get action items for a meeting
"""

import json
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.business.meeting_service import MeetingService
from app.services.business.extraction_service import ExtractionService
from app.schemas.common import ResponseEnvelope
from app.schemas.meeting import (
    MeetingSummaryResponse,
    MeetingDetailResponse,
    MeetingUploadResponse,
    ParticipantResponse,
)
from app.schemas.action import ActionItemResponse
from app.models.enums import ProcessingStatus, ActionStatus
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/meetings", tags=["Meetings"])


@router.post(
    "/upload",
    response_model=ResponseEnvelope[MeetingUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Extract Transcript",
    description="Ingests a meeting transcript file (.txt, .vtt, .srt), checks SHA-256 duplicate, runs AI extraction, and stores results.",
)
async def upload_transcript(
    file: UploadFile = File(..., description="Transcript file (.txt, .vtt, .srt)"),
    meeting_date: Optional[date] = Form(None, description="Optional meeting anchor date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """Upload and process a meeting transcript."""
    logger.info(f"[{LogEvent.UPLOAD}] Received upload request: filename='{file.filename}'")

    content_bytes = await file.read()
    meeting, metrics = ExtractionService.process_transcript_file(
        db=db,
        filename=file.filename or "uploaded_transcript.txt",
        content_bytes=content_bytes,
        meeting_date=meeting_date,
    )

    upload_data = MeetingUploadResponse(
        meeting_id=meeting.meeting_id,
        title=meeting.title,
        processing_status=meeting.processing_status,
        is_duplicate=metrics.is_duplicate,
        action_items_extracted=metrics.action_items_count,
        total_time_ms=metrics.total_time_ms,
        llm_provider_used=metrics.llm_provider_used,
    )

    msg = "Existing meeting loaded (duplicate hash hit)." if metrics.is_duplicate else "Meeting uploaded and extracted successfully."
    return ResponseEnvelope.ok(data=upload_data, message=msg)


@router.get(
    "",
    response_model=ResponseEnvelope[List[MeetingSummaryResponse]],
    summary="List Meetings",
    description="Returns a list of all meetings ordered by creation date DESC.",
)
def list_meetings(
    status: Optional[ProcessingStatus] = Query(None, description="Filter by processing status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List meetings with optional filtering."""
    meetings = MeetingService.list_meetings(db=db, status=status, limit=limit, offset=offset)

    summaries = []
    for m in meetings:
        summaries.append(
            MeetingSummaryResponse(
                meeting_id=m.meeting_id,
                title=m.title,
                meeting_date=m.meeting_date,
                uploaded_at=m.uploaded_at,
                processing_status=m.processing_status,
                action_items_count=len(m.action_items),
                created_at=m.created_at,
            )
        )

    return ResponseEnvelope.ok(data=summaries)


@router.get(
    "/{meeting_id}",
    response_model=ResponseEnvelope[MeetingDetailResponse],
    summary="Get Meeting Detail",
    description="Fetches full meeting detail by UUID including summary, decisions, risks, questions, and participants.",
)
def get_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """Get single meeting detail."""
    meeting = MeetingService.get_meeting_by_id(db=db, meeting_id=meeting_id)

    # Safely parse stored JSON strings
    decisions = json.loads(meeting.decisions or "[]")
    risks = json.loads(meeting.risks or "[]")
    open_questions = json.loads(meeting.open_questions or "[]")

    participants = [
        ParticipantResponse(
            participant_id=p.participant_id,
            name=p.name,
            email=p.email,
            role=p.role,
        )
        for p in meeting.participants
    ]

    detail = MeetingDetailResponse(
        meeting_id=meeting.meeting_id,
        title=meeting.title,
        meeting_date=meeting.meeting_date,
        uploaded_at=meeting.uploaded_at,
        transcript_hash=meeting.transcript_hash,
        processing_status=meeting.processing_status,
        summary=meeting.summary,
        decisions=decisions,
        risks=risks,
        open_questions=open_questions,
        participants=participants,
        error_message=meeting.error_message,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )

    return ResponseEnvelope.ok(data=detail)


@router.get(
    "/{meeting_id}/actions",
    response_model=ResponseEnvelope[List[ActionItemResponse]],
    summary="Get Meeting Action Items",
    description="Fetches all action items for a given meeting, optionally filtered by ActionStatus.",
)
def get_meeting_action_items(
    meeting_id: str,
    action_status: Optional[ActionStatus] = Query(None, description="Filter by action status (PENDING_REVIEW, APPROVED, REJECTED, SYNCED)"),
    db: Session = Depends(get_db),
):
    """Fetch action items for a meeting."""
    items = MeetingService.get_meeting_action_items(db=db, meeting_id=meeting_id, status=action_status)
    item_responses = [ActionItemResponse.model_validate(item) for item in items]
    return ResponseEnvelope.ok(data=item_responses)
