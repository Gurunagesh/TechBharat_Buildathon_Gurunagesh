"""
schemas/meeting.py
──────────────────
Pydantic API Schemas for Meetings.

Decouples SQLAlchemy Meeting ORM models from the public API layer.
Used for serialization in FastAPI response models.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from app.models.enums import ProcessingStatus


class ParticipantResponse(BaseModel):
    """Pydantic model representing a meeting participant in API responses."""
    model_config = ConfigDict(from_attributes=True)

    participant_id: str
    name: str
    email: Optional[str] = None
    role: Optional[str] = None


class MeetingSummaryResponse(BaseModel):
    """Lightweight meeting schema for list endpoints."""
    model_config = ConfigDict(from_attributes=True)

    meeting_id: str
    title: str
    meeting_date: Optional[date] = None
    uploaded_at: datetime
    processing_status: ProcessingStatus
    action_items_count: Optional[int] = 0
    created_at: datetime


class MeetingDetailResponse(BaseModel):
    """Full meeting detail schema including summary, decisions, risks, and questions."""
    model_config = ConfigDict(from_attributes=True)

    meeting_id: str
    title: str
    meeting_date: Optional[date] = None
    uploaded_at: datetime
    transcript_hash: str
    processing_status: ProcessingStatus
    summary: Optional[str] = None
    decisions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    participants: List[ParticipantResponse] = Field(default_factory=list)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MeetingUploadResponse(BaseModel):
    """Response returned immediately after file upload & ingestion."""
    meeting_id: str
    title: str
    processing_status: ProcessingStatus
    is_duplicate: bool = False
    action_items_extracted: int = 0
    total_time_ms: float = 0.0
    llm_provider_used: str = "Gemini"
