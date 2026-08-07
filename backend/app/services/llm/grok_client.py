"""
services/llm/grok_client.py
───────────────────────────
Secondary Fallback LLM Client — Grok / xAI (OpenAI-compatible format).

Triggered when Gemini API is rate-limited or unavailable (HTTP 429).
Uses `openai` client pointing to settings.grok_base_url.
"""

import json
from typing import Optional, List, Dict
from openai import OpenAI
from pydantic import ValidationError

from app.services.llm.schemas import ExtractedMeetingInfo
from app.services.llm.prompts import SYSTEM_PROMPT, build_extraction_prompt
from app.core.config import settings
from app.core.exceptions import LLMExtractionError
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


class GrokClient:
    """Fallback LLM caller for Grok / xAI API using OpenAI client interface."""

    @classmethod
    def extract_meeting_info(
        cls,
        transcript_text: str,
        anchor_date: Optional[str] = None,
        known_participants: Optional[List[Dict[str, str]]] = None,
    ) -> ExtractedMeetingInfo:
        """
        Invoke Grok API to extract structured ExtractedMeetingInfo.

        Returns:
            Validated ExtractedMeetingInfo Pydantic model instance.

        Raises:
            LLMExtractionError: If Grok API fails or key is missing.
        """
        if not settings.grok_api_key:
            raise LLMExtractionError(
                message="GROK_API_KEY is not configured in environment.",
                provider="Grok",
            )

        try:
            logger.info(f"[{LogEvent.LLM_FALLBACK}] Invoking Grok fallback model ({settings.grok_model})...")

            client = OpenAI(
                api_key=settings.grok_api_key,
                base_url=settings.grok_base_url,
            )

            prompt = build_extraction_prompt(
                transcript_text=transcript_text,
                anchor_date=anchor_date,
                known_participants=known_participants,
            )

            response = client.chat.completions.create(
                model=settings.grok_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + "\nRespond strictly in valid JSON matching the requested schema."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise LLMExtractionError("Grok returned empty message content.", provider="Grok")

            raw_json = json.loads(content)
            extracted_info = ExtractedMeetingInfo.model_validate(raw_json)

            logger.info(
                f"[{LogEvent.LLM_FALLBACK}] Grok extraction SUCCESS: "
                f"actions={len(extracted_info.action_items)}, decisions={len(extracted_info.decisions)}"
            )
            return extracted_info

        except ValidationError as val_err:
            raise LLMExtractionError(f"Grok response failed Pydantic validation: {val_err}", provider="Grok")
        except Exception as exc:
            logger.error(f"[{LogEvent.LLM_FALLBACK}] Grok API call failed: {exc}")
            raise LLMExtractionError(f"Grok API call failed: {exc}", provider="Grok")
