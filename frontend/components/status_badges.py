"""
components/status_badges.py
────────────────────────────
UI Status Badge Component.

Renders styled badges for ProcessingStatus, ActionStatus, and Priority.
"""

import streamlit as st


def render_action_status_badge(status_str: str):
    """Render color-coded HTML badge for ActionStatus."""
    color_map = {
        "PENDING_REVIEW": ("#f59e0b", "#fef3c7", "⏳ Pending Review"),
        "APPROVED": ("#10b981", "#d1fae5", "✅ Approved"),
        "REJECTED": ("#ef4444", "#fee2e2", "❌ Rejected"),
        "SYNCED": ("#6366f1", "#e0e7ff", "🐙 Synced to GitHub"),
    }
    border, bg, label = color_map.get(status_str, ("#6b7280", "#f3f4f6", status_str))
    st.markdown(
        f'<span style="background-color:{bg}; color:{border}; border: 1px solid {border}; '
        f'padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 13px;">{label}</span>',
        unsafe_allow_html=True,
    )


def render_processing_status_badge(status_str: str):
    """Render color-coded badge for ProcessingStatus."""
    color_map = {
        "UPLOADING": ("#3b82f6", "Uploading..."),
        "PARSING": ("#3b82f6", "Parsing Transcript..."),
        "EXTRACTING": ("#8b5cf6", "AI Extracting..."),
        "VALIDATING": ("#8b5cf6", "Validating..."),
        "READY_FOR_REVIEW": ("#10b981", "Ready for Review"),
        "COMPLETED": ("#10b981", "Completed"),
        "FAILED": ("#ef4444", "Failed"),
    }
    color, label = color_map.get(status_str, ("#6b7280", status_str))
    if status_str in ["READY_FOR_REVIEW", "COMPLETED"]:
        st.success(f"Status: {label}")
    elif status_str == "FAILED":
        st.error(f"Status: {label}")
    else:
        st.info(f"Status: {label}")


def render_priority_badge(priority_str: str):
    """Render small priority tag."""
    color_map = {
        "HIGH": "🔴 High",
        "MEDIUM": "🟡 Medium",
        "LOW": "🟢 Low",
    }
    return color_map.get(priority_str.upper(), priority_str)
