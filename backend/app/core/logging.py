"""
core/logging.py
───────────────
Centralized structured logger.

Every module gets a logger via:
    from app.core.logging import get_logger
    logger = get_logger(__name__)

DO NOT use print() anywhere in the codebase.
"""

import logging
import sys
from typing import Optional


# ── Log Event Constants (use these in log messages for searchability) ─
class LogEvent:
    """Named log event types — prevents typos and aids log filtering."""
    UPLOAD = "UPLOAD"
    PARSE = "PARSE"
    DUPLICATE_DETECTED = "DUPLICATE_DETECTED"
    EXTRACT = "EXTRACT"
    VALIDATE = "VALIDATE"
    RESOLVE = "RESOLVE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    EDIT = "EDIT"
    SYNC = "SYNC"
    GITHUB_SUCCESS = "GITHUB_SUCCESS"
    GITHUB_FAILURE = "GITHUB_FAILURE"
    LLM_RETRY = "LLM_RETRY"
    LLM_FALLBACK = "LLM_FALLBACK"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    DB_ERROR = "DB_ERROR"
    WORKFLOW_VIOLATION = "WORKFLOW_VIOLATION"


def _build_formatter() -> logging.Formatter:
    """Create a structured log formatter."""
    fmt = "[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    return logging.Formatter(fmt=fmt, datefmt=datefmt)


def _configure_root_logger() -> None:
    """Configure the root logger once at import time."""
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. uvicorn already set one up)
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_build_formatter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)


_configure_root_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a named logger.

    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info(f"[{LogEvent.UPLOAD}] meeting_id={meeting_id} file={filename}")
    """
    return logging.getLogger(name or "meeting_assistant")
