"""
workflow/transitions.py
───────────────────────
Explicit state transition definitions.

Defines the directed graph of allowed state transitions for:
1. Meeting ProcessingStatus
2. ActionItem ActionStatus

Rules:
- Transitions not explicitly defined in these maps are ILLEGAL.
- Any attempt to transition to an illegal state will raise InvalidStateTransitionError.
"""

from typing import Dict, Set
from app.models.enums import ProcessingStatus, ActionStatus

# ── Meeting Processing Status Transitions ─────────────────────────
# Maps current status -> set of allowed target statuses
MEETING_TRANSITIONS: Dict[ProcessingStatus, Set[ProcessingStatus]] = {
    ProcessingStatus.UPLOADING: {
        ProcessingStatus.PARSING,
        ProcessingStatus.FAILED,
    },
    ProcessingStatus.PARSING: {
        ProcessingStatus.EXTRACTING,
        ProcessingStatus.FAILED,
    },
    ProcessingStatus.EXTRACTING: {
        ProcessingStatus.VALIDATING,
        ProcessingStatus.FAILED,
    },
    ProcessingStatus.VALIDATING: {
        ProcessingStatus.READY_FOR_REVIEW,
        ProcessingStatus.FAILED,
    },
    ProcessingStatus.READY_FOR_REVIEW: {
        ProcessingStatus.COMPLETED,
        ProcessingStatus.FAILED,
    },
    ProcessingStatus.COMPLETED: set(),  # Terminal state
    ProcessingStatus.FAILED: {
        ProcessingStatus.UPLOADING,    # Allow retry from start
        ProcessingStatus.PARSING,
        ProcessingStatus.EXTRACTING,
    },
}

# ── Action Item Status Transitions ────────────────────────────────
# Maps current status -> set of allowed target statuses
ACTION_ITEM_TRANSITIONS: Dict[ActionStatus, Set[ActionStatus]] = {
    ActionStatus.PENDING_REVIEW: {
        ActionStatus.APPROVED,
        ActionStatus.REJECTED,
    },
    ActionStatus.APPROVED: {
        ActionStatus.SYNCED,
        ActionStatus.REJECTED,         # Can reject an approved item before sync
    },
    ActionStatus.REJECTED: set(),      # Terminal state — rejection is final
    ActionStatus.SYNCED: set(),        # Terminal state — cannot go back once synced to GitHub
}
