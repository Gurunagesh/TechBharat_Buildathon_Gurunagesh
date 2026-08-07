"""
services/business/duplicate_checker.py
───────────────────────────────────────
Idempotency & Duplicate Suppression Service.

Calculates SHA-256 hash digest of ingested transcripts and checks MySQL
for existing transcript_hash records.

Rules:
- Re-running the exact same meeting transcript MUST NOT create duplicate tasks.
- If a hash match is found, the existing Meeting ID is returned.
- Pure deterministic SHA-256 hashing.
"""

import hashlib
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.models import Meeting
from app.models.enums import ProcessingStatus
from app.core.exceptions import DuplicateTranscriptError
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


class DuplicateChecker:
    """Service for SHA-256 transcript deduplication and idempotency enforcement."""

    @staticmethod
    def compute_sha256(content: str) -> str:
        """
        Compute SHA-256 hex digest of a normalized text string.

        Args:
            content: Normalized transcript text.

        Returns:
            64-character lowercase hexadecimal digest string.
        """
        cleaned = content.strip().encode("utf-8")
        return hashlib.sha256(cleaned).hexdigest()

    @classmethod
    def check_duplicate(
        cls, db: Session, transcript_text: str
    ) -> Tuple[str, Optional[Meeting]]:
        """
        Check if a transcript has already been processed in MySQL.

        Args:
            db: SQLAlchemy session.
            transcript_text: Raw or normalized transcript text.

        Returns:
            Tuple of (transcript_hash, existing_meeting_or_none)

        If existing meeting is found, logs DUPLICATE_DETECTED event.
        """
        transcript_hash = cls.compute_sha256(transcript_text)

        existing_meeting = (
            db.query(Meeting)
            .filter(Meeting.transcript_hash == transcript_hash)
            .first()
        )

        if existing_meeting:
            # If the previously matched meeting FAILED, do not treat it as a
            # valid duplicate — allow the pipeline to reprocess and overwrite it.
            if existing_meeting.processing_status == ProcessingStatus.FAILED:
                logger.info(
                    f"[{LogEvent.DUPLICATE_DETECTED}] Hash matched a FAILED meeting "
                    f"({existing_meeting.meeting_id[:8]}...). Allowing reprocess."
                )
                # Delete the failed record so a fresh one can be created
                db.delete(existing_meeting)
                db.flush()
                return transcript_hash, None

            logger.info(
                f"[{LogEvent.DUPLICATE_DETECTED}] Idempotency hit: "
                f"hash={transcript_hash[:12]}... matched existing meeting_id={existing_meeting.meeting_id}"
            )
            return transcript_hash, existing_meeting

        return transcript_hash, None

    @classmethod
    def check_and_raise_if_duplicate(cls, db: Session, transcript_text: str) -> str:
        """
        Check for duplicate and raise DuplicateTranscriptError if found.

        Returns:
            transcript_hash if clean (no duplicate).

        Raises:
            DuplicateTranscriptError if transcript hash already exists in DB.
        """
        transcript_hash, existing = cls.check_duplicate(db, transcript_text)
        if existing:
            raise DuplicateTranscriptError(
                transcript_hash=transcript_hash,
                existing_meeting_id=existing.meeting_id,
            )
        return transcript_hash
