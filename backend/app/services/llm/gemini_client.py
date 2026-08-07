"""
services/llm/gemini_client.py
─────────────────────────────
Primary LLM Client — Google Gemini (gemini-1.5-flash).

Uses `google-genai` SDK with Pydantic structured output validation (`response_schema`).

Features:
- Enforces strict Pydantic ExtractedMeetingInfo JSON schema output.
- Retries on HTTP 429 / Rate Limit or JSON validation error (max 2 attempts).
- Raises LLMExtractionError on failure to trigger Grok fallback.
"""

import time
import json
from typing import Optional, List, Dict
from google import genai
from google.genai import types
from pydantic import ValidationError

from app.services.llm.schemas import ExtractedMeetingInfo
from app.services.llm.prompts import SYSTEM_PROMPT, build_extraction_prompt
from app.core.config import settings
from app.core.exceptions import LLMExtractionError
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


class GeminiClient:
    """Primary LLM caller for Google Gemini 1.5-flash using google-genai SDK."""

    @classmethod
    def extract_meeting_info(
        cls,
        transcript_text: str,
        anchor_date: Optional[str] = None,
        known_participants: Optional[List[Dict[str, str]]] = None,
    ) -> ExtractedMeetingInfo:
        """
        Invoke Gemini 1.5-flash to extract structured ExtractedMeetingInfo.

        Args:
            transcript_text: Cleaned raw transcript text.
            anchor_date: ISO date string for relative date anchoring.
            known_participants: List of known participant dicts.

        Returns:
            Validated ExtractedMeetingInfo Pydantic model instance.

        Raises:
            LLMExtractionError: If Gemini API fails after retries.
        """
        if not settings.gemini_api_key:
            raise LLMExtractionError(
                message="GEMINI_API_KEY is not configured in environment.",
                provider="Gemini",
            )

        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = build_extraction_prompt(
            transcript_text=transcript_text,
            anchor_date=anchor_date,
            known_participants=known_participants,
        )

        max_attempts = settings.llm_max_retries
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(
                    f"[{LogEvent.EXTRACT}] Calling Gemini ({settings.gemini_model}) "
                    f"[Attempt {attempt}/{max_attempts}]..."
                )

                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,  # Low temperature for deterministic structured extraction
                    top_p=0.95,
                    response_mime_type="application/json",
                    response_schema=ExtractedMeetingInfo,
                )

                response = client.models.generate_content(
                    model=settings.gemini_model,
                    contents=prompt,
                    config=config,
                )

                if not response.text:
                    raise LLMExtractionError(
                        message="Gemini returned empty response text.",
                        provider="Gemini",
                    )

                # Parse JSON and validate with Pydantic
                raw_json = json.loads(response.text)
                extracted_info = ExtractedMeetingInfo.model_validate(raw_json)

                logger.info(
                    f"[{LogEvent.EXTRACT}] Gemini extraction SUCCESS: "
                    f"actions={len(extracted_info.action_items)}, "
                    f"decisions={len(extracted_info.decisions)}, "
                    f"participants={len(extracted_info.participants)}"
                )
                return extracted_info

            except ValidationError as val_err:
                last_error = f"Pydantic Validation Error: {val_err}"
                logger.warning(
                    f"[{LogEvent.LLM_RETRY}] Gemini response failed Pydantic validation: {val_err}"
                )

            except json.JSONDecodeError as json_err:
                last_error = f"JSON Decode Error: {json_err}"
                logger.warning(
                    f"[{LogEvent.LLM_RETRY}] Gemini returned invalid JSON string: {json_err}"
                )

            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    f"[{LogEvent.LLM_RETRY}] Gemini API call failed (attempt {attempt}): {exc}"
                )

            if attempt < max_attempts:
                time.sleep(settings.llm_retry_delay_seconds)

        raise LLMExtractionError(
            message=f"Gemini extraction failed after {max_attempts} attempts. Last error: {last_error}",
            provider="Gemini",
            raw_response=last_error,
        )
