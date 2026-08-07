"""
tests/test_state_machine.py
────────────────────────────
Unit tests for Sprint 2A Workflow State Machine.

Verifies:
1. All valid transitions succeed.
2. Invalid transitions raise InvalidStateTransitionError with correct error_code.
3. No-op transitions return current status cleanly.
4. Terminal states block further transitions.
"""

import pytest
from app.models.enums import ProcessingStatus, ActionStatus
from app.models.models import Meeting, ActionItem
from app.workflow.state_machine import StateMachine
from app.core.exceptions import InvalidStateTransitionError


# ── Meeting State Machine Tests ───────────────────────────────────
def test_valid_meeting_workflow():
    """Test standard linear lifecycle: UPLOADING -> PARSING -> EXTRACTING -> VALIDATING -> READY_FOR_REVIEW -> COMPLETED."""
    meeting = Meeting(meeting_id="test-meeting-123", transcript_hash="abc123hash")
    assert meeting.processing_status == ProcessingStatus.UPLOADING

    # UPLOADING -> PARSING
    status = StateMachine.transition_meeting(meeting, ProcessingStatus.PARSING)
    assert status == ProcessingStatus.PARSING

    # PARSING -> EXTRACTING
    status = StateMachine.transition_meeting(meeting, ProcessingStatus.EXTRACTING)
    assert status == ProcessingStatus.EXTRACTING

    # EXTRACTING -> VALIDATING
    status = StateMachine.transition_meeting(meeting, ProcessingStatus.VALIDATING)
    assert status == ProcessingStatus.VALIDATING

    # VALIDATING -> READY_FOR_REVIEW
    status = StateMachine.transition_meeting(meeting, ProcessingStatus.READY_FOR_REVIEW)
    assert status == ProcessingStatus.READY_FOR_REVIEW

    # READY_FOR_REVIEW -> COMPLETED
    status = StateMachine.transition_meeting(meeting, ProcessingStatus.COMPLETED)
    assert status == ProcessingStatus.COMPLETED


def test_invalid_meeting_transition_raises_error():
    """Test that skipping states (e.g. UPLOADING -> COMPLETED) raises InvalidStateTransitionError."""
    meeting = Meeting(meeting_id="test-meeting-456", transcript_hash="def456hash")

    with pytest.raises(InvalidStateTransitionError) as exc_info:
        StateMachine.transition_meeting(meeting, ProcessingStatus.COMPLETED)

    err = exc_info.value
    assert err.error_code == "ERR_ILLEGAL_TRANSITION"
    assert err.details["entity_type"] == "Meeting"
    assert err.details["current_status"] == "UPLOADING"
    assert err.details["target_status"] == "COMPLETED"


def test_meeting_failure_recovery_transition():
    """Test that a FAILED meeting can be retried back from UPLOADING, PARSING, or EXTRACTING."""
    meeting = Meeting(meeting_id="test-meeting-789", transcript_hash="ghi789hash")
    StateMachine.transition_meeting(meeting, ProcessingStatus.PARSING)
    StateMachine.transition_meeting(meeting, ProcessingStatus.FAILED)
    assert meeting.processing_status == ProcessingStatus.FAILED

    # Retry from PARSING
    status = StateMachine.transition_meeting(meeting, ProcessingStatus.PARSING)
    assert status == ProcessingStatus.PARSING


# ── ActionItem State Machine Tests ────────────────────────────────
def test_valid_action_item_approval_and_sync():
    """Test valid action item lifecycle: PENDING_REVIEW -> APPROVED -> SYNCED."""
    item = ActionItem(action_item_id="item-123", meeting_id="meeting-123", title="Test task")
    assert item.status == ActionStatus.PENDING_REVIEW

    # Approve
    status = StateMachine.transition_action_item(item, ActionStatus.APPROVED)
    assert status == ActionStatus.APPROVED

    # Sync
    status = StateMachine.transition_action_item(item, ActionStatus.SYNCED)
    assert status == ActionStatus.SYNCED


def test_valid_action_item_rejection():
    """Test action item rejection from PENDING_REVIEW."""
    item = ActionItem(action_item_id="item-456", meeting_id="meeting-123", title="Weak task")

    status = StateMachine.transition_action_item(item, ActionStatus.REJECTED)
    assert status == ActionStatus.REJECTED


def test_synced_action_item_is_terminal():
    """Test that once SYNCED to GitHub, an item CANNOT go back to PENDING_REVIEW or REJECTED."""
    item = ActionItem(action_item_id="item-789", meeting_id="meeting-123", title="Synced task")
    StateMachine.transition_action_item(item, ActionStatus.APPROVED)
    StateMachine.transition_action_item(item, ActionStatus.SYNCED)

    # Attempt illegal backward transition
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        StateMachine.transition_action_item(item, ActionStatus.PENDING_REVIEW)

    err = exc_info.value
    assert err.error_code == "ERR_ILLEGAL_TRANSITION"
    assert err.details["current_status"] == "SYNCED"
    assert err.details["target_status"] == "PENDING_REVIEW"


def test_idempotent_no_op_transition():
    """Test that transitioning to the current status is a valid no-op."""
    item = ActionItem(action_item_id="item-000", meeting_id="meeting-123", title="No-op task")

    # PENDING_REVIEW -> PENDING_REVIEW
    status = StateMachine.transition_action_item(item, ActionStatus.PENDING_REVIEW)
    assert status == ActionStatus.PENDING_REVIEW
