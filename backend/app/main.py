"""
main.py
───────
FastAPI Application Entrypoint.

Registers:
- Versioned API Routers (/api/v1/meetings, /api/v1/actions, /api/v1/meetings/{id}/sync, /api/v1/meetings/{id}/audit)
- Global Exception Handlers (mapping domain errors to ResponseEnvelope.fail())
- CORS Middleware
- /api/health and /api/v1/health endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import check_db_connection
from app.api.exception_handlers import register_exception_handlers
from app.api.meetings import router as meetings_router
from app.api.actions import router as actions_router
from app.api.sync import router as sync_router
from app.api.audit import router as audit_router
from app.schemas.common import ResponseEnvelope, HealthResponse

logger = get_logger(__name__)


# ── Lifespan Lifecycle ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    logger.info("=" * 60)
    logger.info(f"  {settings.app_title} v{settings.app_version}")
    logger.info("=" * 60)

    if check_db_connection():
        logger.info("[DB] Database connection: OK")
        try:
            from app.core.database import Base, engine
            # Import models to ensure they register on Base.metadata
            from app.models import models
            Base.metadata.create_all(bind=engine)
            logger.info("[DB] Schema tables verified/created successfully.")
        except Exception as e:
            logger.error(f"[DB] Error creating schema tables: {e}")
    else:
        logger.warning("[DB] Database connection: FAILED — schema tables not verified")

    if not settings.gemini_api_key:
        logger.warning("[CONFIG] GEMINI_API_KEY is not set!")
    if not settings.github_token:
        logger.warning("[CONFIG] GITHUB_TOKEN is not set — GitHub sync will use mock mode")

    yield

    logger.info("Application shutting down.")


# ── FastAPI App Instance ──────────────────────────────────────────
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=(
        "Agentic AI Meeting Assistant — TechBharat Cohort #2 Buildathon (Use Case B). "
        "Extracts meeting intelligence with strict human-in-the-loop review before GitHub sync."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Register Global Exception Handlers ────────────────────────────
register_exception_handlers(app)

# ── CORS Middleware ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Versioned Routers (/api/v1/...) ──────────────────────
app.include_router(meetings_router, prefix="/api")
app.include_router(actions_router, prefix="/api")
app.include_router(sync_router, prefix="/api")
app.include_router(audit_router, prefix="/api")


# ── Root Welcome Endpoint ─────────────────────────────────────────
@app.get("/", tags=["System"], summary="Root Endpoint")
def root():
    """Welcome endpoint providing service metadata and links."""
    return {
        "name": settings.app_title,
        "version": settings.app_version,
        "status": "online",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# ── Health Check Endpoints ────────────────────────────────────────
@app.get(
    "/api/health",
    response_model=ResponseEnvelope[HealthResponse],
    tags=["System"],
    summary="Health Check",
)
@app.get(
    "/api/v1/health",
    response_model=ResponseEnvelope[HealthResponse],
    tags=["System"],
    summary="Health Check (v1)",
)
def health_check():
    """Returns service health status and database connectivity."""
    db_ok = check_db_connection()
    health_data = HealthResponse(
        status="healthy" if db_ok else "degraded",
        version=settings.app_version,
        database="connected" if db_ok else "unreachable",
        gemini_configured=bool(settings.gemini_api_key),
        github_configured=bool(settings.github_token),
        github_enabled=settings.enable_github,
    )
    return ResponseEnvelope.ok(data=health_data, message="System health check.")
