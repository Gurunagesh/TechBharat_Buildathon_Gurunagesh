"""
models/models.py
────────────────
SQLAlchemy ORM models.

One class per database table. Column names, types, and constraints
mirror database/schema.sql exactly — that file is the canonical source
of truth. Any change to schema.sql must be reflected here and vice versa.

Relationships are defined with back_populates for bidirectional access.
"""

import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    Column, String, Text, Date, DateTime, Enum as SAEnum,
    DECIMAL, Integer, JSON, ForeignKey, UniqueConstraint,
    Index, func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base
from app.models.enums import (
    ProcessingStatus, ActionStatus, Priority,
    AuditEventType, AuditActor, SyncStatus,
)


def _new_uuid() -> str:
    """Generate a new UUID4 string (used as default primary key)."""
    return str(uuid.uuid4())


# ── Meeting ────────────────────────────────────────────────────────
class Meeting(Base):
    """
    Root entity representing one uploaded transcript.

    State machine:
        UPLOADING → PARSING → EXTRACTING → VALIDATING → READY_FOR_REVIEW → COMPLETED
                                                                          → FAILED
    """
    __tablename__ = "meetings"

    meeting_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_new_uuid
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, default="Untitled Meeting"
    )
    meeting_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    transcript_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True,
        comment="SHA-256 hex digest — idempotency key"
    )
    transcript_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decisions: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="JSON array of decision strings"
    )
    risks: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="JSON array of risk strings"
    )
    open_questions: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="JSON array of open question strings"
    )
    participants_raw: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="JSON array of participant objects from AI"
    )
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SAEnum(ProcessingStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProcessingStatus.UPLOADING,
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # ── Relationships ─────────────────────────────────────────────
    participants: Mapped[List["Participant"]] = relationship(
        "Participant", back_populates="meeting", cascade="all, delete-orphan"
    )
    action_items: Mapped[List["ActionItem"]] = relationship(
        "ActionItem", back_populates="meeting", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="meeting", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Meeting id={self.meeting_id[:8]} status={self.processing_status}>"


# ── Participant ────────────────────────────────────────────────────
class Participant(Base):
    """One person identified in a meeting. N participants per meeting."""
    __tablename__ = "participants"

    participant_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_new_uuid
    )
    meeting_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meetings.meeting_id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # ── Relationships ─────────────────────────────────────────────
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="participants")

    def __repr__(self) -> str:
        return f"<Participant name={self.name} meeting={self.meeting_id[:8]}>"


# ── ActionItem ────────────────────────────────────────────────────
class ActionItem(Base):
    """
    Core business entity — one extracted task per row.

    State machine (enforced by workflow/state_machine.py):
        PENDING_REVIEW → APPROVED → SYNCED
        PENDING_REVIEW → REJECTED
    """
    __tablename__ = "action_items"

    action_item_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_new_uuid
    )
    meeting_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meetings.meeting_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(
        String(255), nullable=False, default="UNASSIGNED"
    )
    owner_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[Priority] = mapped_column(
        SAEnum(Priority, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=Priority.MEDIUM,
    )
    confidence_score: Mapped[float] = mapped_column(
        DECIMAL(4, 3), nullable=False, default=0.0,
        comment="AI certainty 0.000–1.000"
    )
    evidence_quote: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Exact transcript snippet"
    )
    status: Mapped[ActionStatus] = mapped_column(
        SAEnum(ActionStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ActionStatus.PENDING_REVIEW,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # ── Relationships ─────────────────────────────────────────────
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="action_items")
    github_sync: Mapped[Optional["GitHubSync"]] = relationship(
        "GitHubSync", back_populates="action_item",
        cascade="all, delete-orphan", uselist=False
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="action_item"
    )

    def __repr__(self) -> str:
        return f"<ActionItem id={self.action_item_id[:8]} status={self.status} owner={self.owner}>"


# ── GitHubSync ────────────────────────────────────────────────────
class GitHubSync(Base):
    """
    Tracks GitHub synchronization for one action item.
    One row per action item (UNIQUE constraint).

    Designed for extensibility: SlackSync, CalendarSync can follow the same pattern.
    """
    __tablename__ = "github_syncs"

    sync_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_new_uuid
    )
    action_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("action_items.action_item_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    github_issue_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    github_issue_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    github_issue_title: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    sync_status: Mapped[SyncStatus] = mapped_column(
        SAEnum(SyncStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SyncStatus.PENDING,
    )
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # ── Relationships ─────────────────────────────────────────────
    action_item: Mapped["ActionItem"] = relationship(
        "ActionItem", back_populates="github_sync"
    )

    def __repr__(self) -> str:
        return f"<GitHubSync action={self.action_item_id[:8]} status={self.sync_status}>"


# ── AuditLog ──────────────────────────────────────────────────────
class AuditLog(Base):
    """
    Immutable event history.

    IMPORTANT: Rows are NEVER updated after insertion.
    The audit log is the system's ground truth for what happened and when.
    """
    __tablename__ = "audit_logs"

    audit_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_new_uuid
    )
    meeting_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meetings.meeting_id", ondelete="CASCADE"), nullable=False
    )
    action_item_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("action_items.action_item_id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type: Mapped[AuditEventType] = mapped_column(
        SAEnum(AuditEventType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    actor: Mapped[AuditActor] = mapped_column(
        SAEnum(AuditActor, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AuditActor.SYSTEM,
    )
    payload: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="Additional event context"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    # ── Relationships ─────────────────────────────────────────────
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="audit_logs")
    action_item: Mapped[Optional["ActionItem"]] = relationship(
        "ActionItem", back_populates="audit_logs"
    )

    def __repr__(self) -> str:
        return f"<AuditLog event={self.event_type} actor={self.actor}>"
