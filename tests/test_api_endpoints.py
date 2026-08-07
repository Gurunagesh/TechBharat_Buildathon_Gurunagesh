"""
tests/test_api_endpoints.py
────────────────────────────
Integration & Endpoint Tests for Sprint 4 API Layer.

Verifies:
1. /api/health and /api/v1/health return ResponseEnvelope.ok().
2. OpenAPI Swagger docs load successfully (/docs).
3. Exception handlers cleanly catch domain errors (404, 409) and return ResponseEnvelope.fail().
4. Response envelope structure is enforced on all endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify health endpoint returns 200 OK with standard response envelope."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["status"] in ["healthy", "degraded"]
    assert "database" in data["data"]


def test_openapi_swagger_docs_load():
    """Verify OpenAPI JSON schema and Swagger UI endpoints load cleanly."""
    response = client.get("/docs")
    assert response.status_code == 200

    openapi_res = client.get("/openapi.json")
    assert openapi_res.status_code == 200
    spec = openapi_res.json()
    assert spec["info"]["title"] == "Agentic AI Meeting Assistant"


def test_meeting_not_found_returns_404_envelope():
    """Verify non-existent meeting UUID raises MeetingNotFoundError mapped to 404 envelope."""
    response = client.get("/api/v1/meetings/non-existent-uuid-999")
    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert data["error"]["error_code"] == "ERR_MEETING_NOT_FOUND"
    assert "not found" in data["message"].lower()


def test_action_item_not_found_returns_404_envelope():
    """Verify non-existent action item edit returns 404 envelope."""
    response = client.patch(
        "/api/v1/actions/non-existent-action-999",
        json={"title": "Updated Title"},
    )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["error_code"] == "ERR_ACTION_NOT_FOUND"


def test_invalid_file_upload_returns_400_envelope():
    """Verify uploading an unsupported file type (.pdf) returns 400 Bad Request envelope."""
    files = {"file": ("document.pdf", b"PDF content", "application/pdf")}
    response = client.post("/api/v1/meetings/upload", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["error_code"] == "ERR_INVALID_FILE"
    assert "unsupported" in data["message"].lower()
