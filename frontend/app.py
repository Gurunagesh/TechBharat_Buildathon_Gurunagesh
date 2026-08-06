"""
frontend/app.py
───────────────
Streamlit application entrypoint.

Navigation:
    Sidebar → Dashboard (list of meetings)
    Sidebar → Meeting View → Tabs:
        📋 Summary      (decisions, risks, open questions)
        ✅ Action Items  (edit / approve / reject / evidence drawer)
        🐙 GitHub       (sync button + issue URLs)
        📜 Audit Trail  (timeline table)

Pages are built Sprint by Sprint.
This file is the skeleton that verifies Streamlit starts correctly.
"""

import streamlit as st
import os
import requests

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Backend URL ───────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def check_backend_health() -> dict:
    """Ping the FastAPI health endpoint."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        return response.json()
    except Exception:
        return {"status": "unreachable"}


# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 AI Meeting Assistant")
    st.caption("TechBharat Buildathon — Use Case B")
    st.divider()

    # Navigation
    page = st.radio(
        "Navigate",
        options=["🏠 Dashboard", "📂 Upload Meeting"],
        label_visibility="collapsed",
    )

    st.divider()

    # System status
    st.subheader("System Status")
    health = check_backend_health()
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
        st.success("✅ Gemini: Configured")
    else:
        st.warning("⚠️ Gemini: Not configured")

    if health.get("github_configured"):
        st.success("✅ GitHub: Configured")
    else:
        st.warning("⚠️ GitHub: Not configured")


# ── Main Content ──────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.title("🏠 Meeting Dashboard")
    st.info(
        "**Sprint 0 Checkpoint** — Streamlit is running successfully. "
        "Meeting list will be populated in Sprint 5."
    )
    st.markdown("### Recent Meetings")
    st.caption("No meetings yet. Upload a transcript to get started.")

elif page == "📂 Upload Meeting":
    st.title("📂 Upload Meeting Transcript")
    st.info(
        "**Sprint 0 Checkpoint** — Upload functionality will be implemented in Sprint 5. "
        "The backend upload endpoint will be wired here."
    )
    st.markdown("#### Supported formats: `.txt`, `.vtt`, `.srt`")
    uploaded_file = st.file_uploader(
        "Choose a transcript file",
        type=["txt", "vtt", "srt"],
        help="Upload a meeting transcript in .txt, .vtt, or .srt format",
    )
    if uploaded_file:
        st.success(f"File selected: `{uploaded_file.name}` ({uploaded_file.size} bytes)")
        st.caption("Upload processing will be connected in Sprint 5.")
