# File: /src/rag/embeddings/__init__.py
# Location: src/rag/embeddings/
# Description: Embeddings module initialization

"""Embeddings module initialization."""

from src.rag.embeddings.gemini_embedder import GeminiEmbedder, get_embedder

__all__ = ["GeminiEmbedder", "get_embedder"]
