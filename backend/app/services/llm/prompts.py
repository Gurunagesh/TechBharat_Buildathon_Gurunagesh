"""
services/llm/prompts.py
────────────────────────
Prompt Templates for LLM Extraction.

Contains System Prompts and Extraction Instructions for Gemini 1.5-flash and Grok.

Key Prompt Guardrails:
1. Anchor Date Context: Injects meeting date into prompt so relative dates ("by next Friday") resolve accurately.
2. Participant Context: Injects known team members to help resolve owner names ("Priya" -> "Priya").
3. Evidence Quote Requirement: Every action item MUST extract an exact transcript quote snippet.
4. Precision & Recall: High recall for explicit commitments, zero invented tasks.
"""

from typing import Optional, List, Dict


SYSTEM_PROMPT = """You are an expert AI Meeting Assistant built for enterprise engineering teams.
Your job is to read meeting transcripts and extract accurate, structured meeting intelligence.

RULES:
1. EXTRACT ONLY REAL COMMITMENTS: An action item is a clear commitment where someone agreed to perform a task. Do NOT invent tasks or convert casual observations into tasks.
2. EVIDENCE QUOTES: For EVERY action item, copy the EXACT raw transcript text snippet where the commitment was made.
3. RELATIVE DATES: Convert relative date mentions ("by next Friday", "end of month", "tomorrow") into clear date strings relative to the Anchor Meeting Date provided in context.
4. OWNER ASSIGNMENT: Identify who committed to the task. If a specific person volunteered or was assigned, use their name. If no single person was assigned, use "UNASSIGNED".
5. CONFIDENCE SCORE: Assign a confidence score from 0.0 to 1.0 for each action item estimating your certainty that it represents a real commitment.
6. NO HALLUCINATIONS: Faithfulness is paramount. Do not extrapolate facts not present in the transcript.
"""


def build_extraction_prompt(
    transcript_text: str,
    anchor_date: Optional[str] = None,
    known_participants: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Construct user prompt containing transcript and contextual metadata.

    Args:
        transcript_text: Cleaned transcript string.
        anchor_date: ISO meeting date string (e.g., "2026-08-05")
        known_participants: List of known participant dicts.

    Returns:
        Formatted text prompt for LLM.
    """
    context_sections = []

    if anchor_date:
        context_sections.append(f"ANCHOR MEETING DATE: {anchor_date}")

    if known_participants:
        p_strings = [
            f"- {p.get('name')} ({p.get('role', 'Member')})" for p in known_participants
        ]
        context_sections.append("KNOWN TEAM MEMBERS:\n" + "\n".join(p_strings))

    context_header = ""
    if context_sections:
        context_header = "### MEETING CONTEXT\n" + "\n".join(context_sections) + "\n\n"

    return f"""{context_header}### RAW MEETING TRANSCRIPT
{transcript_text}

### EXTRACTION TASK
Analyze the above meeting transcript carefully and extract:
1. A concise, professional title for the meeting.
2. An executive summary (2-4 paragraphs capturing core discussion).
3. All key decisions agreed upon during the meeting.
4. All risks, blockers, or concerns raised.
5. All unresolved open questions.
6. All identified participants.
7. All action items committed to during the meeting (with owner, relative/ISO due date, priority, confidence score, and exact transcript evidence quote).
"""
