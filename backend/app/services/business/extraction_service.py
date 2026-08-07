"""
services/business/extraction_service.py
────────────────────────────────────────
AI Extraction Pipeline Orchestration Service.

Connects all deterministic and AI modules into a single production pipeline:

   Upload Bytes
        │
        ▼
   TranscriptParser (.txt, .vtt, .srt)
        │
        ▼
   DuplicateChecker (SHA-256 idempotency check)
        │
   Duplicate? ── Yes ──> Return Existing Meeting
        │ No
        ▼
   GeminiClient (or GrokClient fallback)
        │
        ▼
   Pydantic Validation (schemas.py)
        │
        ▼
   BusinessResolver (relative date & owner mapping)
        │
        ▼
   Database Persistence (Meeting, ActionItem, Participant)
        │
        ▼
   AuditLog Service (immutable audit trail)

Features:
- Records ExtractionMetrics (latency, provider, word count)
- Enforces strict human review state (action_items start as PENDING_REVIEW)
"""

import json
import time
from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.models import Meeting, ActionItem, Participant
from app.models.enums import ProcessingStatus, ActionStatus, AuditEventType, AuditActor
from app.workflow.state_machine import StateMachine
from app.services.business.transcript_parser import TranscriptParser
from app.services.business.duplicate_checker import DuplicateChecker
from app.services.business.resolver import BusinessResolver
from app.services.business.audit_service import AuditService
from app.services.llm.gemini_client import GeminiClient
from app.services.llm.grok_client import GrokClient
from app.services.llm.schemas import ExtractedMeetingInfo
from app.core.config import settings
from app.core.exceptions import LLMExtractionError, DuplicateTranscriptError
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


@dataclass
class ExtractionMetrics:
    """Performance and telemetry metrics for an extraction pipeline run."""
    filename: str
    format: str
    word_count: int
    parser_time_ms: float
    llm_time_ms: float
    resolver_time_ms: float
    total_time_ms: float
    llm_provider_used: str
    action_items_count: int
    decisions_count: int
    is_duplicate: bool = False


