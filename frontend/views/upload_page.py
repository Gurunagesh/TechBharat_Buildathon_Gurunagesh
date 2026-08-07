"""
views/upload_page.py
────────────────────
Upload & Ingest Meeting Transcript Page.

Moved here from pages/ to prevent Streamlit multi-page auto-discovery.
app.py imports render_upload_page() from this module directly.

Features:
- File uploader (.txt, .vtt, .srt)
- Optional Meeting Anchor Date selector
- Duplicate transcript detection alert
- Triggers ExtractionService via APIClient.upload_transcript()
"""

import streamlit as st
from datetime import date
from utils.api_client import APIClient
from utils.ui_state import UIState


def render_upload_page():
    """Render the file upload page."""
    st.title("📂 Ingest Meeting Transcript")
    st.caption("Supported transcript formats: **.txt**, **.vtt**, **.srt** (max 10MB)")

    with st.container(border=True):
        col_file, col_date = st.columns([2, 1])

        with col_file:
            uploaded_file = st.file_uploader(
                "Select Transcript File",
                type=["txt", "vtt", "srt"],
                help="Upload a meeting transcript file",
            )
        with col_date:
            anchor_date = st.date_input(
                "Meeting Anchor Date",
                value=date.today(),
                help="Used to resolve relative dates ('next Friday', 'tomorrow')",
            )

        if uploaded_file:
            st.info(f"📁 Selected: **{uploaded_file.name}** ({len(uploaded_file.getvalue())} bytes)")

            if st.button("🚀 Process & Extract Action Items", type="primary", use_container_width=True):
                with st.spinner("Parsing transcript and extracting meeting intelligence via AI..."):
                    filename = uploaded_file.name
                    content = uploaded_file.getvalue()
                    date_str = str(anchor_date) if anchor_date else None

                    success, data_or_err, message = APIClient.upload_transcript(
                        filename=filename,
                        content_bytes=content,
                        meeting_date=date_str,
                    )

                    if success:
                        meeting_id = data_or_err.get("meeting_id")
                        is_duplicate = data_or_err.get("is_duplicate", False)

                        UIState.set_selected_meeting_id(meeting_id)
                        UIState.set_upload_metrics(data_or_err)

                        if is_duplicate:
                            st.warning(f"⚠️ **Duplicate Transcript Detected!** {message}")
                            st.caption("Existing processed record reloaded. No duplicate tasks created.")
                        else:
                            st.balloons()
                            st.success(f"✅ {message}")

                        st.rerun()
                    else:
                        error_code = data_or_err.get("error_code", "ERR_UNKNOWN")
                        if error_code == "ERR_DUPLICATE":
                            st.warning(f"⚠️ **Duplicate Transcript:** {message}")
                        else:
                            st.error(f"❌ **Upload Failed:** {message}")
