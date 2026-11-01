"""
core/database.py
────────────────
SQLAlchemy engine, session factory, and declarative base.

Usage in services:
    from app.core.database import get_db
    # Then use as FastAPI dependency: db: Session = Depends(get_db)

Usage for model definitions:
    from app.core.database import Base
    class Meeting(Base): ...
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Connect Args (SSL for TiDB Cloud / Aiven) ─────────────────────
connect_args = {}
if settings.is_ssl_required:
    ssl_args = {
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    }
    try:
        import certifi
        ssl_args["ssl_ca"] = certifi.where()
    except Exception as exc:
        logger.warning(f"[DB] Could not load certifi CA bundle: {exc}")
    connect_args.update(ssl_args)
    logger.info(f"[DB] SSL/TLS enabled for cloud database ({settings.mysql_host}:{settings.mysql_port})")

# ── Engine ────────────────────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,       # Reconnect automatically on stale connections
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,        # Recycle connections every hour
    echo=False,               # Set True temporarily for SQL debugging
)

# ── Session Factory ───────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Declarative Base (all models inherit from this) ───────────────
Base = declarative_base()


# ── FastAPI Dependency ────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Yields a database session and ensures it is closed after use.

    FastAPI usage:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Health Check Helper ───────────────────────────────────────────
def check_db_connection() -> bool:
    """Return True if the database is reachable, False otherwise."""
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"[DB_ERROR] Database health check failed: {exc}")
        return False
