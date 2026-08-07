"""
core/config.py
──────────────
Single source of truth for all application configuration.

Every module imports settings from here.
NEVER hardcode values in any other module.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── MySQL ─────────────────────────────────────────────────────
    mysql_host: str = Field(default="db", description="MySQL host (Docker service name)")
    mysql_port: int = Field(default=3306)
    mysql_database: str = Field(default="meeting_assistant")
    mysql_user: str = Field(default="meeting_user")
    mysql_password: str = Field(default="meeting_password")
    mysql_root_password: str = Field(default="rootpassword")

    @property
    def database_url(self) -> str:
        """SQLAlchemy connection string."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    # ── Google Gemini (Primary LLM) ───────────────────────────────
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-1.5-flash")

    # ── Grok / xAI (Fallback LLM) ────────────────────────────────
    grok_api_key: str = Field(default="")
    grok_model: str = Field(default="grok-beta")
    grok_base_url: str = Field(default="https://api.x.ai/v1")
    enable_grok_fallback: bool = Field(default=True)

    # ── GitHub Integration ────────────────────────────────────────
    github_token: str = Field(default="", description="GitHub PAT with repo scope")
    github_repo: str = Field(default="", description="owner/repo format")
    enable_github: bool = Field(default=True)

    # ── Application ───────────────────────────────────────────────
    mock_llm: bool = Field(default=True, description="Enable mock LLM responses for demo/buildathon stability")
    confidence_threshold: float = Field(default=0.70, ge=0.0, le=1.0)
    max_upload_size_mb: int = Field(default=10)
    allowed_extensions: str = Field(default=".txt,.vtt,.srt")

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Return extensions as a list, e.g. ['.txt', '.vtt', '.srt']"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]

    # ── LLM Retry Policy ─────────────────────────────────────────
    llm_max_retries: int = Field(default=2, ge=1, le=5)
    llm_retry_delay_seconds: int = Field(default=2, ge=0)

    # ── FastAPI ───────────────────────────────────────────────────
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)
    app_title: str = Field(default="Agentic AI Meeting Assistant")
    app_version: str = Field(default="1.0.0")


# ── Singleton instance ───────────────────────────────────────────
# All modules import this:  from app.core.config import settings
settings = Settings()
