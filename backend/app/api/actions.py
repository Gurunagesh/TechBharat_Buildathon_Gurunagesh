"""
api/actions.py
──────────────
Versioned Action Items REST Router (/api/v1/actions).

Endpoints for human review & editing:
- PATCH /api/v1/actions/{id}: Edit title, owner, due_date, priority
- POST  /api/v1/actions/{id}/approve: Mark APPROVED for sync
- POST  /api/v1/actions/{id}/reject: Mark REJECTED
"""

from fastapi import APIRouter, Depends, Body, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.business.approval_service import ApprovalService
from app.services.business.meeting_service import MeetingService
from app.schemas.common import ResponseEnvelope
from app.schemas.action import (
    ActionItemResponse,
    ActionItemEditRequest,
    ActionItemRejectRequest,
)
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/actions", tags=["Action Items"])


@router.patch(
    "/{action_id}",
    response_model=ResponseEnvelope[ActionItemResponse],
    summary="Edit Action Item",
    description="Human editor updates task title, owner, due_date, or priority before approval.",
)
def edit_action_item(
    action_id: str,
    payload: ActionItemEditRequest = Body(...),
    actor: str = "Human Reviewer",
    db: Session = Depends(get_db),
):
    """Edit an action item's fields."""
    logger.info(f"[{LogEvent.EDIT}] Edit request for action_id='{action_id}' by {actor}")

    updated_item = ApprovalService.edit_action_item(
        db=db,
        action_item_id=action_id,
        title=payload.title,
        owner=payload.owner,
        due_date=payload.due_date,
        priority=payload.priority,
        actor=actor,
    )

    response_data = ActionItemResponse.model_validate(updated_item)
    return ResponseEnvelope.ok(data=response_data, message="Action item updated successfully.")


@router.post(
    "/{action_id}/approve",
    response_model=ResponseEnvelope[ActionItemResponse],
    summary="Approve Action Item",
    description="Transitions action item status from PENDING_REVIEW to APPROVED, making it eligible for GitHub sync.",
)
def approve_action_item(
    action_id: str,
    actor: str = "Human Reviewer",
    db: Session = Depends(get_db),
):
    """Approve an action item."""
    logger.info(f"[{LogEvent.APPROVE}] Approve request for action_id='{action_id}' by {actor}")

    approved_item = ApprovalService.approve_action_item(
        db=db, action_item_id=action_id, actor=actor
    )

    response_data = ActionItemResponse.model_validate(approved_item)
    return ResponseEnvelope.ok(data=response_data, message="Action item APPROVED successfully.")


@router.post(
    "/{action_id}/reject",
    response_model=ResponseEnvelope[ActionItemResponse],
    summary="Reject Action Item",
    description="Transitions action item status from PENDING_REVIEW to REJECTED.",
)
def reject_action_item(
    action_id: str,
    payload: ActionItemRejectRequest = Body(default_factory=ActionItemRejectRequest),
    actor: str = "Human Reviewer",
    db: Session = Depends(get_db),
):
    """Reject an action item."""
    logger.info(f"[{LogEvent.REJECT}] Reject request for action_id='{action_id}' by {actor}")

    rejected_item = ApprovalService.reject_action_item(
        db=db,
        action_item_id=action_id,
        reason=payload.reason,
        actor=actor,
    )

    response_data = ActionItemResponse.model_validate(rejected_item)
    return ResponseEnvelope.ok(data=response_data, message="Action item REJECTED.")
