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

from app.services.llm.schemas import ExtractedMeetingInfo, ExtractedActionItem, ExtractedParticipant
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
        if settings.mock_llm:
            logger.info(f"[{LogEvent.EXTRACT}] MOCK MODE: Generating mock extraction for transcript...")
            return cls._get_mock_extraction(transcript_text)

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

    @classmethod
    def _get_mock_extraction(cls, text: str) -> ExtractedMeetingInfo:
        """Return high-fidelity pre-compiled structured extraction matching the transcript content."""
        normalized = text.lower()

        # ── 1. simple_meeting.txt Match ─────────────────────────────────────
        if "priya" in normalized or "rahul" in normalized or "sprint planning" in normalized:
            return ExtractedMeetingInfo(
                title="Sprint Planning & Roadmap Sync",
                meeting_date_mentioned="2026-08-07",
                summary="The team reviewed slow backend queries and planned the mobile app release candidate. Key optimization efforts focus on user dashboard queries and automated QA coverage. Additionally, credentials renewal and staging space cleanups are scheduled to maintain environment health.",
                decisions=[
                    "Targeting next Thursday for the release candidate build.",
                    "Rahul to renew the payment gateway sandbox credentials today.",
                    "Vikram to isolate the third-party analytics SDK update before event tracking test."
                ],
                risks=[
                    "Third-party analytics SDK update could break client event tracking.",
                    "Low staging environment disk space might block continuous deployment pipelines."
                ],
                open_questions=[
                    "Should the team perform a feature freeze during the migration week?",
                    "Schedule details for the QA smoke tests with the release candidate."
                ],
                participants=[
                    ExtractedParticipant(name="Priya", role="Product Manager", email="priya@company.com"),
                    ExtractedParticipant(name="Rahul", role="Lead Backend Engineer", email="rahul@company.com"),
                    ExtractedParticipant(name="Ananya", role="QA Engineer", email="ananya@company.com"),
                    ExtractedParticipant(name="Vikram", role="Lead Frontend Engineer", email="vikram@company.com")
                ],
                action_items=[
                    ExtractedActionItem(
                        title="Optimize three slow queries in the user dashboard module",
                        owner="Rahul",
                        due_date="next Friday",
                        priority="HIGH",
                        confidence_score=0.95,
                        evidence_quote="I've identified three slow queries in the user dashboard module. I'll have the fix ready by next Friday."
                    ),
                    ExtractedActionItem(
                        title="Write integration tests for optimized queries",
                        owner="Ananya",
                        due_date="Wednesday",
                        priority="MEDIUM",
                        confidence_score=0.92,
                        evidence_quote="I'll write the integration tests for those optimized queries by Wednesday."
                    ),
                    ExtractedActionItem(
                        title="Fix two UI bugs in the Android app",
                        owner="Vikram",
                        due_date="tomorrow",
                        priority="HIGH",
                        confidence_score=0.94,
                        evidence_quote="Android has two UI bugs left. I'll fix those by tomorrow."
                    ),
                    ExtractedActionItem(
                        title="Submit payment gateway sandbox credentials renewal request",
                        owner="Rahul",
                        due_date="today",
                        priority="HIGH",
                        confidence_score=0.88,
                        evidence_quote="Rahul, can you handle the credential renewal? ... Sure, I'll submit the renewal request today."
                    ),
                    ExtractedActionItem(
                        title="Prepare demo dataset and walkthrough script for client presentation",
                        owner="Ananya",
                        due_date="next Tuesday",
                        priority="MEDIUM",
                        confidence_score=0.89,
                        evidence_quote="I'll prepare the demo dataset and walkthrough script by next Tuesday."
                    ),
                    ExtractedActionItem(
                        title="Test the third-party analytics SDK update in isolation",
                        owner="Vikram",
                        due_date="Friday",
                        priority="MEDIUM",
                        confidence_score=0.80,
                        evidence_quote="Vikram, please test the SDK update by end of this week."
                    ),
                    ExtractedActionItem(
                        title="Clean up old deployments to free up space on staging environment",
                        owner="Rahul",
                        due_date="today",
                        priority="LOW",
                        confidence_score=0.78,
                        evidence_quote="Rahul, handle the disk cleanup today if possible. ... Will do."
                    )
                ]
            )

        # ── 2. vtt_meeting.vtt Match ────────────────────────────────────────
        elif "deepika" in normalized or "arjun" in normalized or "roadmap review" in normalized:
            return ExtractedMeetingInfo(
                title="Q3 Roadmap & Infrastructure Sync",
                meeting_date_mentioned="2026-08-07",
                summary="The team evaluated Q3 priorities, focusing on adding real-time collaboration spec, user onboarding redesign, and migrating infrastructure to Kubernetes. Downtime considerations were discussed, with weekend maintenance windows as the planned path.",
                decisions=[
                    "Migrate infrastructure to Kubernetes cluster next quarter.",
                    "Escalate Kubernetes budget request to VP by Friday.",
                    "Perform Kubernetes migration during a scheduled weekend maintenance window."
                ],
                risks=[
                    "Infrastructure migration could cause 2-4 hours of service downtime during cutover.",
                    "Usability confusion reported on step 3 of the new onboarding flow."
                ],
                open_questions=[
                    "Should the team implement a feature freeze during the migration week?"
                ],
                participants=[
                    ExtractedParticipant(name="Deepika", role="Director of Product", email="deepika@company.com"),
                    ExtractedParticipant(name="Arjun", role="Product Analyst", email="arjun@company.com"),
                    ExtractedParticipant(name="Meera", role="UX Lead", email="meera@company.com"),
                    ExtractedParticipant(name="Sanjay", role="DevOps Lead", email="sanjay@company.com")
                ],
                action_items=[
                    ExtractedActionItem(
                        title="Draft feature spec for real-time collaboration editing features",
                        owner="Arjun",
                        due_date="August 31st",
                        priority="HIGH",
                        confidence_score=0.92,
                        evidence_quote="Arjun, can you draft a feature spec for real-time editing by end of month? ... I'll have it ready by August 31st."
                    ),
                    ExtractedActionItem(
                        title="Redesign step 3 of the onboarding flow and run usability tests",
                        owner="Meera",
                        due_date="next Wednesday",
                        priority="HIGH",
                        confidence_score=0.88,
                        evidence_quote="Meera, please redesign step 3 and run another usability test by next Wednesday."
                    ),
                    ExtractedActionItem(
                        title="Send detailed cost breakdown for the Kubernetes cluster",
                        owner="Sanjay",
                        due_date="today",
                        priority="MEDIUM",
                        confidence_score=0.91,
                        evidence_quote="Sanjay, send me the cost breakdown today."
                    ),
                    ExtractedActionItem(
                        title="Propose three weekend maintenance window options for Kubernetes migration",
                        owner="Sanjay",
                        due_date="next Thursday",
                        priority="MEDIUM",
                        confidence_score=0.85,
                        evidence_quote="Sanjay, propose three weekend options."
                    )
                ]
            )

        # ── 3. srt_meeting.srt Match ────────────────────────────────────────
        elif "kavitha" in normalized or "naveen" in normalized or "triage" in normalized:
            return ExtractedMeetingInfo(
                title="Bug Triage & Rate Limiter Sync",
                meeting_date_mentioned="2026-08-07",
                summary="The engineering team synced on critical open issues, prioritizing a payment timeout bug and enterprise row truncation limits. They also agreed to adjust the login rate limiter and configure appropriate monitoring alerts.",
                decisions=[
                    "Increase login rate limiter threshold config from 5 to 10 attempts per minute.",
                    "Create Datadog monitoring alerts for rate-limiting events."
                ],
                risks=[
                    "Billing payment module timeout is currently blocking the upcoming release candidate.",
                    "Row truncation beyond 10,000 items affects the enterprise client export."
                ],
                open_questions=[
                    "Verify if row truncation is a memory footprint issue with the database exporter."
                ],
                participants=[
                    ExtractedParticipant(name="Kavitha", role="Engineering Manager", email="kavitha@company.com"),
                    ExtractedParticipant(name="Naveen", role="Lead Developer", email="naveen@company.com"),
                    ExtractedParticipant(name="Ritu", role="QA Tester", email="ritu@company.com")
                ],
                action_items=[
                    ExtractedActionItem(
                        title="Fix the billing payment module timeout bug and push PR",
                        owner="Naveen",
                        due_date="tomorrow",
                        priority="HIGH",
                        confidence_score=0.96,
                        evidence_quote="Naveen, can you fix the payment timeout bug by tomorrow? ... Yes. I'll push the PR today and it should be merged by tomorrow morning."
                    ),
                    ExtractedActionItem(
                        title="Perform root cause analysis on enterprise data export row truncation issue",
                        owner="Ritu",
                        due_date="Wednesday",
                        priority="HIGH",
                        confidence_score=0.90,
                        evidence_quote="I'll have a root cause analysis by Wednesday."
                    ),
                    ExtractedActionItem(
                        title="Update login rate limiter configuration threshold to 10 attempts",
                        owner="Naveen",
                        due_date="today",
                        priority="HIGH",
                        confidence_score=0.93,
                        evidence_quote="Naveen, update the config by end of day."
                    ),
                    ExtractedActionItem(
                        title="Set up Datadog monitoring alerts for rate limit events",
                        owner="Ritu",
                        due_date="Friday",
                        priority="MEDIUM",
                        confidence_score=0.85,
                        evidence_quote="Ritu, set up Datadog alerts for rate limit triggers by Friday."
                    )
                ]
            )

        # ── 4. ambiguous_meeting.txt Match ──────────────────────────────────
        elif "crashed" in normalized or "landing page" in normalized or "financial report" in normalized:
            return ExtractedMeetingInfo(
                title="Ad-hoc Bug & Sync Sync",
                meeting_date_mentioned="2026-08-07",
                summary="The team had a short sync to triage recurring billing system crashes. Discussion also touched upon sending the Q2 financial report, landing page design updates, and scheduling a security review.",
                decisions=[
                    "Schedule a comprehensive security review before the upcoming audit."
                ],
                risks=[
                    "Billing system crashes are recurring and critically impact users."
                ],
                open_questions=[
                    "Who will take ownership of the landing page design updates?"
                ],
                participants=[
                    ExtractedParticipant(name="Host", role="Facilitator", email="host@company.com"),
                    ExtractedParticipant(name="Participant", role="Team Member", email="participant@company.com")
                ],
                action_items=[
                    ExtractedActionItem(
                        title="Investigate billing system crash",
                        owner="UNASSIGNED",
                        due_date="as soon as possible",
                        priority="HIGH",
                        confidence_score=0.65,
                        evidence_quote="Someone needs to investigate this as soon as possible."
                    ),
                    ExtractedActionItem(
                        title="Send Q2 financial report",
                        owner="UNASSIGNED",
                        due_date="next month",
                        priority="MEDIUM",
                        confidence_score=0.55,
                        evidence_quote="We also need to send the Q2 financial report eventually, maybe sometime next month."
                    ),
                    ExtractedActionItem(
                        title="Update landing page design",
                        owner="UNASSIGNED",
                        due_date="later",
                        priority="LOW",
                        confidence_score=0.45,
                        evidence_quote="I think we should also think about updating the landing page design."
                    )
                ]
            )

        # ── 5. Generic Default Fallback ──────────────────────────────────────
        else:
            return ExtractedMeetingInfo(
                title="Project Alignment Sync",
                meeting_date_mentioned=str(date.today()),
                summary="The meeting centered on regular sprint progress and alignment. Tasks were discussed, emphasizing system validation and team assignments.",
                decisions=[
                    "Proceed with the current sprint plan goals."
                ],
                risks=[
                    "Dependency on external API keys could introduce timeline risk."
                ],
                open_questions=[
                    "Confirm dates for the next sync meeting."
                ],
                participants=[
                    ExtractedParticipant(name="User", role="Facilitator", email="user@company.com")
                ],
                action_items=[
                    ExtractedActionItem(
                        title="Confirm system test execution is complete",
                        owner="User",
                        due_date="tomorrow",
                        priority="MEDIUM",
                        confidence_score=0.85,
                        evidence_quote="Let's make sure all system tests are completed by tomorrow."
                    )
                ]
            )
