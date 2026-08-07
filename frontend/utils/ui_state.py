"""
utils/ui_state.py
─────────────────
Streamlit Session State Manager.

Centralizes initialization and access to st.session_state properties.
Prevents magic string keys scattered across UI code.
"""

import streamlit as st
from typing import Optional, Dict, Any


class UIState:
    """Manager for Streamlit session state."""

    @staticmethod
    def init():
        """Initialize all required session state variables with defaults."""
        if "selected_meeting_id" not in st.session_state:
            st.session_state.selected_meeting_id = None
        if "developer_mode" not in st.session_state:
            st.session_state.developer_mode = False
        if "active_meeting_data" not in st.session_state:
            st.session_state.active_meeting_data = None
        if "last_upload_metrics" not in st.session_state:
            st.session_state.last_upload_metrics = None
        if "navigation_page" not in st.session_state:
            st.session_state.navigation_page = "🏠 Dashboard"

    @classmethod
    def get_selected_meeting_id(cls) -> Optional[str]:
        cls.init()
        return st.session_state.selected_meeting_id

    @classmethod
    def set_selected_meeting_id(cls, meeting_id: Optional[str]):
        cls.init()
        st.session_state.selected_meeting_id = meeting_id

    @classmethod
    def is_developer_mode(cls) -> bool:
        cls.init()
        return st.session_state.developer_mode

    @classmethod
    def set_developer_mode(cls, enabled: bool):
        cls.init()
        st.session_state.developer_mode = enabled

    @classmethod
    def set_upload_metrics(cls, metrics: Dict[str, Any]):
        cls.init()
        st.session_state.last_upload_metrics = metrics

    @classmethod
    def get_upload_metrics(cls) -> Optional[Dict[str, Any]]:
        cls.init()
        return st.session_state.last_upload_metrics
