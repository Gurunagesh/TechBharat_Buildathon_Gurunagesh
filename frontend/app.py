"""
frontend/app.py
───────────────
Main Streamlit Application Entrypoint.

Routing Priority (highest to lowest):
  1. selected_meeting_id is set → always show Single Meeting Workspace
  2. sidebar radio == Upload Transcript → show Upload Page
  3. default → show Meeting Dashboard (list)
"""

import streamlit as st
from utils.api_client import APIClient
from utils.ui_state import UIState
from components.sidebar import render_sidebar
from components.summary_card import render_summary_card
from components.action_table import render_action_items_tab
from components.sync_panel import render_github_sync_tab
from components.audit_table import render_audit_trail_tab
from components.status_badges import render_processing_status_badge
from components.dev_mode import render_developer_mode_panel
from views.upload_page import render_upload_page

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize Session State ──────────────────────────────────────
UIState.init()

# ── Render Sidebar (returns radio selection) ──────────────────────
selected_page = render_sidebar()

# ── Routing ───────────────────────────────────────────────────────
# Read selected_id FIRST — upload sets this, and it takes precedence
# over whatever the sidebar radio currently shows.
selected_id = UIState.get_selected_meeting_id()

# ── ROUTE 1: Single Meeting Workspace ────────────────────────────
if selected_id:
    meeting_data = APIClient.get_meeting_detail(selected_id)

    if not meeting_data:
        st.error("⚠️ Meeting not found or was deleted.")
        if st.button("← Back to Dashboard"):
            UIState.set_selected_meeting_id(None)
            st.rerun()

    else:
        # Header Bar
        col_back, col_title, col_status = st.columns([1, 4, 2])
        with col_back:
            if st.button("← Dashboard", key="btn_back_dashboard"):
                UIState.set_selected_meeting_id(None)
                st.rerun()
        with col_title:
            st.title(f"📄 {meeting_data.get('title', 'Meeting')}")
            st.caption(
                f"Meeting Date: `{meeting_data.get('meeting_date')}` | "
                f"Uploaded: `{meeting_data.get('uploaded_at')}`"
            )
        with col_status:
            render_processing_status_badge(meeting_data.get("processing_status", "UNKNOWN"))

        st.divider()

        # Workspace Tabs
        tab_summary, tab_actions, tab_github, tab_audit = st.tabs([
            "📝 Executive Summary",
            "✅ Human Review Action Items",
            "🐙 GitHub Sync",
            "📜 Audit Trail",
        ])

        with tab_summary:
            render_summary_card(meeting_data)

        with tab_actions:
            render_action_items_tab(selected_id)

        with tab_github:
            render_github_sync_tab(selected_id)

        with tab_audit:
            render_audit_trail_tab(selected_id)

        # Developer Mode Observability Panel
        render_developer_mode_panel(meeting_data)

# ── ROUTE 2: Upload Transcript Page ──────────────────────────────
elif selected_page == "📂 Upload Transcript":
    render_upload_page()

# ── ROUTE 3: Dashboard (Meeting List) ────────────────────────────
else:
    st.title("🏠 Meeting Dashboard")
    st.caption("Select a meeting from the list below or upload a new transcript.")

    meetings = APIClient.list_meetings()

    if meetings:
        st.markdown("### 📋 Ingested Meetings")
        for m in meetings:
            with st.container(border=True):
                c_title, c_status, c_actions, c_btn = st.columns([3, 2, 1.5, 1])
                with c_title:
                    st.markdown(f"#### 📄 {m.get('title', 'Untitled')}")
                    st.caption(f"Uploaded: `{m.get('uploaded_at')}`")
                with c_status:
                    render_processing_status_badge(m.get("processing_status", "UNKNOWN"))
                with c_actions:
                    st.markdown(f"📌 **{m.get('action_items_count', 0)}** action items")
                with c_btn:
                    if st.button("Open", key=f"open_m_{m['meeting_id']}", type="primary"):
                        UIState.set_selected_meeting_id(m["meeting_id"])
                        st.rerun()
    else:
        st.info("No meetings found. Upload a transcript to get started.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📂 Upload Transcript Now", type="primary", use_container_width=True):
                # Signal the sidebar to show the upload page on next rerun
                st.session_state["_force_upload_page"] = True
                st.rerun()
