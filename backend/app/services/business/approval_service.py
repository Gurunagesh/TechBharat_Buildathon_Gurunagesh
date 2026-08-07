"""
services/business/approval_service.py
──────────────────────────────────────
Human Review & Approval Service.

Enforces human-in-the-loop governance over extracted action items.

Operations:
- approve(): PENDING_REVIEW -> APPROVED (records APPROVE audit log)
- reject():  PENDING_REVIEW -> REJECTED (records REJECT audit log)
- edit():    Updates title, owner, due_date, priority (records EDIT audit log)

NO EXTERNAL INTEGRATION IS EVER TRIGGERED HERE.
External side-effects happen strictly in SyncService after approval.
"""

from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.models.models import ActionItem
from app.models.enums import ActionStatus, Priority, AuditEventType, AuditActor
from app.workflow.state_machine import StateMachine
from app.services.business.audit_service import AuditService
from app.core.exceptions import ActionItemNotFoundError
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


class ApprovalService:
    """Service handling human review, editing, approval, and rejection of action items."""

    @staticmethod
    def approve_action_item(
        db: Session, action_item_id: str, actor: str = "Human Reviewer"
    ) -> ActionItem:
        """
        Approve an action item for external syncing.

        Transitions status: PENDING_REVIEW -> APPROVED via StateMachine.
        Records APPROVE event in audit log.
        """
        item = db.query(ActionItem).filter(ActionItem.action_item_id == action_item_id).first()
        if not item:
            raise ActionItemNotFoundError(action_item_id)

        # Delegate state transition validation to StateMachine
        StateMachine.transition_action_item(item, ActionStatus.APPROVED)

        # Audit event
        AuditService.log_event(
            db=db,
            meeting_id=item.meeting_id,
            action_item_id=item.action_item_id,
            event_type=AuditEventType.APPROVE,
            actor=AuditActor.HUMAN_USER,
            payload={"approved_by": actor, "task_title": item.title, "owner": item.owner},
        )

        db.commit()
        db.refresh(item)
        logger.info(f"[{LogEvent.APPROVE}] Action item '{item.action_item_id[:8]}' APPROVED by {actor}")
        return item

    @staticmethod
    def reject_action_item(
        db: Session, action_item_id: str, reason: Optional[str] = None, actor: str = "Human Reviewer"
    ) -> ActionItem:
        """
        Reject an action item.

        Transitions status: PENDING_REVIEW -> REJECTED via StateMachine.
        Records REJECT event in audit log.
        """
        item = db.query(ActionItem).filter(ActionItem.action_item_id == action_item_id).first()
        if not item:
            raise ActionItemNotFoundError(action_item_id)

        # Delegate state transition validation to StateMachine
        StateMachine.transition_action_item(item, ActionStatus.REJECTED)

        # Audit event
        AuditService.log_event(
            db=db,
            meeting_id=item.meeting_id,
            action_item_id=item.action_item_id,
            event_type=AuditEventType.REJECT,
            actor=AuditActor.HUMAN_USER,
            payload={"rejected_by": actor, "reason": reason or "Rejected by human reviewer", "task_title": item.title},
        )

        db.commit()
        db.refresh(item)
        logger.info(f"[{LogEvent.REJECT}] Action item '{item.action_item_id[:8]}' REJECTED by {actor}")
        return item

    @staticmethod
    def edit_action_item(
        db: Session,
        action_item_id: str,
        title: Optional[str] = None,
        owner: Optional[str] = None,
        due_date: Optional[date] = None,
        priority: Optional[Priority] = None,
        actor: str = "Human Reviewer",
    ) -> ActionItem:
        """
        Edit editable fields of an action item before approval.

        Allowed fields: title, owner, due_date, priority.
        Records EDIT event in audit log capturing previous vs new values.
        """
        item = db.query(ActionItem).filter(ActionItem.action_item_id == action_item_id).first()
        if not item:
            raise ActionItemNotFoundError(action_item_id)

        changes = {}

        if title is not None and title != item.title:
            changes["title"] = {"old": item.title, "new": title}
            item.title = title

        if owner is not None and owner != item.owner:
            changes["owner"] = {"old": item.owner, "new": owner}
            item.owner = owner

        if due_date is not None and due_date != item.due_date:
            changes["due_date"] = {
                "old": str(item.due_date) if item.due_date else None,
                "new": str(due_date),
            }
            item.due_date = due_date

        if priority is not None and priority != item.priority:
            changes["priority"] = {"old": item.priority.value, "new": priority.value}
            item.priority = priority

        if changes:
            AuditService.log_event(
                db=db,
                meeting_id=item.meeting_id,
                action_item_id=item.action_item_id,
                event_type=AuditEventType.EDIT,
                actor=AuditActor.HUMAN_USER,
                payload={"edited_by": actor, "changes": changes},
            )
            db.commit()
            db.refresh(item)
            logger.info(f"[{LogEvent.EDIT}] Action item '{item.action_item_id[:8]}' EDITED by {actor}: {list(changes.keys())}")

        return item
