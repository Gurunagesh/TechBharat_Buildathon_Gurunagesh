"""
models/enums.py
───────────────
Centralized enum definitions for all database state columns.

Every module that references a status, priority, event type, or actor
imports from here instead of using raw strings.

Rule: If a value appears in a status column, it lives in this file.
"""

from enum import Enum


# ── Meeting Processing States ─────────────────────────────────────
class ProcessingStatus(str, Enum):
    """
    Lifecycle of a meeting from upload to completion.
    Controlled exclusively by workflow/state_machine.py.
    """
    UPLOADING = "UPLOADING"
    PARSING = "PARSING"
    EXTRACTING = "EXTRACTING"
    VALIDATING = "VALIDATING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ── Action Item States ────────────────────────────────────────────
class ActionStatus(str, Enum):
    """
    Lifecycle of an extracted action item.
    Controlled exclusively by workflow/state_machine.py.

    Valid transitions:
        PENDING_REVIEW → APPROVED → SYNCED
        PENDING_REVIEW → REJECTED

    Invalid (raises MeetingWorkflowError):
        SYNCED → PENDING_REVIEW  (cannot go back)
        REJECTED → APPROVED      (reject is final)
    """
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SYNCED = "SYNCED"


# ── Action Item Priority ──────────────────────────────────────────
class Priority(str, Enum):
    """Priority levels assigned by LLM (validated by Pydantic)."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ── Audit Log Event Types ─────────────────────────────────────────
class AuditEventType(str, Enum):
    """
    Named events recorded in the audit_logs table.
    Maps directly to LogEvent constants in core/logging.py.
    """
    UPLOAD = "UPLOAD"
    PARSE = "PARSE"
    DUPLICATE_DETECTED = "DUPLICATE_DETECTED"
    EXTRACT = "EXTRACT"
    VALIDATE = "VALIDATE"
    RESOLVE = "RESOLVE"
    EDIT = "EDIT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SYNC = "SYNC"
    GITHUB_SUCCESS = "GITHUB_SUCCESS"
    GITHUB_FAILURE = "GITHUB_FAILURE"
    LLM_RETRY = "LLM_RETRY"
    LLM_FALLBACK = "LLM_FALLBACK"
    PROCESSING_FAILED = "PROCESSING_FAILED"


# ── Audit Log Actor Types ─────────────────────────────────────────
class AuditActor(str, Enum):
    """Who triggered the audit event — AI agent or human user."""
    AI_AGENT = "AI_AGENT"
    HUMAN_USER = "HUMAN_USER"
    SYSTEM = "SYSTEM"


# ── GitHub Sync Status ────────────────────────────────────────────
class SyncStatus(str, Enum):
    """State of a GitHub synchronization attempt."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
