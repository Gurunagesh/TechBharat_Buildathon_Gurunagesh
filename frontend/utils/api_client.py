"""
utils/api_client.py
───────────────────
Centralized HTTP API Client for FastAPI Backend (/api/v1).

Every Streamlit component and page calls the backend exclusively through this client.
Handles ResponseEnvelope unwrapping, error mapping, and user-friendly error formatting.
"""

import os
import requests
from typing import Dict, Any, List, Optional, Tuple

def _resolve_backend_url() -> str:
    """Resolve backend URL from env vars or Streamlit Cloud st.secrets."""
    env_url = os.getenv("BACKEND_URL")
    if env_url:
        return env_url.rstrip("/")

    try:
        import streamlit as st
        if hasattr(st, "secrets") and "BACKEND_URL" in st.secrets:
            return str(st.secrets["BACKEND_URL"]).rstrip("/")
    except Exception:
        pass

    return "http://localhost:8000"


BACKEND_URL = _resolve_backend_url()
API_V1_URL = f"{BACKEND_URL}/api/v1"


class APIClient:
    """HTTP Client wrapping FastAPI REST endpoints."""

    @staticmethod
    def get_health() -> Dict[str, Any]:
        """Ping /api/v1/health endpoint."""
        try:
            res = requests.get(f"{API_V1_URL}/health", timeout=12)
            if res.status_code == 200:
                payload = res.json()
                return payload.get("data", {"status": "degraded"})
            return {"status": "degraded"}
        except Exception:
            return {"status": "unreachable", "database": "unreachable"}

    @staticmethod
    def upload_transcript(
        filename: str, content_bytes: bytes, meeting_date: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        POST /api/v1/meetings/upload

        Returns:
            Tuple of (success: bool, data_or_error_dict, user_message: str)
        """
        try:
            files = {"file": (filename, content_bytes)}
            data = {}
            if meeting_date:
                data["meeting_date"] = meeting_date

            res = requests.post(f"{API_V1_URL}/meetings/upload", files=files, data=data, timeout=60)
            payload = res.json()

            if res.status_code in [200, 201] and payload.get("success"):
                return True, payload.get("data", {}), payload.get("message", "Success")

            error_info = payload.get("error", {})
            err_msg = payload.get("message") or error_info.get("message", "Upload failed")
            return False, error_info, err_msg

        except requests.exceptions.Timeout:
            return False, {"error_code": "ERR_TIMEOUT"}, "AI extraction timed out. Please retry."
        except Exception as exc:
            return False, {"error_code": "ERR_NETWORK"}, f"Failed to connect to backend: {exc}"

    @staticmethod
    def list_meetings(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """GET /api/v1/meetings"""
        try:
            params = {}
            if status:
                params["status"] = status
            res = requests.get(f"{API_V1_URL}/meetings", params=params, timeout=10)
            payload = res.json()
            if payload.get("success"):
                return payload.get("data", [])
            return []
        except Exception:
            return []

    @staticmethod
    def get_meeting_detail(meeting_id: str) -> Optional[Dict[str, Any]]:
        """GET /api/v1/meetings/{id}"""
        try:
            res = requests.get(f"{API_V1_URL}/meetings/{meeting_id}", timeout=10)
            payload = res.json()
            if payload.get("success"):
                return payload.get("data")
            return None
        except Exception:
            return None

    @staticmethod
    def get_action_items(meeting_id: str, action_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """GET /api/v1/meetings/{id}/actions"""
        try:
            params = {}
            if action_status:
                params["action_status"] = action_status
            res = requests.get(f"{API_V1_URL}/meetings/{meeting_id}/actions", params=params, timeout=10)
            payload = res.json()
            if payload.get("success"):
                return payload.get("data", [])
            return []
        except Exception:
            return []

    @staticmethod
    def edit_action_item(
        action_id: str,
        title: Optional[str] = None,
        owner: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """PATCH /api/v1/actions/{id}"""
        try:
            body = {}
            if title is not None:
                body["title"] = title
            if owner is not None:
                body["owner"] = owner
            if due_date is not None:
                body["due_date"] = due_date
            if priority is not None:
                body["priority"] = priority

            res = requests.patch(f"{API_V1_URL}/actions/{action_id}", json=body, timeout=10)
            payload = res.json()
            if payload.get("success"):
                return True, payload.get("data"), "Action item updated."
            return False, None, payload.get("message", "Edit failed.")
        except Exception as exc:
            return False, None, f"Network error: {exc}"

    @staticmethod
    def approve_action_item(action_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """POST /api/v1/actions/{id}/approve"""
        try:
            res = requests.post(f"{API_V1_URL}/actions/{action_id}/approve", timeout=10)
            payload = res.json()
            if payload.get("success"):
                return True, payload.get("data"), "Action item APPROVED."
            return False, None, payload.get("message", "Approve failed.")
        except Exception as exc:
            return False, None, f"Network error: {exc}"

    @staticmethod
    def reject_action_item(action_id: str, reason: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """POST /api/v1/actions/{id}/reject"""
        try:
            body = {"reason": reason} if reason else {}
            res = requests.post(f"{API_V1_URL}/actions/{action_id}/reject", json=body, timeout=10)
            payload = res.json()
            if payload.get("success"):
                return True, payload.get("data"), "Action item REJECTED."
            return False, None, payload.get("message", "Reject failed.")
        except Exception as exc:
            return False, None, f"Network error: {exc}"

    @staticmethod
    def sync_meeting_github(meeting_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """POST /api/v1/meetings/{id}/sync"""
        try:
            res = requests.post(f"{API_V1_URL}/meetings/{meeting_id}/sync", timeout=30)
            payload = res.json()
            if payload.get("success"):
                return True, payload.get("data"), payload.get("message", "Synced to GitHub.")
            return False, None, payload.get("message", "GitHub sync failed.")
        except Exception as exc:
            return False, None, f"Network error: {exc}"

    @staticmethod
    def get_audit_trail(meeting_id: str) -> List[Dict[str, Any]]:
        """GET /api/v1/meetings/{id}/audit"""
        try:
            res = requests.get(f"{API_V1_URL}/meetings/{meeting_id}/audit", timeout=10)
            payload = res.json()
            if payload.get("success"):
                return payload.get("data", [])
            return []
        except Exception:
            return []
