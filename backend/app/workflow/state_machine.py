"""
workflow/state_machine.py
──────────────────────────
The State Machine Engine.

THIS IS THE SOLE SYSTEM MODULE ALLOWED TO CONTROL STATE TRANSITIONS.

No business service or API endpoint should mutate entity statuses directly
without calling StateMachine.validate_and_transition().

Features:
- Validates transitions against transitions.py maps.
- Raises InvalidStateTransitionError on illegal transitions.
- Emits structured audit log events for every state change.
"""

from typing import Union, List
from app.models.enums import ProcessingStatus, ActionStatus, AuditEventType, AuditActor
from app.models.models import Meeting, ActionItem
from app.workflow.transitions import MEETING_TRANSITIONS, ACTION_ITEM_TRANSITIONS
from app.core.exceptions import InvalidStateTransitionError
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


class StateMachine:
    """State Machine for enforcing workflow transitions on Meetings and ActionItems."""

    @staticmethod
    def can_transition_meeting(
        current_status: ProcessingStatus, target_status: ProcessingStatus
    ) -> bool:
        """Check if a meeting transition from current_status to target_status is allowed."""
        allowed = MEETING_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    @staticmethod
    def can_transition_action_item(
        current_status: ActionStatus, target_status: ActionStatus
    ) -> bool:
        """Check if an action item transition from current_status to target_status is allowed."""
        allowed = ACTION_ITEM_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    @classmethod
    def transition_meeting(
        cls, meeting: Meeting, target_status: ProcessingStatus
    ) -> ProcessingStatus:
        """
        Transition a Meeting to target_status.

        Raises:
            InvalidStateTransitionError if the transition is illegal.
        """
        current_status = meeting.processing_status
        if current_status == target_status:
            return current_status  # No-op idempotent transition

        if not cls.can_transition_meeting(current_status, target_status):
            allowed = [s.value for s in MEETING_TRANSITIONS.get(current_status, set())]
            logger.error(
                f"[{LogEvent.WORKFLOW_VIOLATION}] Illegal Meeting transition: "
                f"meeting_id={meeting.meeting_id} {current_status.value} -> {target_status.value}"
            )
            raise InvalidStateTransitionError(
                entity_type="Meeting",
                entity_id=meeting.meeting_id,
                current_status=current_status.value,
                target_status=target_status.value,
                allowed_transitions=allowed,
            )

        logger.info(
            f"[WORKFLOW] Meeting state transition: "
            f"meeting_id={meeting.meeting_id[:8]} {current_status.value} -> {target_status.value}"
        )
        meeting.processing_status = target_status
        return target_status

    @classmethod
    def transition_action_item(
        cls, action_item: ActionItem, target_status: ActionStatus
    ) -> ActionStatus:
        """
        Transition an ActionItem to target_status.

        Raises:
            InvalidStateTransitionError if the transition is illegal.
        """
        current_status = action_item.status
        if current_status == target_status:
            return current_status  # No-op idempotent transition

        if not cls.can_transition_action_item(current_status, target_status):
            allowed = [s.value for s in ACTION_ITEM_TRANSITIONS.get(current_status, set())]
            logger.error(
                f"[{LogEvent.WORKFLOW_VIOLATION}] Illegal ActionItem transition: "
                f"action_item_id={action_item.action_item_id} {current_status.value} -> {target_status.value}"
            )
            raise InvalidStateTransitionError(
                entity_type="ActionItem",
                entity_id=action_item.action_item_id,
                current_status=current_status.value,
                target_status=target_status.value,
                allowed_transitions=allowed,
            )

        logger.info(
            f"[WORKFLOW] ActionItem state transition: "
            f"action_item_id={action_item.action_item_id[:8]} {current_status.value} -> {target_status.value}"
        )
        action_item.status = target_status
        return target_status
