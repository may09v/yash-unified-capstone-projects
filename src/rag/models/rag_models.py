"""Data models for RAG system."""

from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """Request model for policy queries."""

    question: str = Field(..., description="User question about travel policy")
    use_rag: bool = Field(default=True, description="Use RAG context for answering")


class DocumentChunk(BaseModel):
    """Represents a document chunk in vector store."""

    text: str = Field(..., description="Document text")
    metadata: str = Field(default="", description="Source or section info")
    embedding: Optional[List[float]] = Field(default=None, description="Embedding vector")


class QueryResult(BaseModel):
    """Result from policy query."""

    answer: str = Field(..., description="Generated answer")
    question: str = Field(..., description="Original question")
    sources: List[dict] = Field(default_factory=list, description="Retrieved source documents")
    used_context: bool = Field(default=True, description="Whether RAG was used")
    error: Optional[str] = Field(default=None, description="Error message if any")


__all__ = ["QueryRequest", "DocumentChunk", "QueryResult"]
