"""Application settings loaded from environment variables.

This module centralizes configuration for the FastAPI chatbot, LangGraph
workflow, and Azure OpenAI access. It relies on python-dotenv so local
`.env` files are honored automatically in development.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Ensure values from .env land in os.environ for downstream libraries
load_dotenv()


class Settings(BaseModel):
    """Typed view over all runtime configuration values."""

    AZURE_API_KEY: str | None = Field(default=None)
    AZURE_API_BASE: str | None = Field(default=None)
    AZURE_API_VERSION: str = Field(default="2024-02-15-preview")
    AZURE_MODEL: str = Field(default="azure/gpt-4o-mini")
    
    # Aliases for embeddings (maps to AZURE_API_KEY and AZURE_API_BASE)
    AZURE_OPENAI_KEY: str | None = Field(default=None)
    AZURE_OPENAI_ENDPOINT: str | None = Field(default=None)

    LLM_TEMPERATURE: float = Field(default=0.2)
    LLM_VERBOSE: bool = Field(default=False)

    JWT_SECRET: str = Field(default="your-super-secret-key")
    JWT_ALGORITHM: str = Field(default="HS256")

    UPLOAD_STORAGE_DIR: str = Field(
        default="docs/uploads",
        description="Directory where uploaded policy/reference documents are stored",
    )


    class Config:
        frozen = True


@lru_cache(maxsize=1)
def _build_settings() -> Settings:
    """Load settings from environment with sensible defaults."""

    data: dict[str, str] = {}
    for field_name in Settings.model_fields.keys():
        value = os.getenv(field_name)
        if value is not None:
            data[field_name] = value
    
    # Map AZURE_API_KEY -> AZURE_OPENAI_KEY if not explicitly set
    if "AZURE_OPENAI_KEY" not in data and "AZURE_API_KEY" in data:
        data["AZURE_OPENAI_KEY"] = data["AZURE_API_KEY"]
    
    # Map AZURE_API_BASE -> AZURE_OPENAI_ENDPOINT if not explicitly set
    if "AZURE_OPENAI_ENDPOINT" not in data and "AZURE_API_BASE" in data:
        data["AZURE_OPENAI_ENDPOINT"] = data["AZURE_API_BASE"]
    
    return Settings(**data)


settings = _build_settings()

__all__ = ["settings", "Settings"]
