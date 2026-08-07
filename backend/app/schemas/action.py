"""
schemas/action.py
─────────────────
Pydantic API Schemas for Action Items & GitHub Syncs.

Decouples ActionItem ORM models from the public API layer.
Includes validation for human edit requests (ActionItemEditRequest).
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from app.models.enums import ActionStatus, Priority, SyncStatus


class GitHubSyncResponse(BaseModel):
    """Schema representing a GitHub Issue sync record in API responses."""
    model_config = ConfigDict(from_attributes=True)

    sync_id: str
    github_issue_number: Optional[int] = None
    github_issue_url: Optional[str] = None
    github_issue_title: Optional[str] = None
    sync_status: SyncStatus
    synced_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ActionItemResponse(BaseModel):
    """Pydantic model representing an action item in API responses."""
    model_config = ConfigDict(from_attributes=True)

    action_item_id: str
    meeting_id: str
    title: str
    description: Optional[str] = None
    owner: str
    owner_email: Optional[str] = None
    due_date: Optional[date] = None
    priority: Priority
    confidence_score: float
    evidence_quote: Optional[str] = None
    status: ActionStatus
    github_sync: Optional[GitHubSyncResponse] = None
    created_at: datetime
    updated_at: datetime


class ActionItemEditRequest(BaseModel):
    """Payload schema for human editing of an action item before approval."""
    title: Optional[str] = Field(default=None, max_length=512, description="New task title")
    owner: Optional[str] = Field(default=None, max_length=255, description="New owner name or UNASSIGNED")
    due_date: Optional[date] = Field(default=None, description="New due date (YYYY-MM-DD)")
    priority: Optional[Priority] = Field(default=None, description="New priority: HIGH, MEDIUM, LOW")


class ActionItemRejectRequest(BaseModel):
    """Payload schema for rejecting an action item."""
    reason: Optional[str] = Field(default=None, max_length=500, description="Optional rejection reason")


class SyncSummaryResponse(BaseModel):
    """Response model for POST /api/v1/meetings/{id}/sync endpoint."""
    meeting_id: str
    total_synced: int
    items: list[dict]
