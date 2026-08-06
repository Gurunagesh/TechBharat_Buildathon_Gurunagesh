# 🤖 Agentic AI Meeting Assistant

**TechBharat Cohort #2 Buildathon — Use Case B**  
Built by: **Mudamanchu GuruNagesh**

---

## Problem Statement

Teams waste hours manually extracting action items from meeting transcripts. Important decisions get lost, owners aren't assigned, and deadlines are missed.

This system solves that by using AI to automatically extract structured meeting intelligence from transcripts, requiring human approval before creating any external tickets — enforcing zero unapproved side-effects.

---

## Architecture Overview

```
Streamlit UI (Port 8501)
       │  HTTP REST
       ▼
FastAPI Backend (Port 8000)
       │
  ┌────┴────────────────┐
  ▼                     ▼
MySQL DB          Gemini 1.5 Flash
(Port 3306)       (+ Grok Fallback)
                        │
                        ▼
                 GitHub Issues API
```

---

## Tech Stack

| Layer       | Technology                              |
|-------------|-----------------------------------------|
| Frontend    | Streamlit                               |
| Backend     | FastAPI + Uvicorn                       |
| Database    | MySQL 8.0 + SQLAlchemy 2.0              |
| Primary LLM | Google Gemini `gemini-1.5-flash`        |
| Fallback LLM| Grok / xAI (OpenAI-compatible)          |
| Integration | GitHub Issues via PyGithub              |
| Validation  | Pydantic v2                             |
| Infra       | Docker Compose                          |

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
- ✅ **Graceful fallback** — Gemini → Grok if rate-limited

---

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Git
- Google Gemini API key (free tier)
- GitHub Personal Access Token (`repo` scope)

### 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/TechBharat-Buildathon-Gurunagesh.git
cd TechBharat-Buildathon-Gurunagesh
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 3. Start the Application

```bash
docker compose up --build
```

### 4. Access the App

| Service  | URL                    |
|----------|------------------------|
| Streamlit UI   | http://localhost:8501 |
| FastAPI Swagger | http://localhost:8000/docs |
| Health Check   | http://localhost:8000/api/health |

---

## Workflow Demo

```
1. Upload meeting transcript (.txt / .vtt / .srt)
        ↓
2. AI extracts: summary, decisions, risks, action items
        ↓
3. Human reviews extracted tasks in Streamlit
        ↓
4. Edit owner / date → Reject irrelevant tasks → Approve valid tasks
        ↓
5. Click "Sync to GitHub" → Issues created for APPROVED tasks only
        ↓
6. Audit trail updated with every event
        ↓
7. Re-upload same file → Duplicate detected, no re-processing
```

---

## Project Structure

```
TechBharat-Buildathon-Gurunagesh/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, DB, Logging
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic API response models
│   │   ├── services/
│   │   │   ├── llm/        # Gemini + Grok clients, prompts
│   │   │   └── business/   # Meeting, approval, sync services
│   │   ├── workflow/       # State machine (sole state controller)
│   │   ├── integrations/   # GitHub service
│   │   └── api/            # FastAPI route handlers
│   └── main.py
├── frontend/
│   └── app.py              # Streamlit application
├── database/
│   └── schema.sql          # MySQL DDL
├── samples/                # Benchmark transcript files
├── tests/                  # Pytest unit & integration tests
├── docker-compose.yml
└── .env.example
```

---

## API Endpoints

| Method | Endpoint                           | Purpose                    |
|--------|------------------------------------|----------------------------|
| GET    | `/api/health`                      | Health check               |
| POST   | `/api/meetings/upload`             | Upload transcript          |
| GET    | `/api/meetings`                    | List all meetings          |
| GET    | `/api/meetings/{id}`               | Get meeting detail         |
| PATCH  | `/api/actions/{id}`                | Edit action item           |
| POST   | `/api/actions/{id}/approve`        | Approve action item        |
| POST   | `/api/actions/{id}/reject`         | Reject action item         |
| POST   | `/api/meetings/{id}/sync`          | Sync approved → GitHub     |
| GET    | `/api/meetings/{id}/audit`         | View audit trail           |

---

## Environment Variables

See [`.env.example`](.env.example) for a complete list of required variables.

---

## Evaluation Criteria Coverage

| Criterion                    | Implementation                              |
|------------------------------|---------------------------------------------|
| 80%+ Action Item Recall      | Multi-pass Gemini extraction                |
| 75%+ Action Item Precision   | Confidence score filtering (≥ 0.70)         |
| 85%+ Owner Accuracy          | Participant context map + UNASSIGNED fallback|
| 90%+ Date Resolution         | `dateparser` anchored to meeting date        |
| Latency < 3 mins             | `gemini-1.5-flash` + Pydantic structured output |
| Zero Unapproved Actions      | State machine enforces PENDING → APPROVED first |
| Idempotency                  | SHA-256 transcript hash deduplication       |

---

## Known Limitations

- Audio transcription not supported (Phase 3 stretch goal)
- Single GitHub repository integration (Slack/Calendar: future)
- No authentication (mock user for hackathon scope)

---

## License

MIT
