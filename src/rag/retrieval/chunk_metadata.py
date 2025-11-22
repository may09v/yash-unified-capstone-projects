# File: /src/rag/retrieval/chunk_metadata.py
# Location: src/rag/retrieval/
# Description: Chunk metadata generation using ChatLiteLLM

"""Chunk metadata generation using ChatLiteLLM.

This helper runs a lightweight LLM prompt per chunk to capture
structured metadata (source, summary, topics, keywords, etc.) so that
chunks can be stored with richer context for downstream retrieval.
"""

from __future__ import annotations

import json
from typing import Any, Dict
from uuid import uuid4
from textwrap import dedent

from langchain_core.messages import HumanMessage

from agent.llm import create_llm


class ChunkMetadataGenerator:
    """Generate structured metadata for text chunks using ChatLiteLLM."""

    def __init__(self, temperature: float = 0.0) -> None:
        self.llm = create_llm()
        if hasattr(self.llm, "temperature"):
            # Metadata extraction should be deterministic
            self.llm.temperature = temperature

    def generate_metadata(
        self,
        chunk_text: str,
        source_name: str,
        file_path: str,
        chunk_index: int,
    ) -> Dict[str, Any]:
        """Return a metadata payload describing the chunk.

        Args:
            chunk_text: The chunk contents.
            source_name: Short source label (e.g., filename stem).
            file_path: Full path to the file (for traceability).
            chunk_index: Absolute chunk index within the ingestion batch.
        """

        prompt = dedent(
            f'''
            You are a data annotator for a corporate travel policy RAG system.
            Read the chunk below and respond with STRICT JSON (no additional text).
            JSON schema:
            {{
                "source": string (short name identifying the file or policy section),
                "filename": string (original filename),
                "chunk_summary": string (concise 1-2 sentence summary),
                "country_or_region": string | null,
                "employee_grades": list[string] | null,
                "topics": list[string],
                "keywords": list[string],
                "chunk_index": integer,
                "chunk_id": string (uuid),
                "file_path": string
            }}

            If you cannot determine a field, set it to null or an empty list.

            SOURCE NAME: {source_name}
            FILE PATH: {file_path}
            CHUNK INDEX: {chunk_index}

            CHUNK:
            """{chunk_text.strip()}"""
            '''
        ).strip()

        message = HumanMessage(content=prompt)

        try:
            response = self.llm.invoke([message])
            metadata = self._parse_json_response(response.content)
        except Exception:
            metadata = {}

        metadata.setdefault("source", source_name)
        metadata.setdefault("filename", source_name)
        metadata.setdefault("chunk_summary", chunk_text[:160].strip())
        metadata.setdefault("topics", [])
        metadata.setdefault("keywords", [])
        metadata.setdefault("chunk_index", chunk_index)
        metadata.setdefault("chunk_id", str(uuid4()))
        metadata.setdefault("file_path", file_path)

        return metadata

    @staticmethod
    def _parse_json_response(response_text: str) -> Dict[str, Any]:
        """Attempt to coerce LLM output into JSON."""
        text = response_text.strip()

        # Handle fenced code blocks
        if text.startswith("```"):
            lines = text.splitlines()
            # Drop the first and last fence lines
            text = "\n".join(line for line in lines if not line.strip().startswith("```")).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Attempt to locate JSON substring
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    pass
        return {}


__all__ = ["ChunkMetadataGenerator"]
