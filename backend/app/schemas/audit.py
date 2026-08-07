"""
schemas/audit.py
────────────────
Pydantic API Schemas for Audit Logs.

Decouples AuditLog ORM models from the public API layer.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.enums import AuditEventType, AuditActor


class AuditLogResponse(BaseModel):
    """Pydantic model representing an audit log entry in API responses."""
    model_config = ConfigDict(from_attributes=True)

    audit_id: str
    meeting_id: str
    action_item_id: Optional[str] = None
    event_type: AuditEventType
    actor: AuditActor
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime
