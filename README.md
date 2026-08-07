# 🤖 Agentic AI Meeting Assistant

**TechBharat Cohort #2 Buildathon — Use Case B**  
Built by: **Mudamanchu GuruNagesh**

---

## Problem Statement

Teams waste hours manually extracting action items from meeting transcripts. Important decisions get lost, owners aren't assigned, and deadlines are missed.

This system solves that by using AI to automatically extract structured meeting intelligence from transcripts, requiring **human approval before creating any external tickets** — enforcing zero unapproved side-effects.

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

## Tech Stack

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
- ✅ **AI extraction** — summary, decisions, risks, open questions, action items
- ✅ **Evidence links** — every action item linked to exact transcript quote
- ✅ **Confidence scoring** — flag low-confidence items for human review
- ✅ **Human review** — edit, approve, or reject before any external action
- ✅ **GitHub Issues** — created only after explicit human approval
- ✅ **Duplicate detection** — SHA-256 hash prevents re-processing
- ✅ **Audit trail** — immutable log of every system event
- ✅ **Graceful fallback** — Gemini → Grok if primary fails
- ✅ **Demo/Offline mode** — works without any API keys via Mock LLM

---

## Quick Start

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

## Workflow Demo

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

## Environment Variables

See [`.env.example`](.env.example) for a complete list. Key variables:

| Variable          | Required | Description                                    |
|-------------------|----------|------------------------------------------------|
| `MOCK_LLM`        | No       | `true` to run offline demo mode (default: true)|
| `GEMINI_API_KEY`  | No*      | Google Gemini API key (*not needed in mock mode)|
| `GROK_API_KEY`    | No       | xAI Grok fallback key                          |
| `GITHUB_TOKEN`    | No       | PAT for GitHub Issues integration              |
| `GITHUB_REPO`     | No       | `owner/repo` to push Issues to                 |

---

## Evaluation Criteria Coverage

| Criterion                 | Implementation                                        |
|---------------------------|-------------------------------------------------------|
| 80%+ Action Item Recall   | Multi-pass Gemini extraction + evidence quotes        |
| 75%+ Action Item Precision| Confidence score filtering (≥ 0.70 threshold)         |
| 85%+ Owner Accuracy       | Participant context map + UNASSIGNED fallback         |
| 90%+ Date Resolution      | `dateparser` anchored to meeting anchor date          |
| Latency < 3 mins          | `gemini-1.5-flash` + Pydantic structured JSON output  |
| Zero Unapproved Actions   | State machine enforces PENDING → APPROVED before sync |
| Idempotency               | SHA-256 transcript hash deduplication (auto-reprocess FAILED)|

---

## Running Tests

```bash
docker-compose exec backend pytest -v
# Expected: 12 tests passing
```

---

## Known Limitations

- Audio transcription not supported (text transcript input only)
- Single GitHub repository integration (Slack/Calendar: future)
- No authentication layer (mock user for hackathon scope)

---

## License

MIT
