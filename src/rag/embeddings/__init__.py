"""Embeddings module initialization."""

from src.rag.embeddings.gemini_embedder import GeminiEmbedder, get_embedder

__all__ = ["GeminiEmbedder", "get_embedder"]
