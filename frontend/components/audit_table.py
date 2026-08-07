"""
components/audit_table.py
──────────────────────────
Audit Trail Component.

Renders immutable chronological timeline table of system events.
"""

import streamlit as st
import json
from typing import Dict, Any
from utils.api_client import APIClient


def render_audit_trail_tab(meeting_id: str):
    """Render chronological audit trail timeline table."""
    st.subheader("📜 System Audit Log")
    st.caption("Immutable event history. Every AI extraction, human edit, approval, and GitHub sync is logged.")

    logs = APIClient.get_audit_trail(meeting_id)

    if not logs:
        st.info("No audit logs recorded for this meeting yet.")
        return

    # Timeline view
    for log in logs:
        event_type = log.get("event_type", "EVENT")
        actor = log.get("actor", "SYSTEM")
        created_at = log.get("created_at", "")
        payload = log.get("payload") or {}

        # Icon mapping
        icon_map = {
            "UPLOAD": "📂",
            "PARSE": "⚙️",
            "DUPLICATE_DETECTED": "🔍",
            "EXTRACT": "🤖",
            "VALIDATE": "✅",
            "RESOLVE": "📅",
            "EDIT": "✏️",
            "APPROVE": "👍",
            "REJECT": "👎",
            "SYNC": "🚀",
            "GITHUB_SUCCESS": "🐙",
            "GITHUB_FAILURE": "❌",
            "LLM_RETRY": "🔄",
            "LLM_FALLBACK": "🔀",
            "PROCESSING_FAILED": "💥",
        }
        icon = icon_map.get(event_type, "📌")

        with st.container(border=True):
            col_event, col_actor, col_time = st.columns([2, 1, 1])
            with col_event:
                st.markdown(f"**{icon} {event_type}**")
            with col_actor:
                if actor == "HUMAN_USER":
                    st.markdown("👤 **Human User**")
                elif actor == "AI_AGENT":
                    st.markdown("🤖 **AI Agent**")
                else:
                    st.markdown("⚙️ **System**")
            with col_time:
                st.caption(f"`{created_at}`")

            if payload:
                st.json(payload, expanded=False)
