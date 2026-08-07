"""
components/sidebar.py
─────────────────────
Streamlit Sidebar Component.

Renders:
- Navigation controls
- System Status Panel (Backend, Database, Gemini, GitHub)
- Demo Benchmark Scenario selector
- Developer Mode toggle switch
"""

import streamlit as st
from utils.api_client import APIClient
from utils.ui_state import UIState


def render_sidebar() -> str:
    """
    Render the Streamlit sidebar.

    Returns:
        Selected page name ("🏠 Dashboard", "📂 Upload Transcript")
    """
    with st.sidebar:
        st.title("🤖 AI Meeting Assistant")
        st.caption("TechBharat Buildathon — Use Case B")
        st.divider()

        # ── Navigation ────────────────────────────────────────────
        page = st.radio(
            "Navigate",
            options=["🏠 Dashboard", "📂 Upload Transcript"],
            label_visibility="collapsed",
        )

        st.divider()

        # ── System Status Panel ───────────────────────────────────
        st.subheader("System Status")
        health = APIClient.get_health()

        status = health.get("status", "unreachable")
        if status == "healthy":
            st.success("✅ Backend: Online")
        elif status == "degraded":
            st.warning("⚠️ Backend: Degraded")
        else:
            st.error("❌ Backend: Offline")

        if health.get("database") == "connected":
            st.success("✅ Database: Connected")
        else:
            st.error("❌ Database: Disconnected")

        if health.get("gemini_configured"):
            st.success("✅ Gemini 1.5: Configured")
        else:
            st.warning("⚠️ Gemini: Key missing")

        if health.get("github_configured"):
            if health.get("github_enabled"):
                st.success("✅ GitHub API: Connected")
            else:
                st.info("ℹ️ GitHub: Mock Mode")
        else:
            st.warning("⚠️ GitHub: Token missing")

        st.divider()

        # ── Developer Mode Toggle ─────────────────────────────────
        dev_mode = st.toggle("🛠️ Developer Mode", value=UIState.is_developer_mode())
        UIState.set_developer_mode(dev_mode)
        if dev_mode:
            st.caption("🔍 Raw telemetry, SHA-256 hashes, & latency timings enabled.")

    return page
