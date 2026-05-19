"""
Configuration — loads all settings from .env using pydantic BaseSettings.
Single source of truth for the entire application.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Groq (LLM)
    GROQ_API_KEY: str = ""

    # Qdrant (Vector DB)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "astrobot"

    # Server
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
