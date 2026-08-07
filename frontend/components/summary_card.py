"""
components/summary_card.py
───────────────────────────
Executive Summary & Record Component.

Renders:
- Executive Summary card
- Key Decisions list
- Risks & Blockers callout box
- Open Questions list
"""

import streamlit as st
from typing import Dict, Any, List


def render_summary_card(meeting_data: Dict[str, Any]):
    """Render the executive summary and structured record tab."""
    summary = meeting_data.get("summary") or "No executive summary available."
    decisions: List[str] = meeting_data.get("decisions", [])
    risks: List[str] = meeting_data.get("risks", [])
    open_questions: List[str] = meeting_data.get("open_questions", [])
    participants = meeting_data.get("participants", [])

    st.subheader("📝 Executive Summary")
    st.markdown(summary)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Key Decisions Made")
        if decisions:
            for idx, d in enumerate(decisions, 1):
                st.markdown(f"**{idx}.** {d}")
        else:
            st.info("No explicit decisions recorded in this meeting.")

        st.markdown("### ❓ Open Questions")
        if open_questions:
            for idx, q in enumerate(open_questions, 1):
                st.markdown(f"- {q}")
        else:
            st.caption("No open questions detected.")

    with col2:
        st.markdown("### ⚠️ Risks & Blockers")
        if risks:
            for r in risks:
                st.warning(f"**Risk:** {r}")
        else:
            st.success("No critical risks or blockers identified.")

        st.markdown("### 👥 Meeting Participants")
        if participants:
            for p in participants:
                role_str = f" ({p.get('role')})" if p.get("role") else ""
                email_str = f" — `{p.get('email')}`" if p.get("email") else ""
                st.markdown(f"- **{p.get('name')}**{role_str}{email_str}")
        else:
            st.caption("No specific participant list extracted.")
