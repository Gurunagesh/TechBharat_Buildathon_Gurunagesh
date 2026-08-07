"""
services/business/resolver.py
──────────────────────────────
Deterministic Date and Owner Resolution Service.

Performs deterministic post-processing on AI-extracted raw values:
1. Date Resolution: Uses `dateparser` anchored to `meeting_date` to turn relative expressions
   ("by next Friday", "end of quarter", "tomorrow") into valid ISO dates (YYYY-MM-DD).
2. Owner Resolution: Matches extracted names ("Priya", "John") against a known list of participants/emails.
   If no match is found, defaults loudly to "UNASSIGNED".
3. Field Sanitation: Enforces priority enums and confidence bounds (0.0 to 1.0).

ZERO LLM DEPENDENCIES. 100% Deterministic Python logic.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
import dateparser

from app.models.enums import Priority
from app.core.logging import get_logger

logger = get_logger(__name__)


class BusinessResolver:
    """Deterministic resolver for dates, owners, priorities, and confidence scores."""

    @staticmethod
    def resolve_date(
        raw_date_str: Optional[str], anchor_date: Optional[date] = None
    ) -> Optional[date]:
        """
        Parse a raw date string (relative or absolute) into a deterministic date object.

        Args:
            raw_date_str: String such as "by next Friday", "2026-08-15", "tomorrow", or None
            anchor_date: The meeting date to anchor relative expressions against.

        Returns:
            Resolved datetime.date object, or None if unparseable / missing.
        """
        if not raw_date_str or not raw_date_str.strip():
            return None

        clean_str = raw_date_str.strip()

        # Check if already ISO format (YYYY-MM-DD)
        try:
            return date.fromisoformat(clean_str)
        except ValueError:
            pass

        # Anchor date setting for dateparser
        base_date = datetime.combine(anchor_date or date.today(), datetime.min.time())
        settings = {
            "RELATIVE_BASE": base_date,
            "PREFER_DATES_FROM": "future",
            "RETURN_AS_TIMEZONE_AWARE": False,
        }

        # Remove common prefixes ("by ", "due ", "before ")
        for prefix in ["by ", "due ", "before ", "on "]:
            if clean_str.lower().startswith(prefix):
                clean_str = clean_str[len(prefix):].strip()

        parsed_dt = dateparser.parse(clean_str, settings=settings)
        if parsed_dt:
            resolved_date = parsed_dt.date()
            logger.info(f"[RESOLVE] Date '{raw_date_str}' -> {resolved_date} (anchor: {anchor_date})")
            return resolved_date

        logger.warning(f"[RESOLVE_FAILED] Could not parse relative date: '{raw_date_str}'")
        return None

    @staticmethod
    def resolve_owner(
        raw_owner: Optional[str], known_participants: Optional[List[Dict[str, str]]] = None
    ) -> Tuple_Owner_Email:
        """
        Match raw owner string against known team participants.

        Args:
            raw_owner: Extracted owner string (e.g. "Priya", "John Doe", "unassigned")
            known_participants: List of dicts [{'name': 'Priya Sharma', 'email': 'priya@co.com'}]

        Returns:
            Tuple of (owner_name: str, owner_email: Optional[str])
            If unmatched, returns ("UNASSIGNED", None).
        """
        if not raw_owner or not raw_owner.strip():
            return "UNASSIGNED", None

        clean_name = raw_owner.strip()
        lower_name = clean_name.lower()

        if lower_name in ["unassigned", "unknown", "nobody", "none", "tbd", "n/a"]:
            return "UNASSIGNED", None

        if not known_participants:
            return clean_name, None

        # Search for exact or first-name match in known participants
        for p in known_participants:
            p_name = p.get("name", "").strip()
            p_email = p.get("email")

            if not p_name:
                continue

            # Exact match or first-name match
            if lower_name == p_name.lower() or lower_name in p_name.lower().split():
                logger.info(f"[RESOLVE] Owner '{raw_owner}' mapped to '{p_name}' ({p_email})")
                return p_name, p_email

        # If no match found, keep provided name but log warning
        logger.info(f"[RESOLVE] Owner '{raw_owner}' not in known team list — preserving as '{clean_name}'")
        return clean_name, None

    @staticmethod
    def resolve_priority(raw_priority: Optional[str]) -> Priority:
        """Sanitize priority string to Priority enum (HIGH, MEDIUM, LOW). Default MEDIUM."""
        if not raw_priority:
            return Priority.MEDIUM

        clean = raw_priority.strip().upper()
        if clean in Priority.__members__:
            return Priority[clean]

        return Priority.MEDIUM

    @staticmethod
    def sanitize_confidence_score(raw_score: Any) -> float:
        """Ensure confidence score is float bounded between 0.000 and 1.000."""
        try:
            score = float(raw_score)
            return max(0.000, min(1.000, round(score, 3)))
        except (ValueError, TypeError):
            return 0.500


# Type helper alias
Tuple_Owner_Email = tuple[str, Optional[str]]
