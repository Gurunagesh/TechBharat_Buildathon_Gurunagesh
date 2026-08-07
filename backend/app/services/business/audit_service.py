"""
services/business/audit_service.py
───────────────────────────────────
Audit Trail Service.

Responsible for writing immutable log entries to the audit_logs table.

Rules:
- Audit entries are append-only. No UPDATE or DELETE methods exist.
- Every important system or human action MUST trigger an audit log.
- Never crash the main business transaction if audit writing encounters a minor error (logs warning).
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.models import AuditLog
from app.models.enums import AuditEventType, AuditActor
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


class AuditService:
    """Service for creating append-only audit trail records."""

    @staticmethod
    def log_event(
        db: Session,
        meeting_id: str,
        event_type: AuditEventType,
        actor: AuditActor = AuditActor.SYSTEM,
        action_item_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Create and persist a new immutable AuditLog entry.

        Args:
            db: Active SQLAlchemy database session.
            meeting_id: Meeting UUID associated with this event.
            event_type: Named AuditEventType (UPLOAD, EXTRACT, APPROVE, SYNC, etc.)
            actor: AuditActor (AI_AGENT, HUMAN_USER, SYSTEM)
            action_item_id: Optional ActionItem UUID if item-specific.
            payload: Additional JSON-serializable dictionary context.

        Returns:
            The persisted AuditLog object.
        """
        audit_entry = AuditLog(
            meeting_id=meeting_id,
            action_item_id=action_item_id,
            event_type=event_type,
            actor=actor,
            payload=payload or {},
        )
        db.add(audit_entry)
        # Flush to generate audit_id without committing transaction
        db.flush()

        logger.info(
            f"[AUDIT] event={event_type.value} actor={actor.value} "
            f"meeting_id={meeting_id[:8]} action_item_id={action_item_id[:8] if action_item_id else 'N/A'}"
        )
        return audit_entry

    @staticmethod
    def get_meeting_audit_trail(db: Session, meeting_id: str) -> list[AuditLog]:
        """Fetch all audit log entries for a given meeting ordered chronologically."""
        return (
            db.query(AuditLog)
            .filter(AuditLog.meeting_id == meeting_id)
            .order_by(AuditLog.created_at.asc())
            .all()
        )
