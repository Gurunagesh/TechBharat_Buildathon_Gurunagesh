"""
services/llm/schemas.py
───────────────────────
Pydantic Extraction Schemas for LLM Structured Outputs.

These schemas define the strict JSON contract returned by Gemini 1.5-flash / Grok.
If the LLM returns JSON violating these schemas, validation fails before hitting MySQL.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ExtractedActionItem(BaseModel):
    """Pydantic model representing one AI-extracted action item."""
    title: str = Field(
        description="Action item task description. Clear, actionable summary of what needs to be done."
    )
    owner: str = Field(
        default="UNASSIGNED",
        description="Person assigned to the task, or UNASSIGNED if no clear owner was specified."
    )
    due_date: Optional[str] = Field(
        default=None,
        description="Raw or relative due date mentioned in transcript (e.g., 'next Friday', '2026-08-15', 'end of month')."
    )
    priority: str = Field(
        default="MEDIUM",
        description="Priority level: HIGH, MEDIUM, or LOW."
    )
    confidence_score: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 estimating AI certainty of this action item."
    )
    evidence_quote: str = Field(
        description="Exact quote snippet from transcript where this task was agreed upon."
    )


class ExtractedParticipant(BaseModel):
    """Pydantic model representing one identified meeting participant."""
    name: str = Field(description="Participant full or first name.")
    email: Optional[str] = Field(default=None, description="Email address if mentioned or inferable.")
    role: Optional[str] = Field(default=None, description="Role or job title if mentioned.")


class ExtractedMeetingInfo(BaseModel):
    """Pydantic model representing the complete multi-pass AI extraction output."""
    title: str = Field(
        default="Meeting Recap",
        description="Suggested concise title for the meeting."
    )
    meeting_date_mentioned: Optional[str] = Field(
        default=None,
        description="Meeting date if explicitly stated in text (e.g. 'Wednesday, Aug 5, 2026')."
    )
    summary: str = Field(
        description="Executive summary of the meeting (2-4 concise paragraphs)."
    )
    decisions: List[str] = Field(
        default_factory=list,
        description="List of key decisions made during the meeting."
    )
    risks: List[str] = Field(
        default_factory=list,
        description="List of risks, blockers, or concerns raised during the meeting."
    )
    open_questions: List[str] = Field(
        default_factory=list,
        description="List of unresolved questions or discussion points."
    )
    participants: List[ExtractedParticipant] = Field(
        default_factory=list,
        description="List of meeting participants identified in transcript."
    )
    action_items: List[ExtractedActionItem] = Field(
        default_factory=list,
        description="List of actionable task commitments extracted from transcript."
    )
