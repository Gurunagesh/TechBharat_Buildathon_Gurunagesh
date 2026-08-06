"""
main.py
───────
FastAPI application entrypoint.

Registers:
- CORS middleware
- All API routers
- /api/health endpoint
- Startup event (DB connection check)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import check_db_connection

logger = get_logger(__name__)


# ── Lifespan (startup / shutdown) ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    # ── Startup ──────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info(f"  {settings.app_title} v{settings.app_version}")
    logger.info("=" * 60)

    if check_db_connection():
        logger.info("[DB] Database connection: OK")
    else:
        logger.warning("[DB] Database connection: FAILED — will retry on first request")

    if not settings.gemini_api_key:
        logger.warning("[CONFIG] GEMINI_API_KEY is not set!")
    if not settings.github_token:
        logger.warning("[CONFIG] GITHUB_TOKEN is not set — GitHub sync will be disabled")

    yield

    # ── Shutdown ─────────────────────────────────────────────────
    logger.info("Application shutting down.")


# ── FastAPI App ───────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=(
        "Agentic AI Meeting Assistant — TechBharat Cohort #2 Buildathon (Use Case B). "
        "Extracts action items from meeting transcripts with human approval workflow."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────────
# Allows Streamlit (port 8501) to call FastAPI (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ──────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
def health_check():
    """
    Health check endpoint.
    Returns service status and database connectivity.
    Used by Docker Compose healthcheck and monitoring.
    """
    db_ok = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.app_version,
        "database": "connected" if db_ok else "unreachable",
        "gemini_configured": bool(settings.gemini_api_key),
        "github_configured": bool(settings.github_token),
        "github_enabled": settings.enable_github,
    }


# ── Routers (added Sprint by Sprint) ─────────────────────────────
# Sprint 6 will add:
# from app.api import meetings, actions, sync, audit
# app.include_router(meetings.router, prefix="/api", tags=["Meetings"])
# app.include_router(actions.router, prefix="/api", tags=["Actions"])
# app.include_router(sync.router, prefix="/api", tags=["Sync"])
# app.include_router(audit.router, prefix="/api", tags=["Audit"])
