"""
services/business/meeting_service.py
─────────────────────────────────────
Meeting & Action Item Query Service.

Provides read, list, filter, and detail access for Meetings, Action Items,
Participants, and Audit Trails.

Rule: Keep read/query logic clean and separated from processing & LLM services.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.models import Meeting, ActionItem, Participant, AuditLog
from app.models.enums import ProcessingStatus, ActionStatus
from app.core.exceptions import MeetingNotFoundError, ActionItemNotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


class MeetingService:
    """Service providing query and retrieval operations for meetings and action items."""

    @staticmethod
    def get_meeting_by_id(db: Session, meeting_id: str) -> Meeting:
        """
        Fetch a single Meeting by UUID with all relations (participants, action_items, audit_logs) eagerly loaded.
        Raises MeetingNotFoundError if missing.
        """
        meeting = (
            db.query(Meeting)
            .options(
                joinedload(Meeting.participants),
                joinedload(Meeting.action_items).joinedload(ActionItem.github_sync),
                joinedload(Meeting.audit_logs),
            )
            .filter(Meeting.meeting_id == meeting_id)
            .first()
        )
        if not meeting:
            raise MeetingNotFoundError(meeting_id)
        return meeting

    @staticmethod
    def list_meetings(
        db: Session,
        status: Optional[ProcessingStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Meeting]:
        """List meetings ordered by created_at DESC with optional status filter."""
        query = db.query(Meeting)
        if status:
            query = query.filter(Meeting.processing_status == status)
        return query.order_by(Meeting.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_meeting_action_items(
        db: Session,
        meeting_id: str,
        status: Optional[ActionStatus] = None,
    ) -> List[ActionItem]:
        """Fetch all action items for a given meeting, optionally filtered by ActionStatus."""
        # Ensure meeting exists
        MeetingService.get_meeting_by_id(db, meeting_id)

        query = (
            db.query(ActionItem)
            .options(joinedload(ActionItem.github_sync))
            .filter(ActionItem.meeting_id == meeting_id)
        )
        if status:
            query = query.filter(ActionItem.status == status)

        return query.order_by(ActionItem.created_at.asc()).all()

    @staticmethod
    def get_action_item_by_id(db: Session, action_item_id: str) -> ActionItem:
        """Fetch a single ActionItem by UUID. Raises ActionItemNotFoundError if missing."""
        item = (
            db.query(ActionItem)
            .options(joinedload(ActionItem.github_sync))
            .filter(ActionItem.action_item_id == action_item_id)
            .first()
        )
        if not item:
            raise ActionItemNotFoundError(action_item_id)
        return item