class ExtractionService:
    """High-level orchestration service for transcript ingestion and AI extraction."""

    @classmethod
    def process_transcript_file(
        cls,
        db: Session,
        filename: str,
        content_bytes: bytes,
        meeting_date: Optional[date] = None,
        known_participants: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[Meeting, ExtractionMetrics]:
        """
        Ingest a transcript file, run AI extraction pipeline, and persist to MySQL.

        Args:
            db: SQLAlchemy session.
            filename: Original file name (e.g. "team_sync.vtt")
            content_bytes: Raw upload content bytes.
            meeting_date: Optional explicit meeting date for date anchoring.
            known_participants: Optional list of team members for owner matching.

        Returns:
            Tuple of (persisted Meeting ORM object, ExtractionMetrics)
        """
        start_total = time.perf_counter()

        # ── Step 1: Parse Transcript ──────────────────────────────────
        start_parse = time.perf_counter()
        parsed_data = TranscriptParser.parse(filename, content_bytes)
        raw_text = parsed_data["raw_text"]
        parse_time_ms = round((time.perf_counter() - start_parse) * 1000, 2)

        # ── Step 2: Idempotency Duplicate Check ───────────────────────
        transcript_hash, existing_meeting = DuplicateChecker.check_duplicate(db, raw_text)
        if existing_meeting:
            total_ms = round((time.perf_counter() - start_total) * 1000, 2)
            metrics = ExtractionMetrics(
                filename=filename,
                format=parsed_data["format"],
                word_count=parsed_data["word_count"],
                parser_time_ms=parse_time_ms,
                llm_time_ms=0.0,
                resolver_time_ms=0.0,
                total_time_ms=total_ms,
                llm_provider_used="None (Cached)",
                action_items_count=len(existing_meeting.action_items),
                decisions_count=len(json.loads(existing_meeting.decisions or "[]")),
                is_duplicate=True,
            )
            AuditService.log_event(
                db=db,
                meeting_id=existing_meeting.meeting_id,
                event_type=AuditEventType.DUPLICATE_DETECTED,
                actor=AuditActor.SYSTEM,
                payload={"transcript_hash": transcript_hash, "metrics": asdict(metrics)},
            )
            db.commit()
            return existing_meeting, metrics

        # ── Step 3: Create Initial Meeting Record (UPLOADING state) ───
        meeting = Meeting(
            title=filename.rsplit(".", 1)[0].replace("_", " ").title(),
            meeting_date=meeting_date or date.today(),
            transcript_hash=transcript_hash,
            transcript_text=raw_text,
            processing_status=ProcessingStatus.UPLOADING,
        )
        db.add(meeting)
        db.flush()

        # Audit: Upload
        AuditService.log_event(
            db=db,
            meeting_id=meeting.meeting_id,
            event_type=AuditEventType.UPLOAD,
            actor=AuditActor.HUMAN_USER,
            payload={"filename": filename, "word_count": parsed_data["word_count"]},
        )

        try:
            # Transition: UPLOADING -> PARSING -> EXTRACTING
            StateMachine.transition_meeting(meeting, ProcessingStatus.PARSING)
            AuditService.log_event(
                db=db,
                meeting_id=meeting.meeting_id,
                event_type=AuditEventType.PARSE,
                actor=AuditActor.SYSTEM,
                payload={"lines_count": len(parsed_data["lines"])},
            )
            StateMachine.transition_meeting(meeting, ProcessingStatus.EXTRACTING)

            # ── Step 4: Invoke LLM Layer (Gemini with Grok fallback) ──
            start_llm = time.perf_counter()
            anchor_date_str = str(meeting.meeting_date)
            provider_used = "Gemini"

            try:
                extracted_info = GeminiClient.extract_meeting_info(
                    transcript_text=raw_text,
                    anchor_date=anchor_date_str,
                    known_participants=known_participants,
                )
            except LLMExtractionError as gemini_err:
                logger.warning(f"[EXTRACTION] Gemini failed: {gemini_err}. Checking Grok fallback...")
                if settings.enable_grok_fallback and settings.grok_api_key:
                    provider_used = "Grok (Fallback)"
                    AuditService.log_event(
                        db=db,
                        meeting_id=meeting.meeting_id,
                        event_type=AuditEventType.LLM_FALLBACK,
                        actor=AuditActor.SYSTEM,
                        payload={"reason": str(gemini_err)},
                    )
                    extracted_info = GrokClient.extract_meeting_info(
                        transcript_text=raw_text,
                        anchor_date=anchor_date_str,
                        known_participants=known_participants,
                    )
                else:
                    raise gemini_err

            llm_time_ms = round((time.perf_counter() - start_llm) * 1000, 2)

            # Transition: EXTRACTING -> VALIDATING
            StateMachine.transition_meeting(meeting, ProcessingStatus.VALIDATING)
            AuditService.log_event(
                db=db,
                meeting_id=meeting.meeting_id,
                event_type=AuditEventType.EXTRACT,
                actor=AuditActor.AI_AGENT,
                payload={
                    "provider": provider_used,
                    "action_items_extracted": len(extracted_info.action_items),
                    "decisions_extracted": len(extracted_info.decisions),
                },
            )

            # ── Step 5: Deterministic Business Resolver ───────────────
            start_resolve = time.perf_counter()

            meeting.title = extracted_info.title or meeting.title
            meeting.summary = extracted_info.summary
            meeting.decisions = json.dumps(extracted_info.decisions)
            meeting.risks = json.dumps(extracted_info.risks)
            meeting.open_questions = json.dumps(extracted_info.open_questions)
            meeting.participants_raw = json.dumps(
                [p.model_dump() for p in extracted_info.participants]
            )

            # Resolve participants into DB rows
            for p in extracted_info.participants:
                resolved_owner, resolved_email = BusinessResolver.resolve_owner(
                    p.name, known_participants
                )
                db.add(
                    Participant(
                        meeting_id=meeting.meeting_id,
                        name=resolved_owner if resolved_owner != "UNASSIGNED" else p.name,
                        email=resolved_email or p.email,
                        role=p.role,
                    )
                )

            # Resolve Action Items into DB rows
            for raw_task in extracted_info.action_items:
                resolved_owner, owner_email = BusinessResolver.resolve_owner(
                    raw_task.owner, known_participants
                )
                resolved_due = BusinessResolver.resolve_date(
                    raw_task.due_date, anchor_date=meeting.meeting_date
                )
                resolved_priority = BusinessResolver.resolve_priority(raw_task.priority)
                sanitized_confidence = BusinessResolver.sanitize_confidence_score(
                    raw_task.confidence_score
                )

                action_item = ActionItem(
                    meeting_id=meeting.meeting_id,
                    title=raw_task.title,
                    description=None,
                    owner=resolved_owner,
                    owner_email=owner_email,
                    due_date=resolved_due,
                    priority=resolved_priority,
                    confidence_score=sanitized_confidence,
                    evidence_quote=raw_task.evidence_quote,
                    status=ActionStatus.PENDING_REVIEW,  # Human-in-the-loop rule
                )
                db.add(action_item)

            resolve_time_ms = round((time.perf_counter() - start_resolve) * 1000, 2)

            # Transition: VALIDATING -> READY_FOR_REVIEW
            StateMachine.transition_meeting(meeting, ProcessingStatus.READY_FOR_REVIEW)
            AuditService.log_event(
                db=db,
                meeting_id=meeting.meeting_id,
                event_type=AuditEventType.RESOLVE,
                actor=AuditActor.SYSTEM,
                payload={"action_items_resolved": len(extracted_info.action_items)},
            )

            total_ms = round((time.perf_counter() - start_total) * 1000, 2)
            metrics = ExtractionMetrics(
                filename=filename,
                format=parsed_data["format"],
                word_count=parsed_data["word_count"],
                parser_time_ms=parse_time_ms,
                llm_time_ms=llm_time_ms,
                resolver_time_ms=resolve_time_ms,
                total_time_ms=total_ms,
                llm_provider_used=provider_used,
                action_items_count=len(extracted_info.action_items),
                decisions_count=len(extracted_info.decisions),
                is_duplicate=False,
            )

            db.commit()
            db.refresh(meeting)
            logger.info(
                f"[EXTRACTION_COMPLETE] Meeting '{meeting.meeting_id[:8]}' processed in {total_ms}ms "
                f"({provider_used}). Actions: {len(meeting.action_items)}"
            )
            return meeting, metrics

        except Exception as exc:
            db.rollback()
            # Fetch fresh reference to update state to FAILED
            failed_meeting = db.query(Meeting).filter(Meeting.meeting_id == meeting.meeting_id).first()
            if failed_meeting:
                failed_meeting.processing_status = ProcessingStatus.FAILED
                failed_meeting.error_message = str(exc)
                AuditService.log_event(
                    db=db,
                    meeting_id=failed_meeting.meeting_id,
                    event_type=AuditEventType.PROCESSING_FAILED,
                    actor=AuditActor.SYSTEM,
                    payload={"error": str(exc)},
                )
                db.commit()

            logger.error(f"[EXTRACTION_FAILED] Processing failed for '{filename}': {exc}")
            raise exc
