# File: /src/rag/embeddings/gemini_embedder.py
# Location: src/rag/embeddings/
# Description: Gemini Embeddings - Generate embeddings using Google's Gemini model

"""Gemini Embeddings - Generate embeddings using Google's Gemini model."""

from __future__ import annotations

from typing import Optional

from google import genai
from google.genai import types

from src.rag.config.rag_config import rag_settings


class GeminiEmbedder:
    """
    Wrapper around Google Gemini embedding model.
    
    Handles embedding generation with configurable dimensions and task types.
    """

    def __init__(self):
        """Initialize Gemini embedder with API configuration."""
        if not rag_settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not configured. Please set it in .env file.")

        self.client = genai.Client(api_key=rag_settings.GOOGLE_API_KEY)
        self.model = rag_settings.EMBED_MODEL
        self.embed_dim = rag_settings.EMBED_DIM

    def embed_text(
        self,
        text: str,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed
            task_type: Task type for embedding ("RETRIEVAL_DOCUMENT" or "RETRIEVAL_QUERY")

        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.embed_dim,
                ),
            )
            return response.embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {str(e)}") from e

    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a query text.

        Args:
            query: Query text to embed

        Returns:
            Embedding vector as list of floats
        """
        return self.embed_text(query, task_type="RETRIEVAL_QUERY")

    def embed_document(self, document: str) -> list[float]:
        """
        Generate embedding for a document text.

        Args:
            document: Document text to embed

        Returns:
            Embedding vector as list of floats
        """
        return self.embed_text(document, task_type="RETRIEVAL_DOCUMENT")

    def embed_batch(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            task_type: Task type for embedding

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                embedding = self.embed_text(text, task_type)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Warning: Failed to embed text: {str(e)}")
                embeddings.append([0.0] * self.embed_dim)  # Fallback: zero vector
        return embeddings


# Global embedder instance (lazy loaded)
_embedder_instance: Optional[GeminiEmbedder] = None


def get_embedder() -> GeminiEmbedder:
    """Get or create global embedder instance."""
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = GeminiEmbedder()
    return _embedder_instance


__all__ = ["GeminiEmbedder", "get_embedder"]
