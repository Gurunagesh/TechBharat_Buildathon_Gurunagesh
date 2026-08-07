"""
api/sync.py
───────────
Versioned External Integration REST Router (/api/v1/meetings/{meeting_id}/sync).

Endpoint:
- POST /api/v1/meetings/{meeting_id}/sync: Triggers GitHub issue creation for APPROVED items
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.business.sync_service import SyncService
from app.schemas.common import ResponseEnvelope
from app.schemas.action import SyncSummaryResponse
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/meetings", tags=["GitHub Sync"])


@router.post(
    "/{meeting_id}/sync",
    response_model=ResponseEnvelope[SyncSummaryResponse],
    summary="Sync Approved Items to GitHub",
    description="Finds all action items in APPROVED state for the meeting and creates GitHub Issues for them.",
)
def sync_approved_items(
    meeting_id: str,
    actor: str = "Human Approver",
    db: Session = Depends(get_db),
):
    """Trigger GitHub synchronization for approved action items."""
    logger.info(f"[{LogEvent.SYNC}] Sync request for meeting_id='{meeting_id}' by {actor}")

    sync_results = SyncService.sync_meeting_approved_items(
        db=db, meeting_id=meeting_id, actor=actor
    )

    successful_count = sum(1 for r in sync_results if r.get("status") == "SUCCESS")

    summary_data = SyncSummaryResponse(
        meeting_id=meeting_id,
        total_synced=successful_count,
        items=sync_results,
    )

    msg = f"Synced {successful_count} approved task(s) to GitHub." if successful_count > 0 else "No approved tasks were found to sync."
    return ResponseEnvelope.ok(data=summary_data, message=msg)
