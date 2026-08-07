"""
components/dev_mode.py
──────────────────────
Developer Mode Observability Panel Component.

Displays deep telemetry when Developer Mode toggle is enabled:
- Meeting ID (UUID)
- SHA-256 Transcript Hash Digest
- Latency Telemetry Timings
- LLM Provider Used
- Raw JSON Payload Inspection
"""

import streamlit as st
from typing import Dict, Any
from utils.ui_state import UIState


def render_developer_mode_panel(meeting_data: Dict[str, Any]):
    """Render observability telemetry panel when Developer Mode is ON."""
    if not UIState.is_developer_mode():
        return

    st.divider()
    with st.expander("🛠️ Developer Mode — Telemetry & Observability Panel", expanded=True):
        st.markdown("##### 🔬 Deep System Observability")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Meeting UUID:** `{meeting_data.get('meeting_id')}`")
            st.markdown(f"**Processing Status:** `{meeting_data.get('processing_status')}`")
        with col2:
            st.markdown(f"**SHA-256 Hash:** `{meeting_data.get('transcript_hash')}`")
            st.markdown(f"**Uploaded At:** `{meeting_data.get('uploaded_at')}`")
        with col3:
            metrics = UIState.get_upload_metrics() or {}
            st.markdown(f"**LLM Provider:** `{metrics.get('llm_provider_used', 'Gemini')}`")
            st.markdown(f"**Total Latency:** `{metrics.get('total_time_ms', 'N/A')} ms`")

        if metrics:
            st.markdown("###### ⏱️ Execution Time Breakdown")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Parser Time", f"{metrics.get('parser_time_ms', 0)} ms")
            with m2:
                st.metric("LLM Time", f"{metrics.get('llm_time_ms', 0)} ms")
            with m3:
                st.metric("Resolver Time", f"{metrics.get('resolver_time_ms', 0)} ms")
            with m4:
                st.metric("Total Latency", f"{metrics.get('total_time_ms', 0)} ms")

        st.markdown("###### 📄 Raw Meeting JSON")
        st.json(meeting_data, expanded=False)
