"""
api/audit.py
────────────
Versioned Audit Trail REST Router (/api/v1/meetings/{meeting_id}/audit).

Endpoint:
- GET /api/v1/meetings/{meeting_id}/audit: Fetch immutable event timeline for a meeting
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.business.audit_service import AuditService
from app.services.business.meeting_service import MeetingService
from app.schemas.common import ResponseEnvelope
from app.schemas.audit import AuditLogResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/meetings", tags=["Audit Logs"])


@router.get(
    "/{meeting_id}/audit",
    response_model=ResponseEnvelope[List[AuditLogResponse]],
    summary="Get Meeting Audit Trail",
    description="Returns the complete chronological event history for a meeting (uploads, extraction, edits, approvals, syncs).",
)
def get_meeting_audit_trail(
    meeting_id: str,
    db: Session = Depends(get_db),
):
    """Fetch chronological audit trail for a meeting."""
    # Ensure meeting exists
    MeetingService.get_meeting_by_id(db=db, meeting_id=meeting_id)

    logs = AuditService.get_meeting_audit_trail(db=db, meeting_id=meeting_id)
    log_responses = [AuditLogResponse.model_validate(log) for log in logs]
    return ResponseEnvelope.ok(data=log_responses)
