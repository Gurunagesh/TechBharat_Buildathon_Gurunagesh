**Yes, i would like to choosing Use Case B (Agentic AI Meeting Assistant) is the right decision.**

The ChatGPT conversation correctly identified that Use Case B provides maximum opportunity to demonstrate end-to-end AI agent capabilities (reasoning, state validation, human approval, tool calls, and idempotency) rather than simple text summarization.

Looking at the official [TechBharat Cohort #2 Buildathon Use Cases document], here are critical **additional importance layers and technical nuances** you must incorporate into your setup to guarantee high evaluation scores:

---

## 1. Hard Constraints & Gatekeeper Requirements

Fail these and your project fails the track regardless of overall UI or feature polish:

* **Zero Unapproved Actions (Strict Threshold):**

* The evaluation criteria explicitly states: **"Zero unapproved actions."**

* *Implementation Layer:* Never trigger external APIs (GitHub Issues, Slack, Calendar) inside the LLM execution path. Enforce a two-stage pipeline:


1. **Drafting Stage:** Extracted items are saved in MySQL with a status of `PENDING_REVIEW`.
2. **Execution Stage:** External APIs are only invoked via a dedicated endpoint (`/api/approve`) triggered by a human user click on the review interface.






* **Idempotency & Duplicate Suppression:**

* The judges will re-run the exact same transcript file twice.


* *Implementation Layer:* Hash the ingested transcript file content (e.g., using `SHA-256`). Store this `transcript_hash` in your `meetings` table. If a duplicate transcript hash is detected, retrieve the existing meeting details instead of re-extracting tasks and re-executing integrations.





---

## 2. Technical Layers for Evaluation Metrics

The judges will evaluate against strict numerical targets:

| Metric Target | Technical Strategy to Guarantee Score |
| --- | --- |
| **80%+ Action Item Recall**<br> | **Multi-Pass Prompting:** Do not attempt to extract summaries, decisions, and action items in a single LLM call. Break parsing into distinct passes (Pass 1: Summary/Decisions, Pass 2: Action Items).

 |
| **75%+ Action Item Precision**<br> | **Confidence Filtering:** Have the LLM assign a `confidence_score` ($0.0 - 1.0$) to each extracted task. Filter out or auto-flag tasks below $0.70$ on the review screen.

 |
| **85%+ Owner Accuracy**<br> | **Participant Context Mapping:** Pass a list of known team members and their email addresses/handles into the LLM system prompt so it resolves names accurately (e.g., "Priya" $\rightarrow$ `priya@company.com`). If an owner cannot be matched, explicitly mark it as `UNASSIGNED`.

 |
| **90%+ Relative Date Resolution**<br> | **Anchor Date Injection:** Inject the explicit meeting date (e.g., *Meeting Date: Wednesday, Aug 5, 2026*) into the LLM system context. Use standard Python parsing libraries like `dateparser` to deterministically validate and parse relative strings like "by next Friday" into ISO format (`YYYY-MM-DD`).

 |
| **Latency Under 3 Minutes**<br> | Use structured extraction frameworks (such as Pydantic structured output) with models like `gemini-2.5-flash` or `gpt-4o-mini` to keep latency low.

 |

---

## 3. High-Impact Stretch Goals (Judge Differentiators)

To stand out from other participants, implement these specific stretch goals from the brief:

1. **Evidence Links (Timestamps / Text Snippets):**

* Map every action item back to the exact transcript line or timestamp where it was discussed (e.g., `[00:14:22] "John: I will update the database schema by Friday."`). Display this evidence link inside your Streamlit review drawer.




2. **Audit Log Trail:**

* Maintain a dedicated `audit_logs` table recording: `timestamp`, `event_type` (`EXTRACTED`, `EDITED`, `APPROVED`, `REJECTED`, `SYNCED`), `actor` (`AI_AGENT` or `HUMAN_USER`), and `payload`. Show this log in a separate Streamlit tab.





---

## 4. Recommended Submission Repository Structure

Align your project layout cleanly to reflect enterprise practices:

```text
TechBharat_Buildathon_MudamanchuGuruNagesh/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI endpoints (upload, approve, logs)
│   │   ├── core/            # Configs & DB connection
│   │   ├── services/        # AI Agents, Date Resolvers, Duplicate Checker
│   │   ├── integrations/    # GitHub / Slack payload creators
│   │   └── models/          # SQLAlchemy schemas
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── app.py               # Streamlit application entrypoint
│   └── requirements.txt
├── database/
│   └── schema.sql           # MySQL initial tables
├── samples/                 # Test transcripts for live demo
├── docker-compose.yml       # Orchestrates FastAPI + MySQL + Streamlit
└── README.md

```
---------
Here is a complete, execution-ready 48-hour plan tailored for **Use Case B (Agentic AI Meeting Assistant)**, addressing all 10 strategic questions raised at the end of your session along with key architectural recommendations.

---

## 🏗️ Direct Answers to the 10 Technical Questions

| # | Question | Decision & Recommendation | Technical Justification |
| --- | --- | --- | --- |
| **1** | **LLM Choice** | **Gemini 2.5 Flash / GPT-4o-mini** | Low latency, highly accurate structured outputs (via Pydantic), and cost-effective.

 |
| **2** | **Input Scope** | **Transcript files (`.vtt`, `.srt`, `.txt`)**<br> | Starting with transcripts meets all core requirements cleanly. (Keep Whisper API modular as a stretch goal for `.mp3`).

 |
| **3** | **Tool Integration** | **GitHub Issues**<br> | Easiest to test, demo-friendly, and simple to reset via API.

 |
| **4** | **Database** | **MySQL**<br> | Aligns with your comfort level and handles transactional states (`PENDING`, `APPROVED`, `SYNCED`) cleanly.

 |
| **5** | **Backend Architecture** | **FastAPI + Streamlit**<br> | Streamlit handles UI fast, while FastAPI enforces clear enterprise boundary separation.

 |
| **6** | **Deployment Strategy** | **Local Demo + Docker Compose**<br> | Judges prioritize working code. A local `docker-compose up` eliminates cloud network failure risks during live evaluation.

 |
| **7** | **Authentication** | **Intentionally Omitted** | Avoid building auth in a 48h hackathon. Use a mock current user (`Admin / Product Manager`) to save hours. |
| **8** | **Code Design** | **Modular Layered Architecture**<br> | Keep `agents/`, `services/`, `integrations/`, and `database/` separated.

 |
| **9** | **Evidence Linking** | **Text/Timestamp Snippets**<br> | Extract exact quote snippets (e.g., `[14:22] "John: I will complete this by Friday"`) to prove AI reasoning.

 |
| **10** | **Testing Strategy** | **Pre-fabricated Benchmark Files** | Create 4 test transcript files covering: simple items, ambiguous owners, missing dates, and duplicate uploads.

 |

---

## ⏱️ 48-Hour Hourly Execution Roadmap

```
[Day 1: Setup & Core Extraction] ──► [Day 2: Validation & Review UI] ──► [Day 3: Integrations & Demo Prep]
  (Checkpoint 1 @ 11 AM)               (Checkpoint 2 @ 5 PM)                 (Checkpoint 3 @ 11 AM)

```

### Day 1: Foundation & Extraction (Hours 0 – 16)

* **Hours 0–3:** Set up repository `TechBharat_Buildathon_MudamanchuGuruNagesh`. Scaffold FastAPI backend, MySQL database schema, and Streamlit app.


* **Hours 3–7:** Build file ingestion logic (`.txt`, `.vtt`, `.srt` parser) and duplicate checking via transcript SHA-256 hash.


* **Hours 7–12:** Implement the Multi-Pass LLM Extraction Agent using Pydantic structured schemas:


* *Pass 1:* Executive Summary & Decisions.


* *Pass 2:* Action Items with Owner, Relative Date, Priority, Confidence Score, and Evidence Quote.




* **Hours 12–16:** Test parser on sample transcripts and commit to GitHub before **Checkpoint 1**.



### Day 2: Validation, UI, & Human Approval (Hours 17 – 32)

* **Hours 17–22:** Build Python-side Deterministic Validation Layer:


* Resolve relative dates against the meeting date using standard date parsing.


* Resolve owners against a known participant list or flag as `UNASSIGNED`.




* **Hours 22–27:** Build the Streamlit Human Review Interface:


* Display extracted tasks with editable fields (Owner, Date, Priority).


* Add Action buttons: **Approve**, **Reject**, or **Edit** per item.




* **Hours 27–32:** Store status transitions in MySQL (`PENDING_REVIEW` $\rightarrow$ `APPROVED`) and log audit entries. Commit code before **Checkpoint 2**.



### Day 3: Integrations, Idempotency, & Polishing (Hours 33 – 48)

* **Hours 33–38:** Implement the GitHub API tool integration:


* Create GitHub Issues only for items marked `APPROVED`.


* Update task status in MySQL to `SYNCED`.


* **Hours 38–42:** Add Duplicate Suppression (re-uploading the same file reloads existing records without re-triggering task creation).


* **Hours 42–45:** Build the Audit Log view tab in Streamlit.


* **Hours 45–48:** Perform a full demo trial run following the exact suggested evaluation narrative. Final push before **Checkpoint 3** and project submission.



---

## 🎯 Key Differentiator Layers to Score Max Points

1. **Evidence / Reasoning Column:** Display the raw quote snippet from the transcript inside the review UI. This immediately proves to the judges that the extraction is faithful.


2. **Strict Guardrails / Safety:** Ensure no network calls happen until the user clicks **Approve** on the review UI.


3. **Audit Log Drawer:** Show an explicit timeline table (`Timestamp`, `Actor`, `Action`, `Item_ID`) in Streamlit to satisfy the zero unapproved action requirement.
---------
Here is a clear breakdown of why these specific choices make sense for a **48-hour hackathon**, along with practical recommendations on what to adopt and what to skip.

---

## 1. Why GitHub Issues vs. Jira, Slack, Calendar, or Gmail?

While the problem brief permits any of these integrations, **GitHub Issues is the fastest, safest, and most demo-friendly choice** for a 48-hour build:

| Metric / Criteria | **GitHub Issues** 🟢 | **Slack / Teams** 🟡 | **Jira / Asana** 🔴 | **Google Calendar / Gmail** 🔴 |
| --- | --- | --- | --- | --- |
| **API Setup Effort** | **5 minutes** (1 Personal Access Token / PAT)

 | **30+ minutes** (Slack App setup, Webhooks, Bot Scopes) | **45+ minutes** (Atlassian Cloud API, Workspace tokens) | **1+ hour** (GCP Console, OAuth2 Client ID, Refresh tokens) |
| **Judge Accessibility** | **100% Public** (Judges can view issues live on your public project repo)

 | Private (Requires inviting judges to a custom Slack workspace) | Semi-private (Requires Atlassian workspace invite) | Private (Requires personal Google account permissions) |
| **Code Implementation** | **~15 lines of Python code** (`PyGithub` or standard `httpx` POST) | Requires Slack Webhook SDK | Requires Atlassian REST client | Requires Google API Client & token flow |
| **Demo Reset & Cleanup** | Delete/Close test issues in 1 click | Hard to purge messages dynamically | Complex board cleanup | Pollutes actual calendar/inbox |

> **Recommendation:** Use **GitHub Issues** as your primary integration to meet the mandatory requirement. If you have extra time on Day 3, add Slack Webhooks as a quick secondary stretch goal.
> 
> 

---

## 2. Vector DBs & AI Frameworks: What to Use vs. What to Skip

In a 48-hour hackathon, every hour spent debugging framework abstractions is an hour lost on core requirements.

### A. Vector Database (ChromaDB)

* **Verdict:** ❌ **SKIP IT (Over-engineering for 48 Hours)**
* **Why:**
1. A standard 45-minute meeting transcript is roughly 5,000–8,000 words (~7,000 tokens).
2. Modern LLMs like **Gemini 2.5 Flash** or **GPT-4o-mini** easily handle context windows from 128K up to 1M+ tokens.
3. Passing the full raw transcript directly to the LLM guarantees **100% context visibility** without chunking loss or retrieval failure points.
4. MySQL handles storing and querying past transcript text perfectly fine.





---

### B. AI Frameworks (LangChain vs. LangGraph vs. Pydantic AI vs. Native SDK)

```
       Complexity & Debugging Overhead
Low ──────────────────────────────────────────► High

[ Native SDK / Pydantic ] ───► [ LangChain ] ───► [ LangGraph ]
  (Fastest & Safest)           (Medium)            (Excessive Overhead)

```

#### 1. Pydantic / Pydantic AI — ✅ **STRONGLY RECOMMENDED**

* **Why:** You need structured outputs (JSON) containing specific fields: `title`, `owner`, `due_date`, `priority`, `confidence_score`, and `evidence_quote`.


* **Reasoning:** Defining a standard Pydantic schema ensures the LLM returns strictly typed objects. If a field is missing, validation fails fast before hitting MySQL.



```python
# Example Pydantic Schema for Action Items
from pydantic import BaseModel, Field
from typing import Optional

class ActionItem(BaseModel):
    title: str = Field(description="Action item task description")
    owner: str = Field(description="Assigned person or UNASSIGNED")
    due_date: Optional[str] = Field(description="Resolved ISO date YYYY-MM-DD")
    priority: str = Field(description="HIGH, MEDIUM, or LOW")
    confidence_score: float = Field(description="Score between 0.0 and 1.0")
    evidence_quote: str = Field(description="Exact transcript quote snippet")

```

#### 2. LangChain & LangGraph — ❌ **SKIP FOR 48H SPRINT**

* **Why:**
* **LangChain:** Adds heavy abstraction wrappers over API calls that make simple prompt adjustments harder to debug when tokens get truncated.
* **LangGraph:** Designed for multi-agent cyclical loops. Your pipeline is a **linear 2-stage flow** (`Ingest` $\rightarrow$ `Extract & Validate` $\rightarrow$ `Store in DB` $\rightarrow$ `Human Approve` $\rightarrow$ `Sync to GitHub`). A linear pipeline is much easier to write and control using standard Python functions in FastAPI.





---

## 💡 Summary of Your Ideal Stack

* **Frontend:** Streamlit


* **Backend API:** FastAPI


* **Database:** MySQL (State: `PENDING_REVIEW`, `APPROVED`, `SYNCED`)


* **LLM Calls:** Direct Google GenAI / OpenAI SDK with **Pydantic** structured outputs


* **Tool Integration:** GitHub Issues via `PyGithub`

* **Deployment:** Local Docker Compose (`fastapi` + `streamlit` + `mysql`)



---

So, now mention your thoughts for my plane for 48 hours if i have enough then we will stretch the goals or, improve the project features. Right?
---------
I think your plan is **very strong**. If I were evaluating it as a Buildathon judge, I'd score the **architecture and planning** around **9.5/10**.

However, there are a few places where I would adjust the plan to maximize the probability of a successful submission within 48 hours.

---

# Overall Assessment

| Aspect               |  Score | Comments                                   |
| -------------------- | -----: | ------------------------------------------ |
| Requirement Coverage |  10/10 | Covers almost every mandatory requirement. |
| Architecture         |  10/10 | Clean separation of concerns.              |
| Scalability          |   9/10 | More than enough for a hackathon.          |
| Demo Potential       |  10/10 | Strong narrative.                          |
| Time Feasibility     | 7.5/10 | This is the biggest concern.               |

Your biggest risk is **not technical**.

It is **scope management**.

---

# The Trap I Think You're Falling Into

Right now, your plan resembles a **2–3 week engineering sprint**, not a **48-hour Buildathon**.

Your architecture is excellent, but you're planning to build:

* FastAPI
* Streamlit
* MySQL
* Docker
* Pydantic
* GitHub Integration
* Multi-pass LLM
* Duplicate Detection
* Audit Logs
* Evidence Links
* Date Resolution
* Owner Resolution
* Confidence Filtering
* Structured Outputs
* Validation Layer
* Review UI

That's a lot.

Individually, each feature is reasonable. Collectively, they create many integration points where bugs can appear.

---

# I Would Reframe the Project Into Three Phases

## Phase 1 — Guaranteed Submission (First Priority)

This phase should satisfy **all mandatory Buildathon requirements**. 

Features:

* Streamlit UI
* FastAPI backend
* MySQL
* Transcript upload
* Multi-pass LLM extraction
* Human review
* Approve/Reject
* GitHub Issue creation
* Audit log
* SHA-256 duplicate detection

If this works reliably, you already have a competitive submission.

---

## Phase 2 — Quality Improvements

Only after Phase 1 is complete:

* Better prompts
* Confidence filtering
* Date parser
* Owner resolution
* Better UI
* Better README
* Error handling
* Loading indicators

These improve polish without changing the core architecture.

---

## Phase 3 — Stretch Goals

Only if there is time:

* Audio transcription
* Slack integration
* Meeting analytics
* Cross-meeting memory
* Live mode
* Multi-language support

These are nice differentiators but not worth jeopardizing the mandatory requirements.

---

# One Design Change I Strongly Recommend

Instead of thinking:

```text
AI Agent
```

Think in terms of a **pipeline**.

```text
Transcript

↓

Parser

↓

Extractor

↓

Validator

↓

Storage

↓

Human Review

↓

Approval

↓

GitHub

↓

Audit Log
```

Each stage has:

* Input
* Output
* Responsibility

This makes debugging much easier during a hackathon.

---

# Another Improvement: Build a "Feature Kill Switch"

Suppose GitHub integration fails because of an API issue.

Your project should still be demoable.

For example:

```text
config.py

ENABLE_GITHUB = True
ENABLE_EMAIL = False
ENABLE_SLACK = False
```

If GitHub has a problem, disable it temporarily and continue demonstrating the rest of the workflow.

---

# Another Important Layer: Demo Reliability

Ask yourself:

> "If the internet disappears for five minutes, what still works?"

Try to make these work offline:

* Upload transcript
* Parsing
* Database
* Review UI
* Audit log

Only the LLM call and GitHub integration should depend on external services.

---

# Another Layer: Observability

Don't make the system feel like a black box.

Show progress such as:

```text
✔ Transcript uploaded

✔ Parsed successfully

✔ AI extraction complete

✔ Validation complete

✔ Stored in database

✔ Awaiting approval

✔ GitHub issue created

✔ Audit log updated
```

This reassures judges that the system is progressing correctly.

---

# Another Layer: Explainability

For each extracted task, show something like:

```text
Task:
Update authentication module

Owner:
John

Due Date:
2026-08-08

Confidence:
94%

Evidence:
"I'll finish the authentication changes by Friday."
```

This builds trust in the AI's output.

---

# Another Layer: Enterprise Thinking

Many hackathon teams stop at "it works."

Ask:

* Can the system recover from failures?
* Can it be restarted safely?
* Can it be extended with another integration?
* Can another developer understand the codebase?

A clean folder structure, modular services, and good documentation will help here.

---

# Another Layer: README Quality

Many teams underestimate this.

A strong README should include:

* Problem statement
* Architecture diagram
* Tech stack
* Folder structure
* Setup instructions
* Environment variables
* Screenshots
* Demo GIF/video
* API endpoints
* Database schema
* Future improvements

Judges often review the repository before or after the demo.

---

# What I Would Remove

To maximize success in 48 hours, I would postpone:

* ❌ ChromaDB
* ❌ LangChain
* ❌ LangGraph
* ❌ OAuth authentication
* ❌ Multi-agent orchestration
* ❌ Complex caching
* ❌ Kubernetes
* ❌ Cloud deployment unless it becomes effortless

None of these are required by the Buildathon brief, and each adds complexity.

---

# My Final Recommendation

I would organize the work into **three milestones**:

### Milestone 1 (Must Finish)

> "A complete, working system that satisfies every mandatory requirement."

### Milestone 2 (Should Finish)

> "A polished, reliable system with validation, confidence scoring, and a better user experience."

### Milestone 3 (Nice to Have)

> "Stretch goals that differentiate the project if time permits."

---

## One suggestion I believe will have the biggest payoff

Given your background and the way you approach projects, don't think of this as "building a hackathon app." Think of it as building a **small enterprise AI product**.

That means we'll spend the first few hours designing the architecture, database schema, prompts, APIs, and UI flow before coding. A solid blueprint will reduce rework, help you move faster during the Buildathon, and make the final project look much more professional.

I think that's the highest-return investment for the limited 48-hour window.
----------
### My Assumptions:

> **"AI IDEs make development 5–10× faster, therefore I should be able to build all three milestones in 48 hours."**

That is **partially true**, but it only applies to **code generation**, not **product completion**.

The missing layer is that a software project is much more than writing code.

---

# The Software Development Iceberg

Most beginners (and even many experienced developers using AI) think software development looks like this:

```text
Idea
   ↓
AI writes code
   ↓
Project finished
```

In reality, it looks like this:

```text
                    Product
                       ▲
                Demo Story
                       ▲
              Testing & Validation
                       ▲
            Integration & Debugging
                       ▲
            Runtime Configuration
                       ▲
             Architecture Decisions
                       ▲
             Prompt Engineering
                       ▲
             AI Generated Code
```

Notice where AI IDEs help:

They accelerate **one layer**—code generation.

They don't automatically solve the layers above it.

---

# Think in Terms of "Time Buckets"

Let's estimate a realistic breakdown for a 48-hour hackathon.

| Activity               | Without AI IDE | With AI IDE |
| ---------------------- | -------------: | ----------: |
| Writing code           |           20 h |         5 h |
| Architecture decisions |            4 h |         4 h |
| Prompt engineering     |            5 h |         5 h |
| Debugging              |            8 h |       5–8 h |
| Integration            |            5 h |         4 h |
| API setup              |            2 h |         2 h |
| Testing                |            6 h |         6 h |
| Demo preparation       |            3 h |         3 h |

Notice something interesting.

AI reduced **coding time dramatically**.

It barely reduced the other activities.

Those other activities often dominate hackathons.

---

# Where AI IDEs Shine

I would absolutely use Antigravity (or similar tools) aggressively for:

✅ FastAPI scaffolding

✅ Streamlit UI

✅ SQLAlchemy models

✅ MySQL schema

✅ CRUD APIs

✅ Pydantic models

✅ Docker Compose

✅ README generation

✅ Unit test skeletons

✅ GitHub Actions

These are repetitive engineering tasks.

---

# Where AI IDEs Don't Remove the Need for Judgment

## 1. Prompt Quality

Suppose the AI generates:

```python
summary = model.generate(transcript)
```

Looks fine.

But then you notice:

* Action items are missing.
* Owners are wrong.
* Dates are hallucinated.

Now you're iterating on prompts, examples, schemas, and validation.

That takes experimentation.

---

## 2. Integration Bugs

Example:

```
GitHub Issue API

↓

401 Unauthorized

↓

PAT permissions wrong

↓

Repository scope missing

↓

Token regenerated

↓

Works
```

No AI IDE can know your token configuration or repository permissions.

---

## 3. Runtime Behavior

The code compiles.

Then:

```
Upload transcript

↓

LLM succeeds

↓

Database insert succeeds

↓

GitHub API times out

↓

UI spins forever
```

Now you need retries, error messages, and recovery logic.

---

## 4. Human-in-the-Loop Safety

The Buildathon requires that nothing is executed before approval. 

An AI IDE can generate the approval endpoint.

It cannot prove that **every possible execution path** respects that safety rule.

You still need to verify the state transitions yourself.

---

## 5. Demonstration

This is probably the most underestimated part.

Imagine two teams.

### Team A

Amazing architecture.

15 features.

Demo crashes once.

Judges get confused.

---

### Team B

8 features.

Everything works.

Clear explanation.

Smooth demo.

Guess who usually wins?

Team B.

Because hackathons evaluate a working product, not only engineering ambition.

---

# The Biggest Missing Layer

You are optimizing for **development speed**.

The judges optimize for **confidence**.

Those are different objectives.

A judge unconsciously asks:

> "Do I trust this system?"

Trust comes from:

* predictable behavior
* clean UI
* evidence
* audit logs
* graceful failures
* clear explanations

—not from having the most features.

---

# Here's Where I Slightly Disagree with the Earlier Recommendation

The earlier recommendation says:

> Don't build Milestone 3 until Milestone 1 and 2 are complete.

I would refine that:

**You don't need to wait until Hour 37 to think about stretch goals.**

Instead, architect for them from the beginning.

For example:

```text
Service Layer

├── TranscriptService
├── ExtractionService
├── ApprovalService
├── GitHubService
├── AuditService
├── AnalyticsService (placeholder)
└── MemoryService (placeholder)
```

Even if `AnalyticsService` and `MemoryService` are empty initially, the architecture is ready.

Then, if you have spare time, you implement them without restructuring the project.

---

# My Recommendation: Build "Horizontally," Not "Vertically"

Don't think:

```text
Milestone 1

↓

Milestone 2

↓

Milestone 3
```

Think:

```text
Core Architecture
│
├── Upload ✓
├── Extraction ✓
├── Review ✓
├── Approval ✓
├── GitHub ✓
├── Audit ✓
└── Duplicate Check ✓
```

Once the backbone exists, improve each component incrementally:

```text
Upload
    MVP
      ↓
Better validation
      ↓
Multiple file formats

Extraction
    MVP
      ↓
Confidence scoring
      ↓
Evidence links

Approval
    MVP
      ↓
Editable fields
      ↓
Bulk approval

GitHub
    MVP
      ↓
Labels
      ↓
Priority mapping
```

This approach ensures you always have a working end-to-end system while continuously improving it.

---

# My Final Recommendation

I would absolutely leverage Antigravity to its fullest. In fact, I'd expect it to reduce implementation time substantially.

But I would **not** use the saved time primarily to add more features.

I would invest it in:

1. Better prompt engineering.
2. More edge-case testing.
3. Stronger error handling.
4. Cleaner architecture.
5. Better demo flow.
6. More polished documentation.

If, after that, you still have time, then add stretch goals.

That's the strategy that maximizes your chances of both **finishing** and **scoring well** in a 48-hour judged Buildathon.
---------

### SUMMARY OF PROJECT LIFELIFECYCLE:

You said:

> **Project → Architecture → Code → Testing**

I would change it to:

> **Problem → Requirements → Architecture → Design → Implementation → Validation → Hardening → Demo**

The biggest mistake teams make is jumping from architecture directly into coding.

---

# The Complete Enterprise AI Product Lifecycle

Think of this as your master blueprint before writing a single line of code.

```
Business Problem
        │
        ▼
Requirements Analysis
        │
        ▼
Success Metrics
        │
        ▼
MVP Scope
        │
        ▼
System Architecture
        │
        ▼
Low-Level Design
        │
        ▼
Implementation Plan
        │
        ▼
AI-Assisted Development
        │
        ▼
Validation & Testing
        │
        ▼
Hardening
        │
        ▼
Demo & Documentation
```

---

# Phase 0 — Problem Understanding ✅

This is already complete.

From the Buildathon document, you have:

* Selected **Use Case B**
* Understood mandatory requirements
* Understood stretch goals
* Understood evaluation metrics
* Understood constraints like zero unapproved actions and idempotency. 

So yes, **this phase is essentially done**.

---

# Phase 1 — Requirement Engineering

This is more than saying "I want these features."

Create a simple requirements table.

| Requirement          | Priority | Status  |
| -------------------- | -------- | ------- |
| Upload transcript    | Must     | Planned |
| Extract summary      | Must     | Planned |
| Extract action items | Must     | Planned |
| Human approval       | Must     | Planned |
| GitHub Issues        | Must     | Planned |
| Duplicate prevention | Must     | Planned |
| Audit log            | Must     | Planned |
| Evidence links       | Stretch  | Planned |
| Meeting analytics    | Stretch  | Planned |

This becomes your checklist.

---

# Phase 2 — Success Metrics

Don't ask only:

> Does it work?

Ask:

> How will I prove it works?

For every requirement, define acceptance criteria.

Example:

**Requirement**

Duplicate detection

**Acceptance Test**

* Upload transcript A
* Upload transcript A again
* No duplicate GitHub Issues are created
* Existing meeting is loaded

Now the feature is measurable.

---

# Phase 3 — System Architecture

This is the 10,000-foot view.

Questions to answer:

* What are the major components?
* How do they communicate?
* Where does AI fit?
* Where does MySQL fit?
* Where do external APIs fit?

One architecture diagram is enough.

---

# Phase 4 — Low-Level Design (Most Teams Skip This)

This is where many hackathon teams lose time.

Before coding, define:

## Database

* Tables
* Relationships
* Keys
* Indexes

## APIs

For example:

```
POST /upload

POST /extract

GET /meeting/{id}

POST /approve

GET /audit
```

## AI Contracts

Define what the LLM returns.

Example:

```
Summary

Decisions

Action Items

Confidence

Evidence
```

## State Machine

Very important.

```
Uploaded

↓

Extracted

↓

Pending Review

↓

Approved

↓

Synced

↓

Completed
```

This ensures you never violate the "zero unapproved actions" rule.

---

# Phase 5 — Implementation Plan

Only now should you think about Antigravity.

Break the work into independent modules.

Example:

```
Module 1

Database

Module 2

Transcript Parser

Module 3

AI Extraction

Module 4

Review UI

Module 5

GitHub Integration

Module 6

Audit Logs
```

Each module should compile and work independently.

---

# Phase 6 — AI-Assisted Coding

This is where Antigravity becomes powerful.

But don't ask it:

> Build the whole project.

Instead ask:

> Build Module 3 according to this API contract and database schema.

Smaller prompts produce more reliable code.

---

# Phase 7 — Validation (Much Bigger Than Testing)

Most beginners think validation equals testing.

Actually there are several layers.

## 1. Functional Validation

Does it meet the requirements?

---

## 2. Integration Validation

Does every module communicate correctly?

---

## 3. Business Validation

Does it solve the problem?

---

## 4. AI Validation

Are the extracted tasks actually correct?

---

## 5. User Validation

Can a first-time user complete the workflow?

---

## 6. Performance Validation

Can it process a meeting within the required time?

---

## 7. Safety Validation

Can any action bypass approval?

---

## 8. Regression Validation

Does fixing one feature break another?

---

# Phase 8 — Hardening

This is different from testing.

Hardening asks:

"What happens when things go wrong?"

Examples:

* Empty transcript
* Invalid file
* GitHub unavailable
* LLM timeout
* Database disconnected
* Missing owner
* Missing due date

Your system should fail gracefully.

---

# Phase 9 — Demo Engineering

This is another layer most teams ignore.

Design the demo before submission.

Prepare:

* Sample transcript
* Expected outputs
* GitHub repository ready
* Screens already opened
* Backup transcript
* Backup API key
* Offline fallback where possible

A polished demo often matters as much as polished code.

---

# One Important Layer You're Missing

You're thinking about **building**.

Also think about **maintaining**.

Ask these questions before coding:

* Can I understand this code tomorrow if I'm tired?
* Can I replace Gemini with OpenAI in one place?
* Can I add Slack without rewriting everything?
* Can I test each module independently?
* Is every module responsible for one thing?

If the answer is "yes," your architecture is modular.

---

# My Recommended Pre-Coding Deliverables

Before opening Antigravity, I would have these ready:

1. ✅ Problem statement and evaluation criteria (done).
2. ✅ MVP feature checklist.
3. ✅ System architecture diagram.
4. ✅ Database ER diagram and schema.
5. ✅ API specification.
6. ✅ Folder structure.
7. ✅ State machine for the workflow.
8. ✅ LLM input/output schemas (Pydantic models).
9. ✅ UI wireframes (even simple sketches).
10. ✅ Test plan with normal, edge, and failure cases.
11. ✅ Development order (which module to build first).
12. ✅ Demo script and acceptance checklist.

---

## My recommendation

If I were mentoring a team for this Buildathon, I would **not allow anyone to write code until these 12 artifacts exist**.

The reason is simple: once these are defined, AI IDEs like Antigravity become dramatically more effective because they receive precise architecture, contracts, and interfaces instead of vague feature requests. That reduces rework, keeps the codebase consistent, and makes debugging much easier during the 48-hour sprint.
==============================

Excellent. This is exactly how experienced software architects work. They spend time thinking first, then use AI to accelerate implementation.

We'll build this like an enterprise AI product, not just a hackathon project.

---

# Overall Roadmap (Pre-Coding Deliverables)

```
Phase 0 ✅ Problem Understanding (Completed)

Phase 1 → Requirements Engineering
Phase 2 → Success Metrics & Acceptance Criteria
Phase 3 → MVP Scope Definition
Phase 4 → System Architecture
Phase 5 → Low-Level Design
Phase 6 → Database Design
Phase 7 → API Design
Phase 8 → AI Design
Phase 9 → UI/UX Flow
Phase 10 → Development Roadmap
Phase 11 → Test Strategy
Phase 12 → Demo Strategy

↓

AI IDE (Antigravity)

↓

Implementation

↓

Validation

↓

Hardening

↓

Submission
```

We'll complete **one deliverable at a time**.

---

# Deliverable 1 — Requirements Engineering (Foundation)

This is the most important document because **everything else depends on it**.

## Objective

Convert the Buildathon PDF into **clear engineering requirements**.

Instead of reading paragraphs, engineers think in terms of functional and non-functional requirements.

---

# 1. Functional Requirements (What the system must do)

## Module A — Input Management

**FR-1**

User uploads a meeting transcript.

Supported:

* `.txt`
* `.vtt`
* `.srt`

(Source-supported requirement.) 

---

## Module B — AI Understanding

**FR-2**

System extracts:

* Executive Summary
* Decisions
* Open Questions
* Risks / Blockers
* Action Items

(Source-supported requirement.) 

---

## Module C — Action Item Intelligence

Each action item contains:

* Title
* Owner
* Due Date
* Priority
* Confidence Score

(Source-supported requirement.) 

---

## Module D — Human Review

Before any external action:

User can

* Edit
* Approve
* Reject

(Source-supported requirement.) 

---

## Module E — Tool Integration

After approval

Create GitHub Issues.

(This satisfies the requirement for at least one real tool integration.) 

---

## Module F — Duplicate Prevention

If the same meeting is uploaded again

System must

* detect duplicate
* avoid duplicate issue creation

(Source-supported idempotency requirement.) 

---

## Module G — Audit Logging

Record

* AI Extraction
* Human Edit
* Approval
* GitHub Sync

(Source-supported requirement.) 

---

# 2. Non-Functional Requirements (How the system should behave)

### Performance

* Process within Buildathon target time. 

---

### Reliability

Never lose extracted tasks.

---

### Safety

Never create GitHub Issues before approval.

This is a critical evaluation requirement. 

---

### Maintainability

Modular architecture.

---

### Scalability

Support larger transcripts without redesigning the architecture.

---

### Usability

First-time user should understand the workflow.

---

# 3. Constraints

These are fixed by the Buildathon brief.

* Individual project
* Human approval required before external actions
* At least one external integration
* Duplicate suppression
* Public GitHub repository
* Public Google Drive folder

(Source-supported.) 

---

# 4. Assumptions (Our Design Decisions)

These are **our choices**, not Buildathon requirements.

| Decision              | Reason                         |
| --------------------- | ------------------------------ |
| Streamlit             | Fast UI development            |
| FastAPI               | Clean backend separation       |
| MySQL                 | Transactional state management |
| GitHub Issues         | Simplest integration           |
| Gemini 2.5 Flash      | Fast structured extraction     |
| Transcript input only | Delivers MVP faster            |

---

# 5. Risks

Before coding, identify major risks.

| Risk                     | Mitigation                     |
| ------------------------ | ------------------------------ |
| LLM returns invalid JSON | Pydantic validation            |
| GitHub API failure       | Retry + clear error message    |
| Duplicate upload         | SHA-256 hash                   |
| Missing owner            | Mark `UNASSIGNED`              |
| Missing due date         | Leave null and flag for review |
| Invalid transcript       | Show validation error          |

---

# 6. Out of Scope (Very Important)

These are intentionally **not** part of the MVP.

* Audio transcription
* Live meeting mode
* Slack integration
* Teams integration
* Calendar integration
* Cross-meeting memory
* Meeting analytics
* Multi-language support

These remain candidates for stretch goals.

---

# Deliverable 1 Output

We now have a concise **Requirements Engineering Document**.

This document becomes the reference for:

* Architecture
* Database
* APIs
* AI prompts
* UI
* Testing

---

# Next Deliverable

We'll move to **Deliverable 2: Success Metrics & Acceptance Criteria**.

This is where we define, for **every feature**, exactly **how we will verify it works** before writing any code. It becomes the checklist we'll use during development and before the final submission.
---------
Perfect. This is one of the most important deliverables because it changes our mindset from **"building features"** to **"proving the system works."**

> **Principle:** Every requirement must have a measurable acceptance test. If it cannot be tested, it is not truly complete.

---

# Deliverable 2 — Success Metrics & Acceptance Criteria

## Goal

Before writing code, define **how each feature will be verified**.

Think of this as the **Definition of Done (DoD)** for every module.

---

# Overall Success Criteria

At the highest level, our project is successful if it:

* ✅ Satisfies all mandatory Buildathon requirements.
* ✅ Meets or exceeds the evaluation metrics where possible.
* ✅ Demonstrates a complete end-to-end workflow.
* ✅ Is reliable during the live demo.

(Source: Buildathon evaluation metrics and mandatory requirements.) 

---

# Module 1 — Transcript Upload

## Objective

Accept supported transcript files.

### Acceptance Criteria

✅ Upload `.txt`

✅ Upload `.vtt`

✅ Upload `.srt`

✅ Invalid file types rejected with a clear message.

### Test Cases

* Normal `.txt`
* Normal `.vtt`
* Normal `.srt`
* Empty file
* Unsupported extension (`.pdf`)
* Corrupted file

---

# Module 2 — Transcript Parsing

## Objective

Convert uploaded transcript into clean text.

### Acceptance Criteria

✅ Speaker labels preserved (if available).

✅ Timestamps extracted (when present).

✅ Empty transcript detected.

### Test Cases

* Speaker-labelled transcript
* Timestamped transcript
* Plain text transcript
* Missing speaker names
* Broken timestamp format

---

# Module 3 — AI Extraction

## Objective

Extract structured meeting information.

### Acceptance Criteria

Generate:

* Executive Summary
* Decisions
* Open Questions
* Risks
* Action Items

(Source-supported requirement.) 

### Test Cases

* Short meeting
* Long meeting
* No action items
* Multiple speakers
* Mixed formatting

---

# Module 4 — Action Item Quality

## Objective

Each action item should contain:

* Title
* Owner
* Due Date
* Priority
* Confidence Score

### Acceptance Criteria

No required field is missing without explanation.

If owner cannot be identified:

→ `UNASSIGNED`

If due date missing:

→ Leave blank for human review.

---

# Module 5 — Human Review

## Objective

Nothing happens automatically.

### Acceptance Criteria

User can:

* Edit
* Approve
* Reject

No GitHub Issue is created before approval.

This directly satisfies the "zero unapproved actions" requirement. 

---

# Module 6 — GitHub Integration

## Objective

Approved items become GitHub Issues.

### Acceptance Criteria

* One approved task → one GitHub Issue.
* Rejected tasks → no issue.
* Edited task → edited version is used.

### Test Cases

* Single approval
* Multiple approvals
* API failure
* Invalid token
* Repository not found

---

# Module 7 — Duplicate Prevention

## Objective

Prevent duplicate processing.

### Acceptance Criteria

Upload same transcript twice.

Expected:

* Existing meeting is reused.
* No duplicate GitHub Issues.
* User informed that the meeting already exists.

This satisfies the idempotency requirement. 

---

# Module 8 — Audit Log

## Objective

Every important event is recorded.

### Acceptance Criteria

Audit log contains events such as:

* Upload
* Extraction
* Edit
* Approval
* Rejection
* GitHub Sync

(Source-supported requirement.) 

---

# Module 9 — Performance

## Objective

Meet the Buildathon performance expectations.

### Acceptance Criteria

* Transcript processed within the expected evaluation target.
* UI remains responsive.
* User receives progress indication during processing.

(Source: evaluation metrics.) 

---

# Module 10 — Error Handling

## Objective

Fail safely and clearly.

### Acceptance Criteria

Errors produce informative messages, not crashes.

Examples:

* Invalid file
* Empty transcript
* LLM timeout
* GitHub unavailable
* Database unavailable

---

# Module 11 — Demo Readiness

## Objective

Complete the demo without manual fixes.

### Acceptance Criteria

Demo flow:

1. Upload transcript.
2. AI extraction completes.
3. Review screen appears.
4. Edit one task.
5. Reject one task.
6. Approve remaining tasks.
7. GitHub Issues created.
8. Audit log updated.
9. Re-upload same transcript.
10. Duplicate detection demonstrated.

This closely follows the suggested demo narrative while showcasing mandatory behaviors. 

---

# Acceptance Checklist (Go / No-Go)

| Area                    | Pass? |
| ----------------------- | ----- |
| Transcript upload       | ☐     |
| Parsing                 | ☐     |
| AI extraction           | ☐     |
| Structured outputs      | ☐     |
| Human review            | ☐     |
| GitHub integration      | ☐     |
| Zero unapproved actions | ☐     |
| Duplicate suppression   | ☐     |
| Audit logging           | ☐     |
| Error handling          | ☐     |
| Performance target      | ☐     |
| End-to-end demo         | ☐     |

---

# Additional Layer: Validation Pyramid

Before submission, validate the project in this order:

```text
Level 5 → Demo Validation
          Can judges follow the workflow?

Level 4 → Business Validation
          Does it solve the meeting assistant problem?

Level 3 → Integration Validation
          Do all modules work together?

Level 2 → Functional Validation
          Does each feature satisfy its requirement?

Level 1 → Unit Validation
          Does each module work independently?
```

---

# Deliverable 2 Outcome

We now have a **Definition of Done** for the project. During the Buildathon, every new feature must satisfy its corresponding acceptance criteria before being considered complete.

## Next Deliverable

The logical next step is **Deliverable 3 — MVP Scope & Feature Prioritization**.

Here we'll decide exactly **what is included in Version 1 (mandatory), Version 1.5 (polish), and Version 2 (stretch goals)**. This is the document that prevents scope creep and keeps the 48-hour Buildathon focused.
------------
Excellent. This deliverable is where many hackathon projects either succeed or fail.

Most teams ask:

> **"What features can we build?"**

Instead, we ask:

> **"What is the smallest complete product that satisfies the judges, and what is the highest ROI feature to build next?"**

This is called **Feature Prioritization**.

---

# Deliverable 3 — MVP Scope & Feature Prioritization

## Objective

Define **exactly what we will build**, **what we will postpone**, and **what we will add only if time permits**.

This document prevents **scope creep**, which is the biggest risk in a 48-hour Buildathon.

---

# Guiding Principle

Every feature should answer one question:

> **Does this directly improve our Buildathon score?**

If **Yes** → Build it.

If **No** → Postpone it.

---

# Version Strategy

Instead of one giant project, we'll think in **three product versions**.

```text
Version 1.0 (MVP)
        ↓
Version 1.5 (Production Quality)
        ↓
Version 2.0 (Stretch Goals)
```

---

# Version 1.0 — MVP (Must Build)

These are **non-negotiable** because they satisfy the mandatory requirements from the Buildathon brief. 

## Epic 1 — Meeting Ingestion

### Features

* Upload `.txt`
* Upload `.vtt`
* Upload `.srt`

**Priority:** 🔴 Critical

---

## Epic 2 — Transcript Processing

### Features

* Parse transcript
* Preserve speakers
* Preserve timestamps (if present)
* Clean transcript text

**Priority:** 🔴 Critical

---

## Epic 3 — AI Extraction

### Features

Extract:

* Executive Summary
* Decisions
* Risks
* Open Questions
* Action Items

**Priority:** 🔴 Critical

---

## Epic 4 — Action Item Intelligence

Each action item includes:

* Title
* Owner
* Due Date
* Priority
* Confidence Score
* Evidence Quote (recommended)

**Priority:** 🔴 Critical

> **Note:** The Buildathon requires owner, due date, priority, and confidence. An evidence quote is not mandatory but is a strong differentiator. 

---

## Epic 5 — Human Review

Features:

* Edit
* Approve
* Reject

Nothing executes automatically.

**Priority:** 🔴 Critical

---

## Epic 6 — GitHub Integration

Features:

* Create GitHub Issues
* Update sync status
* Handle failures gracefully

**Priority:** 🔴 Critical

---

## Epic 7 — Duplicate Prevention

Features:

* SHA-256 transcript hash
* Detect duplicate uploads
* Prevent duplicate GitHub Issues

**Priority:** 🔴 Critical

---

## Epic 8 — Audit Logs

Track:

* Upload
* Extraction
* Edit
* Approval
* GitHub Sync

**Priority:** 🔴 Critical

---

# MVP Deliverable

At this point, you have a **complete end-to-end AI Meeting Assistant** that satisfies the mandatory workflow.

---

# Version 1.5 — Production Quality (Build After MVP)

These features don't fundamentally change the product but significantly improve reliability, trust, and demo quality.

## Better AI

* Multi-pass prompting
* Better prompt engineering
* Improved structured outputs

---

## Better Validation

* Owner validation
* Date validation
* Confidence filtering

---

## Better Error Handling

* Invalid transcript
* Empty transcript
* GitHub API errors
* LLM timeout
* Database errors

---

## Better UI

* Progress indicators
* Better tables
* Status badges
* Search and filter
* Expandable evidence view

---

## Better Documentation

* Architecture diagram
* README
* API docs
* Screenshots

---

# Version 2.0 — Stretch Goals

Only if the MVP is complete and stable.

These align with the Buildathon stretch goals. 

### AI Features

* Audio upload (Whisper)
* Video upload
* Code-switched language support
* Cross-meeting memory
* Meeting health analytics
* Disagreement detection

---

### Integrations

* Slack
* Email
* Google Calendar
* Multiple integrations

---

### Intelligence

* Automated reminders
* Meeting history
* Trend analytics
* Team productivity insights

---

# Feature Prioritization Matrix

Think about every new feature using this matrix.

| Priority | Criteria                                    | Action                                  |
| -------- | ------------------------------------------- | --------------------------------------- |
| **P0**   | Mandatory requirement or demo blocker       | Build first                             |
| **P1**   | Strongly improves evaluation or reliability | Build after P0                          |
| **P2**   | Nice improvement, low risk                  | Build if time permits                   |
| **P3**   | Interesting but low evaluation impact       | Skip unless everything else is complete |

---

# Our Project Backlog

| Feature                | Priority | Version |
| ---------------------- | -------- | ------- |
| Transcript Upload      | P0       | 1.0     |
| Transcript Parser      | P0       | 1.0     |
| AI Extraction          | P0       | 1.0     |
| Human Review           | P0       | 1.0     |
| GitHub Issues          | P0       | 1.0     |
| Duplicate Detection    | P0       | 1.0     |
| Audit Logs             | P0       | 1.0     |
| Confidence Filtering   | P1       | 1.5     |
| Owner Validation       | P1       | 1.5     |
| Better UI              | P1       | 1.5     |
| Error Recovery         | P1       | 1.5     |
| README & Docs          | P1       | 1.5     |
| Audio Support          | P2       | 2.0     |
| Slack Integration      | P2       | 2.0     |
| Cross-Meeting Memory   | P2       | 2.0     |
| Meeting Analytics      | P2       | 2.0     |
| Multi-language Support | P2       | 2.0     |

---

# Stop Rules (Very Important)

These rules protect the project from becoming unstable.

### Rule 1

❌ Never start a P1 feature until **all P0 features are working together**.

### Rule 2

❌ Never start a P2 feature until **the end-to-end demo succeeds without manual fixes**.

### Rule 3

If you find a bug in a P0 feature while building a P1 or P2 feature:

➡️ Stop immediately and fix the P0 bug first.

---

# Definition of MVP Complete

Before moving to Version 1.5, every statement below must be true:

* ☐ Transcript uploads successfully.
* ☐ Transcript is parsed correctly.
* ☐ AI extracts the required meeting information.
* ☐ Action items include the required fields.
* ☐ Human can edit, approve, or reject.
* ☐ GitHub Issues are created only after approval.
* ☐ Duplicate uploads do not create duplicate issues.
* ☐ Audit logs capture all major events.
* ☐ The complete demo runs successfully from start to finish.

If all boxes are checked, the MVP is complete.

---

# Deliverable 3 Outcome

We now have a **prioritized product roadmap** that tells us:

* **What must be built first** (Version 1.0 / P0)
* **What improves quality next** (Version 1.5 / P1)
* **What can be added only if time allows** (Version 2.0 / P2)

This roadmap becomes the decision guide during the Buildathon whenever you're tempted to add a new feature.

---

## Next Deliverable

The next logical step is **Deliverable 4 — System Architecture & High-Level Design**.

This is where we'll define:

* The overall architecture (Streamlit, FastAPI, MySQL, LLM, GitHub).
* Component responsibilities.
* Data flow between components.
* Design principles and boundaries.

Once that is complete, Antigravity will have a precise blueprint to generate production-quality modules rather than disconnected pieces of code.
----------
Excellent. This is arguably the **highest ROI deliverable**. If we get the architecture right, Antigravity can generate 70–80% of the implementation consistently.

One refinement before we begin:

> **System Architecture ≠ Folder Structure**

Many beginners think architecture means drawing boxes. It doesn't.

Architecture answers:

* **What are the major components?**
* **What is each component responsible for?**
* **How do they communicate?**
* **What data flows between them?**
* **Where are the boundaries?**
* **Where is AI allowed to make decisions, and where must deterministic code take over?**

---

# Deliverable 4 — System Architecture & High-Level Design

## Objective

Design an architecture that is:

* Modular
* Maintainable
* Testable
* AI-friendly
* Production-inspired
* Buildable in 48 hours

---

# 1. System Context (10,000-foot View)

```text
                        USER
                          │
                          ▼
                 Streamlit Frontend
                          │
               HTTP REST API Calls
                          │
                          ▼
                  FastAPI Backend
                          │
 ┌───────────────┬───────────────┬────────────────┐
 │               │               │                │
 ▼               ▼               ▼                ▼
AI Service   Business Logic   MySQL DB     GitHub Service
   │               │               │                │
   ▼               ▼               ▼                ▼
Gemini       Validation      Persistent      GitHub Issues
2.5 Flash    State Mgmt       Storage        Integration
```

---

# 2. Layered Architecture

We will use a **5-layer architecture**.

```text
Presentation Layer
        │
Application Layer
        │
Domain Layer
        │
Infrastructure Layer
        │
External Services
```

---

## Layer 1 — Presentation Layer

### Responsibility

Everything the user sees.

Technology:

* Streamlit

Responsibilities:

* Upload transcript
* Display summary
* Review action items
* Edit owner/date
* Approve / Reject
* Show audit logs
* Display GitHub sync status

Never:

* Call Gemini directly
* Access MySQL directly
* Contain business logic

---

## Layer 2 — Application Layer

Technology:

* FastAPI

Responsibility:

Acts as the orchestrator.

Example endpoints:

```text
POST /upload

POST /extract

POST /approve

GET /meeting/{id}

GET /audit
```

Responsibilities:

* Receive requests
* Validate inputs
* Call services
* Return responses

Never:

* Write prompts
* Write SQL queries directly

---

## Layer 3 — Domain Layer (Heart of the System)

This is where the actual business rules live.

Services:

```text
Transcript Service

↓

Meeting Service

↓

Extraction Service

↓

Approval Service

↓

Duplicate Service

↓

Audit Service

↓

GitHub Service
```

Responsibilities:

* Business rules
* State transitions
* Validation
* Workflow orchestration

Example:

```
Pending Review

↓

Approved

↓

GitHub Sync

↓

Completed
```

This layer enforces the Buildathon rule that no external action occurs before human approval. 

---

## Layer 4 — Infrastructure Layer

Responsibilities:

* MySQL
* SQLAlchemy
* Repository classes
* File parser
* Environment variables
* Logging

Think of this as the system's plumbing.

---

## Layer 5 — External Services

External dependencies:

* Gemini API
* GitHub API

Future additions:

* Slack
* Calendar
* Email

Notice that external services are isolated, making replacements easier.

---

# 3. Component Responsibilities

| Component          | Responsibility                     |
| ------------------ | ---------------------------------- |
| Streamlit          | User interaction                   |
| FastAPI            | API gateway & orchestration        |
| Transcript Service | Parse transcript files             |
| AI Service         | Generate structured meeting data   |
| Validation Service | Validate owners, dates, confidence |
| Approval Service   | Enforce review workflow            |
| Duplicate Service  | SHA-256 idempotency                |
| GitHub Service     | Create GitHub Issues               |
| Audit Service      | Record system events               |
| MySQL              | Persistent storage                 |

Each component should have **one primary responsibility**.

---

# 4. Data Flow

The complete lifecycle:

```text
Upload Transcript
        │
        ▼
Transcript Parser
        │
        ▼
Duplicate Check
        │
   Duplicate?
    │       │
   Yes      No
    │        │
Load Existing │
Meeting       ▼
        AI Extraction
              │
              ▼
     Structured Output
              │
              ▼
      Business Validation
              │
              ▼
     Save to MySQL
              │
              ▼
     Human Review UI
              │
      Approve / Reject
              │
        Approved?
         │      │
        No     Yes
         │       │
      Update     ▼
      Status  GitHub Issues
                  │
                  ▼
            Audit Logging
```

---

# 5. State Machine

One of the most important design decisions.

```text
UPLOADED
     │
     ▼
PARSED
     │
     ▼
EXTRACTED
     │
     ▼
PENDING_REVIEW
     │
 ┌───┴────┐
 │        │
 ▼        ▼
REJECTED APPROVED
            │
            ▼
        GITHUB_SYNCED
            │
            ▼
         COMPLETED
```

Rules:

* No skipping states.
* No direct jump from `EXTRACTED` to `GITHUB_SYNCED`.
* Only `APPROVED` items may trigger external integrations.

---

# 6. AI vs Deterministic Code Boundary

This is a key architectural decision.

### AI Responsibilities

* Executive summary
* Decisions
* Risks
* Open questions
* Action item extraction
* Confidence estimation

### Deterministic Code Responsibilities

* File parsing
* SHA-256 hashing
* Duplicate detection
* Database operations
* State management
* Approval workflow
* GitHub API calls
* Audit logging
* Error handling

**Principle:** If Python can do it reliably, don't ask the LLM to do it.

---

# 7. Design Principles

Our architecture will follow these principles:

* **Single Responsibility:** Each service has one job.
* **Loose Coupling:** Services communicate through clear interfaces.
* **High Cohesion:** Related logic stays together.
* **Separation of Concerns:** UI, business logic, storage, and AI are isolated.
* **Fail Gracefully:** External service failures don't crash the application.
* **Extensibility:** New integrations (Slack, Calendar) can be added without changing the core workflow.

---

# 8. Future Extension Points

We intentionally leave room for future growth.

```text
Integrations/
├── github_service.py
├── slack_service.py
├── calendar_service.py
└── email_service.py

AI/
├── gemini_provider.py
├── openai_provider.py
└── claude_provider.py
```

This makes switching providers or adding integrations much easier.

---

# Deliverable 4 Outcome

We now have a **High-Level Architecture Blueprint** that answers:

* What components exist.
* What each component owns.
* How data flows.
* Where AI is used.
* Where deterministic logic takes over.
* How the system enforces Buildathon constraints such as human approval before external actions. 

---

# Before Moving to Deliverable 5

One additional architectural question that experienced software architects ask is:

> **What are the core domain entities of the business?**

Architecture tells us **how** the system is organized.

The next deliverable—**Low-Level Design (LLD)**—defines **what** the system manipulates in detail:

* Domain entities (Meeting, Participant, ActionItem, AuditLog, etc.)
* Database schema
* API contracts
* Pydantic models
* Class relationships
* Sequence diagrams
* Folder structure

This becomes the precise specification that Antigravity can use to generate consistent production-quality code.
-------------
Excellent. We're now entering the level where **architects think before developers code**.

One clarification first:

Many people think **Low-Level Design (LLD)** means drawing UML class diagrams.

That's only **10%** of LLD.

LLD is actually the **engineering blueprint** from which developers (or AI IDEs) can implement the system with minimal ambiguity.

---

# Deliverable 5 — Low-Level Design (LLD)

## Objective

Translate the High-Level Architecture into **precise implementation contracts**.

By the end of this deliverable, we should know:

* What are the domain entities?
* How do they relate?
* What services exist?
* What state transitions are allowed?
* What interfaces/modules will Antigravity generate?

> **Note:** We will intentionally keep the actual database schema and API details for the next deliverables (Database Design and API Design). Here we focus on the domain model and module responsibilities.

---

# 1. Domain Model (Business Entities)

The system revolves around these core entities:

```text
Meeting
│
├── Participants
├── Summary
├── Decisions
├── Risks
├── Open Questions
├── Action Items
└── Audit Logs
```

### Core Entities

| Entity           | Purpose                                          |
| ---------------- | ------------------------------------------------ |
| **Meeting**      | Root entity representing one uploaded transcript |
| **Participant**  | People identified in the meeting                 |
| **ActionItem**   | Tasks extracted by AI                            |
| **Decision**     | Decisions made during the meeting                |
| **Risk**         | Risks or blockers identified                     |
| **OpenQuestion** | Unresolved discussion points                     |
| **AuditLog**     | Immutable history of important events            |
| **GitHubSync**   | Tracks synchronization with GitHub Issues        |

---

# 2. Entity Relationships

```text
Meeting
 ├── 1 Summary
 ├── N Participants
 ├── N Decisions
 ├── N Risks
 ├── N OpenQuestions
 ├── N ActionItems
 └── N AuditLogs

ActionItem
 └── 0..1 GitHubSync
```

Meaning:

* One meeting contains many action items.
* Each action item may create one GitHub Issue.
* Audit logs are attached to the meeting.

---

# 3. Module Responsibilities

Each module should have **one clear responsibility**.

| Module             | Responsibility                          |
| ------------------ | --------------------------------------- |
| Transcript Parser  | Read and normalize transcript           |
| Duplicate Checker  | Detect previously uploaded meetings     |
| AI Extractor       | Generate structured meeting information |
| Validator          | Validate owners, dates, confidence      |
| Repository         | Read/write MySQL data                   |
| Approval Manager   | Handle review workflow                  |
| GitHub Integration | Create GitHub Issues                    |
| Audit Logger       | Record system events                    |

This follows the **Single Responsibility Principle (SRP)**.

---

# 4. State Machines

## Meeting Lifecycle

```text
UPLOADED
    ↓
PARSED
    ↓
EXTRACTED
    ↓
READY_FOR_REVIEW
    ↓
COMPLETED
```

---

## Action Item Lifecycle

```text
EXTRACTED
     ↓
PENDING_REVIEW
     ↓
APPROVED
     ↓
SYNCED
```

or

```text
EXTRACTED
     ↓
PENDING_REVIEW
     ↓
REJECTED
```

These state machines ensure no action bypasses human approval, aligning with the Buildathon requirements. 

---

# 5. Service Interaction

Instead of every module talking to every other module, keep interactions simple.

```text
Streamlit
     │
FastAPI
     │
Meeting Service
     │
 ├── Transcript Parser
 ├── Duplicate Checker
 ├── AI Extractor
 ├── Validator
 ├── Repository
 ├── Approval Manager
 ├── GitHub Service
 └── Audit Logger
```

The **Meeting Service** acts as the orchestrator.

---

# 6. Business Rules (Critical)

These are rules that **must never be violated**.

### Rule 1

A meeting cannot be processed if the upload is invalid.

---

### Rule 2

Duplicate meetings must not be processed again.

---

### Rule 3

Every extracted action item starts as:

```text
PENDING_REVIEW
```

---

### Rule 4

Only **APPROVED** action items can be synced to GitHub.

---

### Rule 5

Every important action generates an audit log entry.

---

### Rule 6

If GitHub synchronization fails:

* Keep the action item approved.
* Mark sync as failed.
* Allow retry.

---

# 7. Error Handling Strategy

Think about failures before coding.

| Failure              | Expected Behaviour           |
| -------------------- | ---------------------------- |
| Empty transcript     | Reject upload                |
| Unsupported format   | Validation error             |
| Invalid LLM response | Retry or show error          |
| GitHub API failure   | Retry later, don't lose data |
| Database unavailable | Fail gracefully              |
| Duplicate upload     | Load existing meeting        |

---

# 8. Extension Points

Design for future growth without implementing it now.

Examples:

* Additional LLM providers (OpenAI, Claude)
* Slack integration
* Calendar integration
* Email notifications
* Audio transcription

These should plug into existing interfaces rather than require major redesign.

---

# 9. LLD Checklist

Before coding, we should be able to answer:

* ✅ What are the core entities?
* ✅ How are they related?
* ✅ What modules exist?
* ✅ What is each module responsible for?
* ✅ What are the valid state transitions?
* ✅ What business rules are enforced?
* ✅ How are failures handled?
* ✅ Where can future features be added?

If the answer is "yes" to all of these, the LLD is sufficiently complete for a 48-hour Buildathon.

---

# Deliverable 5 Outcome

We now have a clear **implementation blueprint**:

* Domain model
* Entity relationships
* Module responsibilities
* State machines
* Business rules
* Error-handling philosophy
* Extension strategy

This gives Antigravity clear boundaries and responsibilities instead of vague instructions.

---

# Next Deliverable Recommendation

The next deliverable should be **Deliverable 6 — Database Design (ER Model + MySQL Schema)**.

This is where we'll define:

1. Which tables exist (and why).
2. Primary and foreign keys.
3. Relationships.
4. Normalization level.
5. Indexes.
6. State columns.
7. Audit strategy.
8. Whether to store AI outputs as normalized tables or JSON.
9. Performance considerations.

This database design will become the single source of truth for both FastAPI and the AI extraction pipeline.
------------
Excellent. This is where we stop thinking like AI engineers and start thinking like **Data Architects**.

One important correction before we begin.

Many beginners ask:

> "What tables do I need?"

Professional architects ask:

> **"What business entities need persistence, what relationships exist, what is the data grain, and what queries will the application execute?"**

The database is **not** just for storing data.

It should support:

* Business workflow
* State management
* AI outputs
* Auditability
* Performance
* Future extensibility

---

# Deliverable 6 — Database Design

## Goal

Design a **minimal but production-inspired relational database** that satisfies:

* Buildathon requirements
* Future extensibility
* Easy AI integration
* Easy Streamlit UI
* Easy FastAPI development

---

# Step 1 — Identify Persistent Business Entities

Ask a simple question:

> **"What information must still exist after the application restarts?"**

Those become tables.

For our project:

```text
Meeting
Participant
ActionItem
AuditLog
GitHubSync
```

Everything else can either be:

* Generated on demand
* Stored inside Meeting
* Computed dynamically

---

# Step 2 — Database Grain (Very Important)

One of the most overlooked concepts.

Every table must represent **one thing at one level of detail (grain).**

| Table       | Grain                              |
| ----------- | ---------------------------------- |
| Meeting     | One uploaded meeting               |
| Participant | One participant in one meeting     |
| ActionItem  | One extracted task                 |
| AuditLog    | One system event                   |
| GitHubSync  | One GitHub synchronization attempt |

Never mix grains.

Example:

❌ One row = Meeting + Action Item + Audit

Good:

✅ One row = One Action Item

---

# Step 3 — ER Model

```text
Meeting
│
├────────────┐
│            │
▼            ▼
Participant  ActionItem
                 │
        ┌────────┴────────┐
        ▼                 ▼
    GitHubSync       AuditLog
```

Relationship summary

```
Meeting

1 ---- N Participants

1 ---- N Action Items

1 ---- N Audit Logs

Action Item

1 ---- 0..1 GitHub Sync
```

---

# Step 4 — Table Design

## Meeting

Represents one uploaded transcript.

### Suggested Columns

```
meeting_id (PK)

title

meeting_date

uploaded_at

transcript_hash

transcript_text

summary

decisions

risks

open_questions

status

created_at

updated_at
```

Why store summary in Meeting?

Because there is only **one summary per meeting.**

No separate Summary table needed.

---

## Participant

```
participant_id (PK)

meeting_id (FK)

name

email

role
```

Why separate table?

Because meetings have multiple participants.

---

## ActionItem

Most important table.

```
action_item_id (PK)

meeting_id (FK)

title

description

owner

due_date

priority

confidence_score

evidence_quote

status

created_at

updated_at
```

Status values

```
PENDING_REVIEW

APPROVED

REJECTED

SYNCED
```

---

## AuditLog

```
audit_id (PK)

meeting_id (FK)

action_item_id (nullable FK)

event_type

actor

payload

created_at
```

Example

```
UPLOAD

EXTRACT

EDIT

APPROVE

REJECT

SYNC
```

---

## GitHubSync

```
sync_id (PK)

action_item_id (FK)

github_issue_number

github_issue_url

sync_status

synced_at

error_message
```

Why separate?

Future integrations become easy.

Tomorrow you add:

```
SlackSync

CalendarSync

EmailSync
```

without changing ActionItem.

---

# Step 5 — Normalization

Should we normalize everything?

No.

Hackathon strategy:

### Normalize

* Participants
* Action Items
* Audit Logs

### Keep inside Meeting

* Summary
* Decisions
* Risks
* Open Questions

Why?

Those are **single meeting-level outputs**, not repeating entities.

Creating four extra tables adds complexity with little benefit in 48 hours.

---

# Step 6 — Primary Keys

Use UUIDs or Auto Increment?

Recommendation

```
meeting_id

participant_id

action_item_id

audit_id

sync_id
```

Use **UUIDs** if comfortable; otherwise **AUTO_INCREMENT BIGINT** is perfectly acceptable for a hackathon.

---

# Step 7 — Foreign Keys

```
Participant

meeting_id

↓

Meeting


ActionItem

meeting_id

↓

Meeting


AuditLog

meeting_id

↓

Meeting


GitHubSync

action_item_id

↓

ActionItem
```

This preserves referential integrity.

---

# Step 8 — Index Strategy

We don't need many indexes.

Just the important ones.

```
Meeting

transcript_hash

meeting_date
```

```
ActionItem

meeting_id

status

owner
```

```
AuditLog

meeting_id

created_at
```

These support our expected queries efficiently.

---

# Step 9 — State Management

Don't scatter states.

Meeting State

```
UPLOADED

PARSED

EXTRACTED

READY_FOR_REVIEW

COMPLETED
```

Action Item State

```
PENDING_REVIEW

APPROVED

REJECTED

SYNCED
```

GitHub Sync State

```
NOT_SYNCED

SUCCESS

FAILED
```

Each entity owns its own lifecycle.

---

# Step 10 — Data Flow into Database

```text
Upload Transcript
        │
        ▼
Meeting Table

        │
        ▼
AI Extraction

        │
 ┌──────┴────────┐
 ▼               ▼

Meeting      ActionItem

                    │
                    ▼

               AuditLog

                    │
                    ▼

              GitHubSync
```

---

# Step 11 — Why This Database is Strong

Compared to a beginner design:

❌ One huge table with 30–40 columns mixing meetings, participants, tasks, and logs.

Our design:

* Clear entity separation
* Proper relationships
* Easy querying
* Simple joins
* Extensible
* Supports audit trails
* Supports future integrations
* Minimal enough for a 48-hour Buildathon

---

# Architecture Decision Record (ADR)

Before coding, record a few key decisions. This helps avoid second-guessing during implementation.

| Decision            | Choice              | Reason                                     |
| ------------------- | ------------------- | ------------------------------------------ |
| Database            | MySQL               | Familiar, transactional, relational        |
| Schema style        | Hybrid normalized   | Balance between simplicity and scalability |
| Meeting outputs     | Stored in `Meeting` | One summary/decision set per meeting       |
| Action items        | Separate table      | Core business entity with lifecycle        |
| Audit logs          | Separate table      | Traceability and debugging                 |
| Integrations        | Separate sync table | Easy to add Slack/Calendar later           |
| Duplicate detection | `transcript_hash`   | Enforces idempotency                       |

---

# Final Database Blueprint

```text
Meeting
│
├── meeting_id
├── transcript_hash
├── transcript_text
├── summary
├── decisions
├── risks
├── open_questions
└── status
      │
      ├──────────────┐
      ▼              ▼
Participant      ActionItem
                     │
                     ├──────────┐
                     ▼          ▼
                GitHubSync  AuditLog
```

---

## Deliverable 6 Outcome

We now have a database design that is:

* ✅ Normalized where it matters.
* ✅ Simple enough to implement within 48 hours.
* ✅ Aligned with the Buildathon workflow.
* ✅ Ready for SQLAlchemy models and MySQL schema generation.
* ✅ Extensible for future integrations without major redesign.

---

# Before Deliverable 7

One more architectural question experienced backend engineers ask before writing APIs is:

> **"What are the contracts between the frontend, backend, AI, and database?"**

That's exactly what **Deliverable 7 — API Design & Interface Contracts** will answer. We'll define every endpoint, request/response model, validation rule, status code, and the interaction sequence so Antigravity can generate consistent FastAPI endpoints with minimal manual changes.
---------------
Excellent. We have now reached the point where most backend engineers start coding. However, experienced architects do **API Design first** because **APIs are contracts**.

Think of it this way:

* **Database** = How data is stored.
* **API** = How data moves.
* **Frontend** = How data is presented.
* **AI** = How data is generated.

If the API contract is stable, the frontend, backend, and AI can be developed independently.

---

# Deliverable 7 — API Design & Interface Contracts

## Objective

Define a clear contract between:

```text
Streamlit UI
      │
      ▼
 FastAPI APIs
      │
      ▼
 Business Services
      │
      ▼
 Database + AI + GitHub
```

Each API should do **one business operation**.

---

# Step 1 — Identify Business Use Cases

Instead of designing APIs first, identify **user actions**.

Our user can:

1. Upload transcript
2. View extracted meeting
3. Review action items
4. Edit action item
5. Approve action item
6. Reject action item
7. Sync approved items
8. View audit logs
9. Check duplicate meeting

Each action becomes one API.

---

# Step 2 — REST API List

## Meeting APIs

| Method | Endpoint                 | Purpose                   |
| ------ | ------------------------ | ------------------------- |
| POST   | `/meetings/upload`       | Upload transcript         |
| GET    | `/meetings/{meeting_id}` | Get complete meeting      |
| GET    | `/meetings`              | List meetings             |
| DELETE | `/meetings/{meeting_id}` | Delete meeting (optional) |

---

## Action Item APIs

| Method | Endpoint                         | Purpose              |
| ------ | -------------------------------- | -------------------- |
| GET    | `/meetings/{meeting_id}/actions` | Get all action items |
| PATCH  | `/actions/{action_id}`           | Edit action item     |
| POST   | `/actions/{action_id}/approve`   | Approve              |
| POST   | `/actions/{action_id}/reject`    | Reject               |

---

## GitHub APIs

| Method | Endpoint                      | Purpose             |
| ------ | ----------------------------- | ------------------- |
| POST   | `/meetings/{meeting_id}/sync` | Sync approved tasks |
| GET    | `/sync/{action_id}`           | Get sync status     |

---

## Audit APIs

| Method | Endpoint                       | Purpose         |
| ------ | ------------------------------ | --------------- |
| GET    | `/meetings/{meeting_id}/audit` | View audit logs |

---

# Step 3 — API Workflow

```text
Upload Transcript
        │
POST /meetings/upload
        │
Meeting Created
        │
GET /meetings/{id}
        │
User Reviews
        │
PATCH /actions/{id}
        │
Approve
        │
POST /actions/{id}/approve
        │
Sync
        │
POST /meetings/{id}/sync
        │
GitHub Issue Created
        │
Audit Updated
```

---

# Step 4 — Request/Response Contracts

This is where many teams fail.

Every API should define:

* Input
* Validation
* Output
* Errors

---

## API 1 — Upload Transcript

### Request

```text
Multipart Form

File
Meeting Date (optional)
Project Name (optional)
```

### Validation

* File exists
* Supported extension
* File size
* Duplicate check

### Success Response

```text
meeting_id
status = READY_FOR_REVIEW
summary
action_items_count
duplicate = false
```

### Error

```text
400 Invalid File

409 Duplicate Transcript

500 Internal Error
```

---

## API 2 — Get Meeting

Returns

```text
Meeting

Summary

Decisions

Risks

Questions

Participants

Action Items
```

Simple read-only endpoint.

---

## API 3 — Edit Action Item

Editable fields only.

Allowed:

```text
Owner

Due Date

Priority

Title
```

Not editable:

* Confidence
* AI evidence
* Meeting ID

Reason:

Maintain audit integrity.

---

## API 4 — Approve

Input

```text
action_id
```

Logic

```text
PENDING

↓

APPROVED
```

Audit log generated.

No GitHub call yet.

---

## API 5 — Reject

```text
PENDING

↓

REJECTED
```

Audit log generated.

---

## API 6 — Sync

Input

```text
meeting_id
```

Logic

For every

APPROVED

↓

Create GitHub Issue

↓

Update status

↓

Audit

If GitHub fails

↓

FAILED_SYNC

---

# Step 5 — Validation Rules

Every API has validation.

| API     | Validation                 |
| ------- | -------------------------- |
| Upload  | File type, size, duplicate |
| Edit    | Valid owner/date/priority  |
| Approve | Must be PENDING            |
| Reject  | Must be PENDING            |
| Sync    | Must be APPROVED           |
| Audit   | Meeting exists             |

---

# Step 6 — Status Codes

| Status | Meaning                               |
| ------ | ------------------------------------- |
| 200    | Success                               |
| 201    | Resource created                      |
| 400    | Bad request                           |
| 404    | Resource not found                    |
| 409    | Duplicate or invalid state transition |
| 422    | Validation failed                     |
| 500    | Internal server error                 |

Avoid returning `200` for everything.

---

# Step 7 — API Security (Hackathon Scope)

We intentionally keep this simple.

* No login system.
* Mock current user (e.g., `Admin`).
* GitHub token stored in `.env`.
* Validate inputs to prevent crashes.

This keeps the focus on the AI workflow rather than authentication.

---

# Step 8 — Idempotency Rules

A critical Buildathon requirement.

| Operation | Idempotent? | Strategy                   |
| --------- | ----------- | -------------------------- |
| Upload    | Yes         | `transcript_hash` check    |
| Approve   | Yes         | Ignore if already approved |
| Reject    | Yes         | Ignore if already rejected |
| Sync      | Yes         | Skip already synced items  |

This prevents duplicate processing and duplicate GitHub Issues.

---

# Step 9 — API Versioning

Even in a hackathon, think ahead.

```text
/api/v1/meetings

/api/v1/actions

/api/v1/sync
```

Future versions can evolve without breaking the frontend.

---

# Step 10 — Sequence Diagram

```text
User
 │
 │ Upload Transcript
 ▼
Streamlit
 │
 ▼
FastAPI
 │
 ▼
Transcript Parser
 │
 ▼
Duplicate Checker
 │
 ├── Duplicate? ──► Return Existing Meeting
 │
 ▼
LLM Extraction
 │
 ▼
Validation
 │
 ▼
MySQL
 │
 ▼
Return Meeting
 │
 ▼
User Reviews
 │
Approve
 │
 ▼
FastAPI
 │
 ▼
GitHub Service
 │
 ▼
GitHub Issue
 │
 ▼
Audit Log
```

---

# API Design Principles

Every endpoint should follow these principles:

* **Single Responsibility:** One endpoint, one business action.
* **Stateless:** Every request contains all the information needed.
* **Idempotent where appropriate:** Repeating the same safe action should not create duplicate effects.
* **Explicit State Transitions:** APIs enforce the workflow (`PENDING → APPROVED → SYNCED`).
* **Clear Errors:** Return meaningful status codes and messages.

---

# Deliverable 7 Outcome

We now have a complete **API Contract** that defines:

* Business operations
* REST endpoints
* Request and response structures
* Validation rules
* State transitions
* Error handling
* Idempotency strategy
* Interaction sequence

This becomes the contract between **Streamlit**, **FastAPI**, and the backend services.

---

# Before Deliverable 8 — One Architectural Refinement

We now have:

* ✅ Requirements
* ✅ Success metrics
* ✅ MVP scope
* ✅ System architecture
* ✅ Low-level design
* ✅ Database design
* ✅ API contracts

The next missing piece is the **AI Architecture**, which is different from the software architecture.

Experienced AI engineers ask questions such as:

* How many LLM calls should we make?
* What should each prompt do?
* Which tasks should be deterministic Python versus AI reasoning?
* How do we validate AI output before saving it?
* How do we reduce hallucinations?
* How do we measure extraction quality?
* How do we retry or recover from malformed outputs?

So the next deliverable should be **Deliverable 8 — AI System Design & Prompt Engineering Architecture**. This will define the entire AI pipeline before Antigravity generates any AI-related code, ensuring the LLM is treated as a controlled component of the system rather than a black box.
-----------
Excellent. This is the deliverable that differentiates an **AI application** from a normal software application.

One important correction before we start.

Many developers think:

> **AI = Call LLM → Get Response → Save Response**

That's a beginner architecture.

Professional AI systems treat the LLM as **one component in a deterministic pipeline**, not as the entire application.

Think of the AI as an **employee**, not the **CEO**.

---

# Deliverable 8 — AI System Design & Prompt Engineering Architecture

## Objective

Design an AI pipeline that is:

* Reliable
* Deterministic where possible
* Measurable
* Easy to debug
* Easy to improve
* Low latency
* Resistant to hallucinations

---

# AI Architecture Philosophy

Our system has **two brains**.

```text
           Human
             │
             ▼
     Business Workflow
             │
             ▼
 ┌──────────────────────────┐
 │ Deterministic Python Code│
 └──────────────────────────┘
             │
      Needs Reasoning?
      │            │
     No           Yes
      │            │
      ▼            ▼
Python Logic    LLM Reasoning
      │            │
      └──────┬─────┘
             ▼
      Validation Layer
             │
             ▼
        Save to MySQL
```

**Golden Rule**

> Use AI only where reasoning is required.

Everything else should be Python.

---

# Step 1 — AI Responsibility Matrix

Let's decide what AI should and shouldn't do.

| Task                   | AI                                | Python |
| ---------------------- | --------------------------------- | ------ |
| Read transcript        | ❌                                 | ✅      |
| Parse VTT/SRT          | ❌                                 | ✅      |
| SHA-256 Hash           | ❌                                 | ✅      |
| Duplicate detection    | ❌                                 | ✅      |
| Executive summary      | ✅                                 | ❌      |
| Meeting decisions      | ✅                                 | ❌      |
| Risks                  | ✅                                 | ❌      |
| Open questions         | ✅                                 | ❌      |
| Action item extraction | ✅                                 | ❌      |
| Confidence estimation  | ✅                                 | ❌      |
| Owner validation       | ⚠️ AI suggests → Python validates |        |
| Date normalization     | ⚠️ AI extracts → Python resolves  |        |
| Save to DB             | ❌                                 | ✅      |
| GitHub API             | ❌                                 | ✅      |
| Audit logs             | ❌                                 | ✅      |

**Key Principle:** AI proposes; deterministic code verifies and executes.

---

# Step 2 — AI Pipeline

Instead of one giant prompt, use a staged pipeline.

```text
Transcript
      │
      ▼
Cleaning
      │
      ▼
LLM Extraction
      │
      ▼
Structured JSON
      │
      ▼
Validation
      │
      ▼
Business Rules
      │
      ▼
Database
```

Each stage has one responsibility.

---

# Step 3 — Single vs Multi-Pass Prompting

Many beginners ask the model to do everything in one prompt.

Instead, compare:

### Option A (One Prompt)

```text
Transcript
↓

Summary
Decisions
Questions
Risks
Tasks
Owners
Dates
Priority
Confidence
Evidence
```

Pros:

* One API call.

Cons:

* Larger prompt.
* Harder to debug.
* One failure affects everything.

---

### Option B (Multi-Pass)

```text
Transcript

↓

Pass 1

Summary
Decisions
Risks
Questions

↓

Pass 2

Action Items

↓

Validation
```

Pros:

* Easier debugging.
* Better accuracy for action items.
* Easier prompt tuning.

For this Buildathon, **2 passes** provide a good balance.

---

# Step 4 — Prompt Architecture

Every prompt should have a consistent structure.

```text
SYSTEM
↓

ROLE

↓

TASK

↓

RULES

↓

INPUT

↓

OUTPUT SCHEMA

↓

EXAMPLES (optional)
```

Avoid vague prompts like "Summarize this meeting."

---

# Step 5 — Structured Outputs

Never ask for free-form text when you expect structured data.

Define schemas such as:

## Meeting Extraction

```text
Summary

Decisions

Risks

Open Questions
```

## Action Item

```text
Title

Owner

Due Date

Priority

Confidence

Evidence
```

The LLM returns structured JSON, which Python validates before storing.

---

# Step 6 — AI Validation Layer

Treat AI output as **untrusted input**.

Validation pipeline:

```text
LLM Output
     │
     ▼
JSON Valid?
     │
     ▼
Schema Valid?
     │
     ▼
Business Rules Valid?
     │
     ▼
Database Save
```

Checks include:

* Required fields present.
* Confidence score within range.
* Due date format valid.
* Owner exists or becomes `UNASSIGNED`.
* Priority is valid.

---

# Step 7 — Hallucination Guardrails

Reduce hallucinations with explicit rules.

Examples:

* Do not invent owners.
* Do not invent due dates.
* If uncertain, return `UNKNOWN` or `UNASSIGNED`.
* Only extract information supported by the transcript.
* Include evidence quotes for each action item when possible.

This is especially valuable during judge review.

---

# Step 8 — Confidence Strategy

Confidence is **not** a decision-maker.

Use it as a review signal.

```text
0.90–1.00
High confidence

0.70–0.89
Needs quick review

Below 0.70
Highlight for manual verification
```

Never auto-reject based only on confidence.

---

# Step 9 — Error Recovery

AI systems fail differently from normal software.

Possible failures:

| Failure          | Strategy                                  |
| ---------------- | ----------------------------------------- |
| Timeout          | Retry once                                |
| Invalid JSON     | Retry with stricter prompt                |
| Missing fields   | Validation error                          |
| Empty extraction | Ask user to review transcript             |
| API unavailable  | Friendly error, preserve uploaded meeting |

---

# Step 10 — AI Observability

Don't treat the LLM as a black box.

Track:

* Prompt version.
* Model used.
* Response time.
* Token usage (if available).
* Success/failure.
* Validation result.

These logs help debug AI behavior and improve prompts later.

---

# Step 11 — AI State Machine

```text
TRANSCRIPT_RECEIVED
        │
        ▼
AI_PROCESSING
        │
        ▼
AI_OUTPUT_RECEIVED
        │
        ▼
VALIDATED
        │
 ┌──────┴──────┐
 │             │
 ▼             ▼
FAILED     READY_FOR_REVIEW
```

This separates AI processing from business workflow.

---

# Step 12 — Prompt Versioning

Treat prompts like code.

Example:

```text
v1.0
Basic extraction

↓

v1.1
Improved owner extraction

↓

v1.2
Better evidence selection
```

If quality drops, you know which prompt changed.

---

# Step 13 — AI Quality Metrics

Measure the AI, not just the application.

| Metric                     | Target              |
| -------------------------- | ------------------- |
| Summary completeness       | High                |
| Action item recall         | ≥ Buildathon target |
| Action item precision      | ≥ Buildathon target |
| Owner accuracy             | ≥ Buildathon target |
| Relative date resolution   | ≥ Buildathon target |
| Structured output validity | 100%                |
| Invalid JSON rate          | Near 0%             |

These align with the evaluation metrics from the Buildathon brief.

---

# Step 14 — AI Design Principles

These become our engineering rules.

1. **AI reasons; Python controls.**
2. **Never trust raw LLM output.**
3. **Validate before storing.**
4. **Keep prompts focused on one responsibility.**
5. **Prefer structured outputs over free text.**
6. **Use deterministic code wherever possible.**
7. **Design prompts as versioned assets.**
8. **Log AI behavior for debugging.**

---

# AI Blueprint

```text
Transcript Upload
        │
        ▼
Transcript Cleaning (Python)
        │
        ▼
LLM Pass 1
Summary + Decisions + Risks + Questions
        │
        ▼
LLM Pass 2
Action Items
        │
        ▼
Schema Validation
        │
        ▼
Business Validation
        │
        ▼
MySQL Storage
        │
        ▼
Human Review
        │
        ▼
GitHub Sync
```

---

# Deliverable 8 Outcome

We now have an **AI architecture** that is:

* ✅ Modular rather than one giant prompt.
* ✅ Deterministic where possible.
* ✅ Measurable through quality metrics.
* ✅ Validated before persistence.
* ✅ Easy to debug and improve.
* ✅ Aligned with the Buildathon evaluation criteria.

---

# My Recommendation Before Coding

At this point, we've completed the **highest-value architectural work**:

* ✅ Requirements Engineering
* ✅ Success Metrics & Acceptance Criteria
* ✅ MVP Scope & Prioritization
* ✅ System Architecture
* ✅ Low-Level Design
* ✅ Database Design
* ✅ API Contracts
* ✅ AI System Design

The next deliverable should not be code yet.

I recommend **Deliverable 9 — Repository Structure, Development Workflow & Implementation Blueprint**.

This bridges architecture to Antigravity by defining:

* Final folder structure.
* File-by-file responsibilities.
* Development order (which module to generate first).
* AI IDE prompting strategy.
* Git workflow and checkpoints.
* Testing workflow.
* Build order to minimize integration risk.

This document becomes the execution playbook for the 48-hour Buildathon.
--------
Excellent. This is the **bridge** between architecture and implementation.

After this deliverable, you should be able to open **Google Antigravity** and start generating production-ready code module by module with almost no ambiguity.

> **Think like a Construction Engineer**
>
> * Deliverables 1–8 = **Architectural Blueprint**
> * Deliverable 9 = **Construction Plan**
> * Deliverable 10+ = **Actual Building**

---

# Deliverable 9 — Repository Structure, Development Workflow & Implementation Blueprint

## Objective

Create a **single execution blueprint** that tells:

* What files exist
* Why they exist
* Which order to build them
* How modules communicate
* How Antigravity should generate code
* How integration happens
* How testing happens

---

# 1. Final Repository Structure

I recommend a **Domain-Driven + Layered Architecture**.

```
TechBharat_Buildathon_MudamanchuGuruNagesh/

│
├── frontend/
│
├── backend/
│
├── database/
│
├── docs/
│
├── samples/
│
├── tests/
│
├── docker/
│
├── .env
│
├── docker-compose.yml
│
├── README.md
│
└── requirements.txt
```

This is clean, scalable, and understandable.

---

# 2. Backend Structure

This is where most logic lives.

```
backend/

app/

├── api/

├── core/

├── database/

├── schemas/

├── models/

├── repositories/

├── services/

├── integrations/

├── utils/

├── prompts/

└── main.py
```

---

## api/

Purpose

HTTP endpoints only.

```
upload.py

meeting.py

action.py

sync.py

audit.py
```

Contains

* Request handling
* Response
* Validation

Should NOT contain

* SQL
* Prompt engineering
* Business logic

---

## core/

Contains

```
config.py

security.py

constants.py
```

Everything globally shared.

---

## database/

Contains

```
connection.py

session.py

base.py
```

Only database infrastructure.

---

## models/

SQLAlchemy Models

```
meeting.py

participant.py

action_item.py

audit.py

github_sync.py
```

---

## schemas/

Pydantic Models

```
meeting_schema.py

action_schema.py

upload_schema.py

audit_schema.py
```

Purpose

Validation

Serialization

API Contracts

---

## repositories/

Purpose

Only SQL operations.

Example

```
meeting_repository.py

action_repository.py

audit_repository.py
```

Repositories never call AI.

---

## services/

This is the brain.

```
meeting_service.py

transcript_service.py

duplicate_service.py

extraction_service.py

validation_service.py

approval_service.py

audit_service.py
```

Business rules live here.

---

## integrations/

External systems only.

```
github_service.py

llm_service.py
```

Future

```
slack_service.py

calendar_service.py
```

---

## prompts/

Very important.

```
summary_prompt.md

action_prompt.md

system_prompt.md
```

Never hardcode prompts inside Python.

---

## utils/

Helper functions.

```
hashing.py

date_parser.py

file_parser.py

logger.py
```

---

# 3. Frontend Structure

```
frontend/

app.py

pages/

components/

utils/
```

Pages

```
Upload

Review

Audit

Settings
```

Components

```
Action Table

Summary Card

Audit Timeline

Status Badge
```

---

# 4. Development Order (Critical)

This is **not** the same as folder order.

Build in dependency order.

```
Database

↓

Models

↓

Repositories

↓

Utilities

↓

Services

↓

API

↓

Frontend

↓

Testing
```

Never start with the frontend.

---

# 5. Antigravity Development Strategy

Don't ask:

> Build my entire project.

Instead:

```
Generate SQLAlchemy model for Meeting.

```

↓

Review

↓

Commit

↓

Next

```
Generate repository.

```

↓

Review

↓

Commit

```
Generate service.

```

↓

Review

↓

Commit

Small iterations reduce debugging.

---

# 6. Git Workflow

```
main

↓

feature/database

↓

feature/backend

↓

feature/frontend

↓

feature/github

↓

feature/testing
```

Even if working alone, logical commits make rollback easier.

---

# 7. Build Order

## Phase 1

Infrastructure

* MySQL
* FastAPI
* Streamlit
* Docker

Checkpoint

Can all containers start?

---

## Phase 2

Database

Checkpoint

Can create tables?

---

## Phase 3

Upload

Checkpoint

Can upload transcript?

---

## Phase 4

AI

Checkpoint

Can generate structured JSON?

---

## Phase 5

Store Data

Checkpoint

Meeting saved?

---

## Phase 6

Review UI

Checkpoint

Can edit?

Approve?

Reject?

---

## Phase 7

GitHub

Checkpoint

Issue created?

---

## Phase 8

Audit

Checkpoint

Events stored?

---

## Phase 9

Testing

Checkpoint

Everything passes?

---

# 8. Testing Strategy

Every feature follows the same lifecycle.

```
Generate

↓

Review

↓

Run

↓

Debug

↓

Retest

↓

Commit
```

Never generate five modules before testing.

---

# 9. AI IDE Prompt Strategy

Think in layers.

Instead of:

```
Build upload feature.
```

Use:

```
Context

Architecture

Requirements

Constraints

Output format

Acceptance criteria

Generate only this module.
```

This dramatically improves AI quality.

---

# 10. Definition of Done (Per Module)

Every generated module must satisfy:

* Compiles
* Passes linting (if used)
* Unit test passes
* No duplicated code
* Matches architecture
* Uses proper logging
* Uses proper error handling
* Uses type hints
* Has docstrings
* Integrates with previous module

Only then move to the next module.

---

# 11. Iteration Loop

This is how you'll work for the entire Buildathon.

```text
Architecture

↓

Generate Module

↓

Review Code

↓

Run

↓

Debug

↓

Validate

↓

Commit

↓

Next Module
```

Never skip validation.

---

# 12. 48-Hour Execution Blueprint

## Sprint 1 (Foundation)

* Repository
* Docker
* Database
* Models
* API skeleton

**Goal:** Everything starts successfully.

---

## Sprint 2 (Core AI)

* Upload
* Parser
* LLM
* Structured extraction

**Goal:** AI extracts meeting information correctly.

---

## Sprint 3 (Workflow)

* Database persistence
* Review UI
* Approve/Reject

**Goal:** Human approval workflow functions correctly.

---

## Sprint 4 (Integration)

* GitHub Issues
* Audit logs
* Duplicate detection

**Goal:** End-to-end workflow is complete.

---

## Sprint 5 (Hardening)

* Error handling
* Edge cases
* UI polish
* Documentation
* Demo rehearsal

**Goal:** Reliable submission and presentation.

---

# 13. Master Dependency Graph

```text
Requirements
      │
Architecture
      │
Database
      │
Models
      │
Repositories
      │
Utilities
      │
Services
      │
AI Integration
      │
API
      │
Frontend
      │
Testing
      │
Documentation
      │
Demo
```

This ensures every layer builds on a stable foundation.

---

# Additional Layer You're Missing (Very Important)

Everything we've designed so far focuses on **building the software**.

An experienced software architect also prepares **execution governance** before coding.

That includes:

* **Architecture Decision Records (ADRs):** Record major technical decisions (e.g., "Why GitHub Issues instead of Slack?"). This prevents second-guessing during the sprint.
* **Definition of Ready (DoR):** Before generating a module with Antigravity, verify inputs are complete: requirements, API contract, schema, acceptance criteria, and dependencies.
* **Definition of Done (DoD):** We defined this per module—don't merge code until it meets it.
* **Risk Register:** Keep a simple list of the top risks (LLM JSON errors, GitHub API failures, Docker issues) with mitigation steps.
* **Technical Debt List:** If you intentionally skip something (e.g., authentication), document it instead of forgetting it.
* **Time Budget:** Reserve the **last 4–6 hours exclusively** for testing, bug fixing, documentation, and demo rehearsal. Avoid adding new features during this period.

These governance artifacts don't take long to create, but they dramatically reduce chaos during a fast-paced hackathon.

---

# Deliverable 9 Outcome

At this stage, you have a complete **execution playbook**:

* ✅ Architecture
* ✅ Domain model
* ✅ Database design
* ✅ API contracts
* ✅ AI architecture
* ✅ Repository structure
* ✅ Module responsibilities
* ✅ Development workflow
* ✅ Antigravity prompting strategy
* ✅ Testing workflow
* ✅ Sprint execution plan

This is enough to start implementation with confidence.

## My Recommendation Before Writing Code

Before opening Antigravity, I would create **one final planning deliverable**:

**Deliverable 10 — Development Task Board & Module-by-Module Execution Plan**.

Instead of thinking in terms of files, it breaks the project into **30–50 small, independently testable tasks**, each with:

* Objective
* Inputs
* Outputs
* Dependencies
* Acceptance criteria
* Estimated time
* Suggested Antigravity prompt

This becomes your minute-by-minute execution guide during the Buildathon and minimizes context switching.
--------
Yes. I actually agree with you.

Those are not optional—they are **critical pre-coding deliverables**. If we skip them, we'll likely end up redesigning parts of the project while coding, which wastes valuable Buildathon time.

I would slightly reorganize the remaining deliverables into this sequence:

---

# ✅ Deliverable 10 — UI/UX Flow & User Journey

**Purpose:** Design the product before implementing Streamlit.

Questions it answers:

* What does the user see first?
* How many screens/pages exist?
* What information is shown on each page?
* What actions are available?
* How does the user move between screens?
* What states (loading, success, error, empty) need handling?
* How do we make the 3-minute demo visually compelling?

### Outputs

* User Journey Map
* Screen Flow
* Wireframes (low fidelity)
* Component hierarchy
* Navigation flow
* UX states (Loading, Empty, Error, Success)
* Streamlit page layout
* Demo-oriented UI decisions

---

# ✅ Deliverable 11 — Testing, Validation & Demo Strategy

**Purpose:** Ensure the project works reliably and is easy to demonstrate.

This combines three areas that are often forgotten.

## A. Testing Strategy

* Unit tests
* Integration tests
* End-to-end workflow tests
* Manual testing checklist
* Regression testing
* Acceptance testing

---

## B. Edge Case Library

Examples:

* Empty transcript
* Duplicate transcript
* Corrupted `.vtt`
* Missing speaker names
* No action items
* Ambiguous owner
* Relative dates
* GitHub API failure
* Invalid API key
* Large transcript
* LLM timeout
* Invalid JSON from LLM

---

## C. Demo Strategy

Probably the **highest ROI** document.

We'll script the entire judge demo.

Example:

```
Open App

↓

Upload Sample Meeting

↓

AI Processing

↓

Review Summary

↓

Edit Owner

↓

Reject Wrong Task

↓

Approve Correct Task

↓

GitHub Issue Created

↓

Audit Log Updated

↓

Re-upload Same File

↓

Duplicate Detection Works

↓

Done
```

No surprises.

No thinking during the demo.

Just execute.

---

# ✅ Deliverable 12 — Development Task Board & Module-by-Module Execution Plan

Only after all design work is complete.

This becomes our implementation guide.

Each task will contain:

* Objective
* Dependencies
* Inputs
* Outputs
* Files to create
* Acceptance criteria
* Estimated time
* Antigravity prompt
* Test cases
* Commit message

Essentially, it's a Jira board tailored for your 48-hour Buildathon.

---

# One More Layer I'd Add (Often Missed)

Since you're using an AI IDE like Antigravity, I'd include a small but powerful artifact within Deliverable 12:

## **AI Prompt Playbook**

Instead of improvising prompts, prepare reusable prompt templates such as:

* Generate SQLAlchemy model
* Generate FastAPI endpoint
* Generate repository layer
* Generate service layer
* Generate Streamlit component
* Refactor code
* Write unit tests
* Review code for architecture compliance
* Find bugs
* Optimize performance
* Generate documentation

This keeps AI output consistent across the entire project and reduces time lost rewriting prompts.

---

## Final Recommended Deliverable Order

| Deliverable | Purpose                                             |
| ----------- | --------------------------------------------------- |
| ✅ 1         | Project Vision & Requirements                       |
| ✅ 2         | Success Metrics & Acceptance Criteria               |
| ✅ 3         | MVP Scope & Feature Prioritization                  |
| ✅ 4         | System Architecture & High-Level Design             |
| ✅ 5         | Low-Level Design (LLD)                              |
| ✅ 6         | Database Design                                     |
| ✅ 7         | API Design & Interface Contracts                    |
| ✅ 8         | AI System Design & Prompt Engineering               |
| ✅ 9         | Repository Structure & Implementation Blueprint     |
| **10**      | **UI/UX Flow & User Journey**                       |
| **11**      | **Testing, Validation & Demo Strategy**             |
| **12**      | **Development Task Board & AI IDE Prompt Playbook** |

I would not add any more planning documents after these. At that point, you'll have an architecture package comparable to what many engineering teams prepare before implementation, and the remaining effort should shift almost entirely to building, testing, and polishing the application rather than creating more documentation.
---------
Excellent. This is one of the highest ROI deliverables because **judges don't experience your database or APIs—they experience your UI**.

For a Buildathon, your UI has **two jobs**:

1. **Enable the workflow** (functional UX).
2. **Tell a compelling story in 3 minutes** (demo UX).

So we won't design the UI like a typical CRUD application. We'll design it like a **guided AI workflow**.

---

# Deliverable 10 — UI/UX Flow & User Journey

## Objective

Design a UI that is:

* Intuitive
* Minimal
* Demo-friendly
* Transparent (shows AI reasoning)
* Supports Human-in-the-Loop approval
* Makes judges immediately understand the value

---

# 1. User Persona

We should optimize for **one primary user**, not everyone.

### Primary User

```text
Product Manager / Team Lead
```

Responsibilities:

* Upload meeting transcript
* Review AI output
* Correct mistakes
* Approve tasks
* Sync to GitHub
* Verify audit trail

Design for this workflow only.

---

# 2. User Journey

```text
Landing
    │
    ▼
Upload Transcript
    │
    ▼
AI Processing
    │
    ▼
Meeting Overview
    │
    ▼
Review Action Items
    │
    ▼
Edit (Optional)
    │
    ▼
Approve / Reject
    │
    ▼
Sync GitHub
    │
    ▼
Audit Timeline
```

Notice:

No unnecessary navigation.

Just one continuous business workflow.

---

# 3. Screen Architecture

Instead of many pages, use **5 logical screens**.

```
Dashboard

↓

Upload

↓

Meeting Review

↓

GitHub Sync

↓

Audit
```

---

## Screen 1 — Dashboard

Purpose

Quick overview.

Show:

```
Recent Meetings

Total Tasks

Pending Review

Approved

Synced

Rejected
```

KPIs on top.

Recent meetings below.

Buttons:

```
Upload Meeting
```

---

## Screen 2 — Upload

Purpose

Start workflow.

Components

```
Transcript Upload

Meeting Date

Project Name

Upload Button
```

After upload

Show

```
Processing...

Parsing...

AI Extraction...

Validation...

Completed
```

This progress feedback reassures judges that the system is working.

---

## Screen 3 — Meeting Review (Core Screen)

This is where judges will spend most of their time.

Layout

```
------------------------------------------------
Meeting Summary
------------------------------------------------

Participants

Decisions

Risks

Questions

-----------------------------------------------

Action Items Table
```

---

### Action Item Table

Each row

```
□

Task

Owner

Due Date

Priority

Confidence

Evidence

Status

Actions
```

Actions

```
Edit

Approve

Reject
```

This is the heart of the application.

---

## Evidence Drawer

Click

```
Evidence
```

Opens

```
Transcript Quote

Timestamp

Reason
```

Example

```
[14:22]

John:

"I'll finish database migration by Friday."
```

This builds trust in the AI output.

---

## Edit Dialog

Editable

```
Owner

Due Date

Priority

Task Title
```

Read-only

```
Confidence

Evidence

AI Reason
```

This preserves AI traceability.

---

## Screen 4 — GitHub Sync

Purpose

Show synchronization status.

Display

```
Task

GitHub Issue

Issue URL

Status

Retry
```

Success indicator

```
✓ Synced
```

Failure

```
Retry
```

No hidden operations.

Everything visible.

---

## Screen 5 — Audit Timeline

Display

```
09:21 Uploaded

09:22 AI Extracted

09:23 Edited

09:24 Approved

09:25 Synced
```

Judges love transparency.

---

# 4. Navigation Flow

Simple left sidebar.

```
Dashboard

Upload

Meeting Review

Audit

Settings
```

Avoid 10+ menu items.

---

# 5. Component Hierarchy

```
App

├── Sidebar

├── Header

├── KPI Cards

├── Upload Panel

├── Summary Card

├── Participants Card

├── Decisions Card

├── Action Table

├── Edit Dialog

├── Evidence Drawer

├── Audit Timeline

└── Footer
```

Small reusable components simplify development.

---

# 6. UI States

Every screen needs these states.

### Empty

```
No meetings uploaded yet.
```

---

### Loading

```
Uploading...

Extracting...

Analyzing...
```

---

### Success

```
✓ Extraction Completed
```

---

### Error

```
GitHub Sync Failed

Retry
```

---

### Duplicate

```
Meeting Already Exists

Open Existing Meeting
```

This directly demonstrates idempotency.

---

# 7. Color Semantics

Use colors consistently.

```
Green

Approved

Synced

-----------------

Yellow

Pending

Review

-----------------

Red

Rejected

Failed

-----------------

Blue

AI Information
```

Avoid using color alone—also include icons or labels for accessibility.

---

# 8. Demo-Optimized UX

Design for the judges' 3-minute experience.

```
Open Dashboard

↓

Upload Sample

↓

Watch AI Processing

↓

Summary Appears

↓

Open Action Items

↓

Show Evidence

↓

Edit Owner

↓

Approve

↓

GitHub Issue Created

↓

Audit Timeline

↓

Duplicate Upload

↓

Duplicate Detected

Finish
```

Every step showcases a key evaluation criterion.

---

# 9. UX Principles

Every screen should answer one question.

| Screen    | User Question                    |
| --------- | -------------------------------- |
| Dashboard | What meetings exist?             |
| Upload    | How do I start?                  |
| Review    | Did the AI understand correctly? |
| Sync      | Were tasks created successfully? |
| Audit     | Can I trust what happened?       |

If a screen tries to answer multiple unrelated questions, simplify it.

---

# 10. Wireframe (Low Fidelity)

```text
---------------------------------------------------------
 Agentic AI Meeting Assistant
---------------------------------------------------------

Sidebar

Dashboard

Upload

Review

Audit

---------------------------------------------------------

Meeting Summary

Participants

Decisions

---------------------------------------------------------

Action Items

---------------------------------------------------------

Task | Owner | Due | Priority | Status | Actions

---------------------------------------------------------

Approve

Reject

Edit

Evidence
```

This wireframe is intentionally simple, allowing Streamlit to implement it quickly.

---

# 11. Micro-Interactions

Small touches improve the experience:

* Progress bar during AI processing.
* Toast notifications for successful approvals.
* Confirmation dialog before syncing to GitHub.
* Expandable evidence panel.
* Status badges that update immediately after actions.

These require little effort but make the app feel polished.

---

# 12. UI Design Principles

1. **One primary action per screen.**
2. **Show AI confidence and evidence, not just results.**
3. **Keep the approval workflow obvious.**
4. **Make state changes immediately visible.**
5. **Optimize for a smooth demo, not feature quantity.**

---

# Deliverable 10 Outcome

We now have a UI that is:

* ✅ Workflow-first.
* ✅ Human-in-the-loop.
* ✅ Transparent.
* ✅ Easy to implement in Streamlit.
* ✅ Optimized for Buildathon judging.

---

# One Enhancement I Recommend

To make the UI feel more like an **AI agent** rather than a traditional CRUD dashboard, add an **AI Processing Timeline** immediately after upload:

```text
Upload Complete        ✓
Transcript Parsed      ✓
Duplicate Check        ✓
Summary Generated      ✓
Action Items Extracted ✓
Validation Complete    ✓
Ready for Review       ✓
```

This serves two purposes:

1. It makes the AI pipeline visible and understandable to judges.
2. It demonstrates that your system follows a controlled, multi-stage process rather than simply calling an LLM and displaying the output.

This small addition can significantly improve the perceived sophistication of your solution without adding much implementation complexity.
-------
Excellent. This is the **most underestimated deliverable** in hackathons.

Most participants spend **90% building** and **10% testing**.

High-performing teams usually do closer to:

* **60% Building**
* **30% Testing & Hardening**
* **10% Demo & Documentation**

Because judges don't evaluate *how much code you wrote*; they evaluate *whether it works reliably*.

---

# Deliverable 11 — Testing, Validation & Demo Strategy

## Objective

Guarantee that our application is:

* Correct
* Reliable
* Robust
* Repeatable
* Demo-ready

Our philosophy:

```text
Build
   ↓
Validate
   ↓
Fix
   ↓
Retest
   ↓
Repeat
```

Testing is continuous, not the final step.

---

# Layer 1 — Testing Pyramid

We'll use a simplified testing pyramid suitable for a 48-hour Buildathon.

```text
                    Demo Validation
                         ▲
                  End-to-End Testing
                         ▲
               Integration Testing
                         ▲
                  Unit Testing
```

---

# Layer 2 — Unit Testing

Test one module in isolation.

| Module            | Test                                   |
| ----------------- | -------------------------------------- |
| Transcript Parser | Reads `.txt`, `.vtt`, `.srt` correctly |
| Duplicate Checker | Detects same SHA-256 hash              |
| Date Resolver     | Resolves "next Friday" correctly       |
| Validator         | Rejects invalid owner/date             |
| GitHub Service    | Mock API success/failure               |
| Repository        | CRUD operations                        |
| Audit Logger      | Correct log creation                   |

Goal:

> Every module works independently.

---

# Layer 3 — Integration Testing

Verify modules work together.

Examples:

### Test 1

```text
Upload

↓

Parser

↓

LLM

↓

Database
```

Expected:

Meeting saved.

---

### Test 2

```text
Approve

↓

GitHub

↓

Audit
```

Expected:

Issue created.

Audit updated.

---

### Test 3

```text
Duplicate Upload

↓

Hash

↓

Existing Meeting Returned
```

Expected:

No duplicate extraction.

---

# Layer 4 — End-to-End Testing

Test the entire business workflow.

```text
Upload

↓

AI Processing

↓

Review

↓

Edit

↓

Approve

↓

GitHub Sync

↓

Audit

↓

Duplicate Upload
```

This is exactly how judges will evaluate the project.

---

# Layer 5 — Validation Strategy

We validate four different things.

## A. Input Validation

Examples:

* Empty file
* Unsupported extension
* Oversized file
* Corrupted transcript
* Blank transcript

Expected:

Reject with clear message.

---

## B. AI Validation

Check:

* Valid JSON
* Required fields
* Confidence present
* Evidence present
* Summary exists

If invalid:

Retry once or report an error without crashing.

---

## C. Business Validation

Examples:

* Due date valid
* Owner assigned or `UNASSIGNED`
* Status transitions valid
* No duplicate GitHub sync

---

## D. Database Validation

Verify:

* Foreign keys
* Constraints
* Duplicate prevention
* Audit records
* Transaction rollback on failure

---

# Layer 6 — Edge Case Library

This is your hidden advantage during judging.

## Transcript Cases

| Case                  | Expected                |
| --------------------- | ----------------------- |
| Empty file            | Reject                  |
| Very large transcript | Process successfully    |
| Missing speakers      | AI handles gracefully   |
| No action items       | Empty review            |
| Only summary          | Summary only            |
| Duplicate upload      | Existing meeting loaded |

---

## AI Cases

| Case               | Expected             |
| ------------------ | -------------------- |
| Invalid JSON       | Retry                |
| Hallucinated owner | `UNASSIGNED`         |
| Missing due date   | `UNKNOWN`            |
| Low confidence     | Highlight for review |
| LLM timeout        | Friendly error       |

---

## GitHub Cases

| Case            | Expected                |
| --------------- | ----------------------- |
| Invalid PAT     | Sync fails safely       |
| Rate limit      | Retry later             |
| Duplicate sync  | Skip                    |
| Network failure | Preserve approval state |

---

## Database Cases

| Case               | Expected          |
| ------------------ | ----------------- |
| Duplicate meeting  | Prevent insertion |
| Missing FK         | Reject            |
| Connection failure | Graceful error    |

---

# Layer 7 — Acceptance Checklist

Before submission, every feature must satisfy:

| Feature                | Pass? |
| ---------------------- | ----- |
| Upload transcript      | ✅     |
| Duplicate detection    | ✅     |
| AI extraction          | ✅     |
| Summary generation     | ✅     |
| Action item extraction | ✅     |
| Edit task              | ✅     |
| Approve                | ✅     |
| Reject                 | ✅     |
| GitHub sync            | ✅     |
| Audit log              | ✅     |
| Evidence display       | ✅     |

Nothing ships unless all boxes are checked.

---

# Layer 8 — Performance Validation

The Buildathon specifies processing within the required time budget.

Measure:

* Upload time
* Parsing time
* LLM response time
* Database write time
* GitHub sync time
* Total processing time

If the total exceeds the target, optimize before adding features.

---

# Layer 9 — Demo Strategy

This is the **story**, not just the software.

## Opening (15–20 sec)

> "This is an Agentic AI Meeting Assistant that extracts meeting outcomes, keeps humans in control, prevents duplicate processing, and creates GitHub issues only after explicit approval."

---

## Demo Flow

```text
Dashboard

↓

Upload transcript

↓

AI processing timeline

↓

Meeting summary

↓

Action items

↓

Evidence

↓

Edit owner

↓

Approve

↓

GitHub issue

↓

Audit timeline

↓

Duplicate upload

↓

Duplicate detected

↓

Finish
```

Every step maps directly to evaluation criteria.

---

# Layer 10 — Demo Dataset

Prepare **four transcript files**.

| File                    | Purpose                       |
| ----------------------- | ----------------------------- |
| `meeting_simple.txt`    | Happy path                    |
| `meeting_ambiguous.txt` | Unknown owner                 |
| `meeting_duplicate.txt` | Duplicate detection           |
| `meeting_edge_case.txt` | Missing dates/no action items |

Never rely on random inputs during the live demo.

---

# Layer 11 — Failure Recovery Plan

If something fails during judging:

| Failure            | Backup Plan                                 |
| ------------------ | ------------------------------------------- |
| GitHub unavailable | Show approved tasks and logged sync failure |
| LLM timeout        | Use a pre-processed sample meeting          |
| Database issue     | Restore from prepared local database        |
| Internet issue     | Run everything locally via Docker           |

The judges generally value graceful failure handling more than crashes.

---

# Layer 12 — Demo Checklist

Before presenting:

* Docker containers running
* `.env` configured
* GitHub PAT verified
* Sample transcripts available
* Database reset to clean state
* Browser tabs prepared
* Logs cleared
* README updated
* Latest GitHub push completed

---

# Layer 13 — Evaluation Mapping

Map your demo directly to the Buildathon scoring.

| Evaluation Area         | Demo Evidence                           |
| ----------------------- | --------------------------------------- |
| AI Extraction           | Summary + action items                  |
| Human-in-the-loop       | Edit, approve, reject                   |
| Zero unapproved actions | GitHub sync only after approval         |
| Idempotency             | Duplicate upload detection              |
| Explainability          | Evidence quotes                         |
| Reliability             | Audit timeline                          |
| Integration             | GitHub Issues                           |
| Engineering             | Modular architecture and clean workflow |

This ensures every scoring criterion is visibly demonstrated.

---

# Layer 14 — Bug Severity Matrix

Prioritize fixes intelligently.

| Severity | Action                                                             |
| -------- | ------------------------------------------------------------------ |
| Critical | Fix immediately (crashes, data loss, unauthorized GitHub actions)  |
| High     | Fix before submission (incorrect extraction, broken approval flow) |
| Medium   | Fix if time permits (minor UI issues, formatting)                  |
| Low      | Document as future improvement (animations, cosmetic polish)       |

Don't spend an hour polishing UI while a critical workflow bug remains.

---

# Layer 15 — Go/No-Go Criteria

Before submission, ask these questions:

* ✅ Can a meeting be uploaded?
* ✅ Does duplicate detection work?
* ✅ Does AI return structured output?
* ✅ Can users edit AI results?
* ✅ Can users approve/reject tasks?
* ✅ Are GitHub issues created only after approval?
* ✅ Is every action logged?
* ✅ Can the full workflow be demonstrated without manual fixes?

If every answer is **Yes**, you're ready to submit.

---

# Deliverable 11 Outcome

You now have:

* ✅ Unit testing plan
* ✅ Integration testing plan
* ✅ End-to-end testing strategy
* ✅ Validation framework
* ✅ Edge case library
* ✅ Performance validation
* ✅ Acceptance checklist
* ✅ Demo script
* ✅ Failure recovery plan
* ✅ Evaluation mapping
* ✅ Bug prioritization
* ✅ Submission readiness criteria

---

# One Final Recommendation Before Deliverable 12

At this point, your planning is complete. **Do not create more design documents.**

The final deliverable should become your **execution engine**:

> **Deliverable 12 — Development Task Board, Module-by-Module Execution Plan & Antigravity Prompt Playbook**

This should break the project into **small 15–45 minute tasks**, each with:

* Clear objective
* Dependencies
* Files to create or modify
* Acceptance criteria
* Test cases
* Git commit suggestion
* Ready-to-use Antigravity prompt

That document will let you execute the Buildathon systematically instead of deciding what to do next every few minutes.
-------
Excellent. This is the **last planning deliverable**.

After this, **planning stops** and **implementation begins**.

This document becomes your **48-hour execution operating system**. Every task should be small enough that you can complete it in **15–45 minutes**, verify it, commit it, and move on.

---

# Deliverable 12 — Development Task Board, Module-by-Module Execution Plan & Antigravity Prompt Playbook

## Execution Philosophy

Every task follows the same lifecycle.

```text
PLAN
   ↓
Generate (Antigravity)
   ↓
Review
   ↓
Run
   ↓
Debug
   ↓
Test
   ↓
Commit
   ↓
Next Task
```

Never generate more than **one module** before testing.

---

# Sprint 0 — Project Foundation (1–2 Hours)

## Task 0.1 — Repository Setup

**Objective**

Create project skeleton.

Files

```
README.md
docker-compose.yml
.env.example
.gitignore
```

Acceptance

* Repository created
* Folder structure matches architecture

Commit

```
chore: initialize project structure
```

---

## Task 0.2 — Docker Setup

Objective

Containers start successfully.

Acceptance

```
FastAPI ✔

MySQL ✔

Streamlit ✔
```

Commit

```
feat: docker infrastructure
```

---

## Task 0.3 — Environment Configuration

Setup

```
MySQL

Gemini API

GitHub PAT

Application Config
```

Acceptance

Application loads config correctly.

---

# Sprint 1 — Database Layer

## Task 1.1

Generate MySQL schema.

Acceptance

Tables created successfully.

---

## Task 1.2

Generate SQLAlchemy models.

Acceptance

Models match schema.

---

## Task 1.3

Database connection.

Acceptance

CRUD test passes.

---

## Task 1.4

Repositories.

Acceptance

```
Create

Read

Update

Delete
```

working.

---

# Sprint 2 — Utilities

## Task 2.1

Transcript parser.

Acceptance

Reads

```
txt

vtt

srt
```

---

## Task 2.2

SHA256 duplicate checker.

Acceptance

Same file

↓

Same hash

↓

Duplicate detected.

---

## Task 2.3

Date resolver.

Acceptance

```
Next Friday

Tomorrow

End of month
```

resolved correctly.

---

# Sprint 3 — AI Layer

## Task 3.1

LLM service.

Acceptance

Returns structured JSON.

---

## Task 3.2

Summary prompt.

Acceptance

Produces

* Summary
* Decisions
* Risks
* Questions

---

## Task 3.3

Action extraction prompt.

Acceptance

Returns

* Task
* Owner
* Due Date
* Confidence
* Evidence

---

## Task 3.4

Validation service.

Acceptance

Invalid outputs rejected.

---

# Sprint 4 — Backend APIs

Generate APIs one by one.

```
Upload

Meeting

Action

Approve

Reject

Sync

Audit
```

Acceptance

Swagger works.

API tests pass.

---

# Sprint 5 — Streamlit UI

## Dashboard

Acceptance

Shows meetings.

---

## Upload Page

Acceptance

Upload works.

---

## Review Page

Acceptance

Summary visible.

Action table editable.

---

## Audit Page

Acceptance

Timeline visible.

---

# Sprint 6 — Workflow

Now integrate everything.

```
Upload

↓

Extract

↓

Store

↓

Review

↓

Approve

↓

GitHub

↓

Audit
```

Acceptance

Entire workflow works.

---

# Sprint 7 — GitHub Integration

Acceptance

Approved task

↓

GitHub Issue

↓

Stored

↓

Audit

---

# Sprint 8 — Hardening

Test

* Duplicate upload
* Invalid file
* Invalid JSON
* GitHub failure
* LLM timeout

Acceptance

Graceful failures.

---

# Sprint 9 — Documentation

Generate

README

Architecture

Installation

Demo

Known limitations

---

# Sprint 10 — Demo Preparation

Practice.

Time every step.

```
Upload

↓

Review

↓

Approve

↓

GitHub

↓

Audit

↓

Duplicate
```

Should finish in

**<3 minutes**

---

# Antigravity Prompt Playbook

This is where most people waste time.

Don't repeatedly explain your project.

Create reusable prompts.

---

## Prompt Template 1

Generate SQLAlchemy Model

```
Context:
You are working on an enterprise FastAPI + MySQL project.

Task:
Generate only the SQLAlchemy model for Meeting.

Constraints:
- SQLAlchemy 2.0
- Type hints
- Relationships
- No business logic
- Follow repository architecture

Output:
Only production-ready code.
```

---

## Prompt Template 2

Generate Repository

```
Generate repository layer for Meeting.

Requirements

CRUD

Error handling

Logging

SQLAlchemy session

No business logic.
```

---

## Prompt Template 3

Generate Service

```
Generate MeetingService.

Responsibilities

Validation

Duplicate checking

Repository calls

Audit logging

No FastAPI code.
```

---

## Prompt Template 4

Generate API

```
Generate FastAPI endpoint.

Requirements

Validation

Response models

HTTP status codes

Dependency injection

No database logic.
```

---

## Prompt Template 5

Generate Streamlit UI

```
Generate Review page.

Needs

Editable table

Approve

Reject

Evidence drawer

Status badges

No backend logic.
```

---

## Prompt Template 6

Generate Tests

```
Write pytest unit tests.

Cover

Success

Failure

Edge cases

Mock external APIs.
```

---

## Prompt Template 7

Code Review

```
Review this module.

Check

Architecture

SOLID

Security

Performance

Readability

Bug risks

Return improvements only.
```

---

## Prompt Template 8

Refactor

```
Refactor without changing behaviour.

Improve

Naming

Complexity

Maintainability

Type hints

Documentation.
```

---

## Prompt Template 9

Bug Hunt

```
Analyze this module.

Find

Race conditions

Duplicate logic

Memory leaks

Exception handling

Edge cases.
```

---

## Prompt Template 10

Performance Review

```
Analyze performance.

Suggest

Caching

Query optimization

Prompt optimization

Database indexing

Latency improvements.
```

---

# Git Commit Strategy

Don't commit "final changes".

Use meaningful commits.

```
feat: transcript upload

feat: duplicate detection

feat: AI extraction

feat: review workflow

feat: GitHub integration

feat: audit logging

test: add integration tests

docs: update architecture

fix: resolve duplicate sync bug

refactor: simplify extraction service
```

---

# Final Go-Live Checklist

Before submission:

* ✅ All Docker containers start.
* ✅ `.env` configured.
* ✅ Database migrations/schema work.
* ✅ Upload supported file types.
* ✅ Duplicate detection works.
* ✅ AI returns structured output.
* ✅ Validation layer catches bad outputs.
* ✅ Review UI functions.
* ✅ Approve/Reject workflow complete.
* ✅ GitHub Issues created only after approval.
* ✅ Audit logs recorded.
* ✅ Edge cases tested.
* ✅ README complete.
* ✅ Demo rehearsed at least three times.
* ✅ Final GitHub push completed.

---

# What We Have Built

You now have a complete engineering package:

1. ✅ Vision & Requirements
2. ✅ Success Metrics
3. ✅ MVP Scope
4. ✅ System Architecture
5. ✅ Low-Level Design
6. ✅ Database Design
7. ✅ API Contracts
8. ✅ AI Architecture
9. ✅ Repository & Implementation Blueprint
10. ✅ UI/UX Flow
11. ✅ Testing, Validation & Demo Strategy
12. ✅ Development Task Board & Antigravity Prompt Playbook

---

## One Final Recommendation

Don't let Antigravity become the "developer" while you become only the "prompt writer."

Treat Antigravity like a **junior engineer**:

* **You** decide the architecture.
* **You** review every generated module.
* **You** integrate components.
* **You** test edge cases.
* **You** own the final quality.

That's the mindset that consistently produces strong hackathon projects and is exactly what interviewers and judges look for when they assess engineering ability.
----