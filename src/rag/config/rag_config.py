"""RAG Configuration - Centralized settings for RAG system."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Ensure environment variables are loaded
load_dotenv()


class RAGSettings(BaseModel):
    """Configuration for RAG system including embeddings, Milvus, and LLM."""

    # Google Gemini Configuration
    GOOGLE_API_KEY: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    EMBED_MODEL: str = Field(default="gemini-embedding-001")
    EMBED_DIM: int = Field(default=3072)
    CHAT_MODEL: str = Field(default="gemini-2.5-flash")

    # Milvus Cloud (Zilliz) Configuration
    MILVUS_URI: str = Field(
        default_factory=lambda: os.getenv(
            "MILVUS_URI"
            
        )
    )
    MILVUS_TOKEN: str = Field(
        default_factory=lambda: os.getenv(
            "MILVUS_TOKEN"
        )
    )
    COLLECTION_NAME: str = Field(default="travel_indent_gemini_3072")
    TEXT_FIELD_NAME: str = Field(default="text", description="Milvus field storing chunk text")
    METADATA_FIELD_NAME: Optional[str] = Field(
        default="metadata",
        description="Milvus field storing metadata; set to empty/None if collection lacks metadata",
    )
    EMBEDDING_FIELD_NAME: str = Field(default="embedding", description="Milvus vector field name")

    # Search Configuration
    SEARCH_LIMIT: int = Field(default=5, description="Number of top results to retrieve")
    COSINE_NPROBE: int = Field(default=10, description="Number of clusters to probe in IVF search")

    # RAG System Configuration
    ENABLE_RAG: bool = Field(default=True, description="Enable RAG system for policy retrieval")
    RAG_TEMPERATURE: float = Field(
        default_factory=lambda: float(os.getenv("RAG_TEMPERATURE", "0.2")),
        description="Temperature for RAG LLM responses (lower = more deterministic, higher = more creative)"
    )

    class Config:
        frozen = True


@lru_cache(maxsize=1)
def get_rag_settings() -> RAGSettings:
    """Get cached RAG settings instance."""
    return RAGSettings()


# Global instance
rag_settings = get_rag_settings()

__all__ = ["RAGSettings", "get_rag_settings", "rag_settings"]
