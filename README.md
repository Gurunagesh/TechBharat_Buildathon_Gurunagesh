# 🤖 Agentic AI Meeting Assistant

**TechBharat Cohort #2 Buildathon — Use Case B**  
Built by: **Mudamanchu GuruNagesh**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)](https://streamlit.io/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why This Project?

Modern teams spend valuable hours manually converting meeting discussions into actionable tasks. Existing tools summarize conversations but lack governance, human approval, auditability, and safe integration with external issue trackers.

This project demonstrates an enterprise-ready **Agentic AI Workflow** that combines LLM-powered extraction with deterministic validation, state-machine governance, human review, and controlled GitHub synchronization.

---

## Problem Statement

Teams waste hours manually extracting action items from meeting transcripts. Important decisions get lost, owners aren't assigned, and deadlines are missed.

This system solves that by using AI to automatically extract structured meeting intelligence from transcripts, requiring **human approval before creating any external tickets** — enforcing zero unapproved side-effects.

---

## Design Principles

- **Human-in-the-Loop**: Strict human approval required before any external API mutation (e.g. GitHub Issues creation).
- **Zero Unapproved Actions**: State machine guarantees no side effects without explicit human review.
- **Deterministic State Transitions**: State Machine is the sole authority for entity status transitions.
- **Idempotent Transcript Ingestion**: SHA-256 content hashing prevents duplicate processing and task creation.
- **Structured AI Outputs**: Pydantic v2 schemas strictly validate all LLM JSON responses.
- **Complete Auditability**: Immutable audit trail logs every system action with timestamp, actor, and payload.
- **Graceful Degradation**: Dual LLM provider fallback (Gemini → Grok) plus offline Mock Mode for stability.

---

## Architecture Overview

```
Streamlit UI (Port 8501)
       │  HTTP REST
       ▼
FastAPI Backend (Port 8000)
       │
  ┌────┴────────────────────────┐
  ▼                             ▼
MySQL DB (Port 3306)     Gemini 1.5 Flash
                         (+ Grok/xAI Fallback)
                         (+ Mock LLM Demo Mode)
                               │
                               ▼
                        GitHub Issues API
```

---

## Enterprise Characteristics

- **Layered Architecture**: Clean separation between API, Business Logic, LLM Providers, Data Models, and UI.
- **State Machine Governance**: Strict transition rules prevent illegal state mutations.
- **Dependency Injection**: FastAPI `Depends()` for database session lifecycle management.
- **Typed Domain Exceptions**: Custom exception hierarchy mapped cleanly to HTTP status codes.
- **Structured Logging & Telemetry**: JSON log formats with custom event types and execution timing.
- **Retry & Fallback Strategy**: Configurable retry policies with automated model failover.

-----
[![Live Demo](https://img.shields.io/badge/Demo-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit)](https://agentic-ai-meeting-assistant.streamlit.app/)
[![API Docs](https://img.shields.io/badge/API-FastAPI%20Docs-009688?style=for-the-badge&logo=fastapi)](https://meeting-assistant-backend-binn.onrender.com/docs)


-----

## Buildathon Requirement Mapping

| Buildathon Requirement | System Implementation | Verification / Evidence |
|------------------------|-----------------------|-------------------------|
| **Human Approval Control** | `ApprovalService` & `StateMachine` | Actions start as `PENDING_REVIEW` until manually approved |
| **Audit Trail** | `AuditService` & `audit_logs` MySQL table | Every event logged with `actor`, `event_type`, and `payload` |
| **Zero Unapproved Side-Effects** | Enforced by State Machine | `SyncService` rejects unapproved action items |
| **Idempotency & Deduplication** | `DuplicateChecker` (SHA-256 digest) | Re-uploading identical file returns existing meeting |
| **External Integration** | `GitHubService` via PyGithub | Issues created exclusively for `APPROVED` action items |
| **Structured AI Outputs** | `GeminiClient` with Pydantic schemas | Validates output format, confidence scores, & quotes |
| **Fallback Strategy** | `GeminiClient` → `GrokClient` → `MockLLM` | Automatic failover on API failure or missing keys |

---

## Technology Stack

| Layer        | Technology                              |
|--------------|-----------------------------------------|
| Frontend     | Streamlit                               |
| Backend      | FastAPI + Uvicorn                       |
| Database     | MySQL 8.0 + SQLAlchemy 2.0              |
| Primary LLM  | Google Gemini `gemini-1.5-flash`        |
| Fallback LLM | Grok / xAI (OpenAI-compatible)          |
| Demo Mode    | Built-in Mock LLM (no API key needed)   |
| Integration  | GitHub Issues via PyGithub              |
| Validation   | Pydantic v2                             |
| Infra        | Docker Compose                          |

---

## Key Features

- ✅ **Upload transcripts** (`.txt`, `.vtt`, `.srt`)
- ✅ **AI extraction** using structured Pydantic outputs with deterministic validation
- ✅ **Evidence links** — every action item linked to exact transcript quote
- ✅ **Confidence scoring** — flag low-confidence items (threshold ≥ 0.70) for human review
- ✅ **Human review** — edit, approve, or reject before any external action
- ✅ **GitHub Issues** — created only after explicit human approval
- ✅ **Duplicate detection** — SHA-256 hash prevents re-processing (reprocesses FAILED runs)
- ✅ **Audit trail** — immutable log of every system event
- ✅ **State Machine Engine** — deterministic workflow state transitions
- ✅ **Demo/Offline mode** — works without any API keys via Mock LLM

---

## Getting Started

### Prerequisites

- Docker Desktop installed and running
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Gurunagesh/TechBharat_Buildathon_Gurunagesh.git
cd TechBharat_Buildathon_Gurunagesh
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env — at minimum set your API keys, or leave MOCK_LLM=true for demo
```

### 3. Start the Application

```bash
docker-compose up --build -d
```

### 4. Access the App

| Service         | URL                                  |
|-----------------|--------------------------------------|
| Streamlit UI    | http://localhost:8501                |
| FastAPI Swagger | http://localhost:8000/docs           |
| Health Check    | http://localhost:8000/api/v1/health  |

---

## Demo Mode (No API Key Required)

Set `MOCK_LLM=true` in your `.env` file (this is the default). The system will use pre-built high-fidelity mock extractions for all 4 benchmark transcripts — no Gemini or Grok key needed.

**Benchmark transcripts are in `samples/`:**

| File                    | Format | Scenario                   |
|-------------------------|--------|----------------------------|
| `simple_meeting.txt`    | TXT    | Sprint planning (7 actions)|
| `vtt_meeting.vtt`       | VTT    | Q3 roadmap sync (4 actions)|
| `srt_meeting.srt`       | SRT    | Bug triage (4 actions)     |
| `ambiguous_meeting.txt` | TXT    | Ambiguous/low-confidence   |

---

## Core Agent Workflow

```
1. Upload meeting transcript (.txt / .vtt / .srt)
        ↓
2. AI extracts: summary, decisions, risks, action items (with evidence)
        ↓
3. Human reviews extracted tasks in Streamlit workspace
        ↓
4. Edit owner / due date → Reject irrelevant tasks → Approve valid tasks
        ↓
5. Click "Sync to GitHub" → Issues created for APPROVED tasks only
        ↓
6. Audit trail records every event (UPLOAD, EXTRACT, APPROVE, REJECT, SYNC)
        ↓
7. Re-upload same file → Duplicate detected, no re-processing (idempotent)
```

---

## Project Structure

```
TechBharat-Buildathon-Gurunagesh/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, DB, Logging, Exceptions
│   │   ├── models/         # SQLAlchemy ORM models + Enums
│   │   ├── schemas/        # Pydantic API response models
│   │   ├── services/
│   │   │   ├── llm/        # Gemini + Grok + Mock clients, prompts
│   │   │   └── business/   # Extraction, approval, sync, audit services
│   │   ├── workflow/       # State machine (sole state controller)
│   │   ├── integrations/   # GitHub Issues service
│   │   └── api/            # FastAPI route handlers
│   └── main.py
├── frontend/
│   ├── app.py              # Streamlit single-entry router
│   ├── views/              # Page render functions (hidden from Streamlit nav)
│   ├── components/         # Reusable UI components
│   └── utils/              # API client, session state manager
├── database/
│   └── schema.sql          # MySQL DDL
├── samples/                # 4 benchmark transcript files (txt, vtt, srt)
├── tests/                  # Pytest unit & integration tests (12 tests)
├── docker-compose.yml
└── .env.example
```

---

## Performance Benchmark

| Metric / Mode | Value |
|---------------|-------|
| **Mock LLM Extraction Latency** | < 1.0 second |
| **Gemini 1.5 Flash Latency** | 3.0 – 8.0 seconds |
| **Parser Processing Time** | < 50 milliseconds |
| **Idempotency Hash Time** | < 5 milliseconds (SHA-256) |
| **Supported Formats** | `.txt`, `.vtt` (WebVTT), `.srt` (SubRip) |

---

## API Endpoints

| Method | Endpoint                              | Purpose                    |
|--------|---------------------------------------|----------------------------|
| GET    | `/api/v1/health`                      | Health check               |
| POST   | `/api/v1/meetings/upload`             | Upload transcript          |
| GET    | `/api/v1/meetings`                    | List all meetings          |
| GET    | `/api/v1/meetings/{id}`               | Get meeting detail         |
| PATCH  | `/api/v1/actions/{id}`                | Edit action item           |
| POST   | `/api/v1/actions/{id}/approve`        | Approve action item        |
| POST   | `/api/v1/actions/{id}/reject`         | Reject action item         |
| POST   | `/api/v1/meetings/{id}/sync`          | Sync approved → GitHub     |
| GET    | `/api/v1/meetings/{id}/audit`         | View audit trail           |

Full interactive documentation: **http://localhost:8000/docs**

---

## Security & Compliance

- **Secrets Isolation**: API keys managed strictly via `.env` (never committed to repository).
- **Human Gatekeeping**: No automated external API calls without explicit human approval.
- **Audit Logging**: Immutable tracking of all user actions and LLM executions.
- **Fail-safe Defaults**: Low confidence items flagged for manual review rather than auto-accepted.

---

## Testing Strategy & Execution

```bash
docker-compose exec backend pytest -v
```

The test suite covers:
- **Unit Tests**: State machine transitions, SHA-256 hash deduplication, date resolution logic.
- **LLM Schema Tests**: Pydantic model validation on raw response parsing.
- **API Integration Tests**: Endpoint request/response envelope validation.

---

## Future Enhancements

- 🔊 **Audio Transcription Support**: Integration with Whisper / Deepgram for raw audio files.
- 💬 **Slack & Jira Integrations**: Multi-platform ticket dispatch beyond GitHub Issues.
- 📅 **Google Calendar Sync**: Auto-schedule meetings for extracted open questions/follow-ups.
- 🔒 **Role-Based Access Control (RBAC)**: Multi-tenant user auth with reviewer permissions.

---

## License

MIT
