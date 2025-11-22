# File: /src/rag/retrieval/milvus_retriever.py
# Location: src/rag/retrieval/
# Description: Milvus Vector Store - Manages vector database for policy documents

"""Milvus Vector Store - Manages vector database for policy documents."""

from __future__ import annotations

import json
from typing import Optional, List, Union, Dict, Any

from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility

from src.rag.config.rag_config import rag_settings


class MilvusRetriever:
    """
    Wrapper around Milvus vector database for document retrieval.
    
    Handles connection, collection management, and similarity search.
    """

    def __init__(self):
        """Initialize Milvus retriever and connect to remote instance."""
        self.uri = rag_settings.MILVUS_URI
        self.token = rag_settings.MILVUS_TOKEN
        self.collection_name = rag_settings.COLLECTION_NAME
        self.embed_dim = rag_settings.EMBED_DIM
        self.search_limit = rag_settings.SEARCH_LIMIT
        self.nprobe = rag_settings.COSINE_NPROBE
        self.text_field = rag_settings.TEXT_FIELD_NAME
        self.metadata_field = rag_settings.METADATA_FIELD_NAME
        self.embedding_field = rag_settings.EMBEDDING_FIELD_NAME
        self._has_metadata_field = False

        self.collection = None
        self._connect()

    def _connect(self) -> None:
        """Establish connection to Milvus instance."""
        try:
            connections.connect(alias="default", uri=self.uri, token=self.token)
            print(f"✅ Connected to Milvus: {self.uri}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Milvus: {str(e)}") from e

    def _ensure_collection_exists(self) -> None:
        """Create collection if it doesn't exist, with proper schema."""
        try:
            if utility.has_collection(self.collection_name):
                print(f"✅ Collection '{self.collection_name}' already exists")
                self.collection = Collection(self.collection_name)
                self.collection.load()
            else:
                self._create_collection()
            self._sync_schema_capabilities()
        except Exception as e:
            raise RuntimeError(f"Failed to ensure collection exists: {str(e)}") from e

    def _create_collection(self) -> None:
        """Create new Milvus collection with embedding field."""
        print(f"🔨 Creating collection: {self.collection_name}")

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name=self.text_field, dtype=DataType.VARCHAR, max_length=10000),
        ]

        if self.metadata_field:
            fields.append(
                FieldSchema(
                    name=self.metadata_field,
                    dtype=DataType.VARCHAR,
                    max_length=2000,
                )
            )

        fields.append(
            FieldSchema(
                name=self.embedding_field,
                dtype=DataType.FLOAT_VECTOR,
                dim=self.embed_dim,
            )
        )

        schema = CollectionSchema(fields, description="Travel Policy RAG Collection")
        self.collection = Collection(self.collection_name, schema)

        # Create index for faster search
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        }
        self.collection.create_index(field_name=self.embedding_field, index_params=index_params)
        self.collection.load()
        self._sync_schema_capabilities()
        print(f"✅ Collection created and indexed")

    def _sync_schema_capabilities(self) -> None:
        """Determine field availability based on loaded collection schema."""
        schema_fields = {field.name for field in self.collection.schema.fields}

        if self.text_field not in schema_fields:
            raise RuntimeError(
                f"Configured text field '{self.text_field}' not found in collection '{self.collection_name}'. "
                f"Available fields: {', '.join(sorted(schema_fields))}"
            )

        if self.embedding_field not in schema_fields:
            raise RuntimeError(
                f"Configured embedding field '{self.embedding_field}' not found in collection '{self.collection_name}'. "
                f"Available fields: {', '.join(sorted(schema_fields))}"
            )

        self._has_metadata_field = bool(self.metadata_field) and self.metadata_field in schema_fields

    def add_documents(self, texts: List[str], embeddings: List[List[float]], metadata: Optional[List[str]] = None) -> None:
        """
        Add documents to the collection.

        Args:
            texts: List of text documents
            embeddings: List of embedding vectors
            metadata: Optional list of metadata strings (e.g., policy section)
        """
        self._ensure_collection_exists()

        if len(texts) != len(embeddings):
            raise ValueError("texts and embeddings must have same length")

        if self._has_metadata_field:
            if metadata is None:
                metadata = ["policy"] * len(texts)
        else:
            metadata = None

        try:
            data: List[List[str] | List[List[float]]] = [texts]

            if self._has_metadata_field and metadata is not None:
                data.append(metadata)

            data.append(embeddings)
            self.collection.insert(data)
            self.collection.flush()
            print(f"✅ Added {len(texts)} documents to collection")
        except Exception as e:
            raise RuntimeError(f"Failed to add documents to Milvus: {str(e)}") from e

    def search(self, query_embedding: List[float], limit: Optional[int] = None) -> List[dict]:
        """
        Search for documents similar to query embedding.

        Args:
            query_embedding: Query embedding vector
            limit: Number of results to return (uses default if not specified)

        Returns:
            List of dictionaries with 'text', 'metadata', and 'distance'
        """
        self._ensure_collection_exists()

        limit = limit or self.search_limit

        try:
            search_params = {"metric_type": "COSINE", "params": {"nprobe": self.nprobe}}

            output_fields = [self.text_field]
            if self._has_metadata_field:
                output_fields.append(self.metadata_field)

            results = self.collection.search(
                data=[query_embedding],
                anns_field=self.embedding_field,
                param=search_params,
                limit=limit,
                output_fields=output_fields,
            )

            hits = results[0]
            search_results = []

            for hit in hits:
                text_value = hit.entity.get(self.text_field, "")
                raw_metadata = (
                    hit.entity.get(self.metadata_field, "") if self._has_metadata_field else ""
                )

                parsed_metadata = self._parse_metadata(raw_metadata)

                search_results.append({
                    "text": text_value,
                    "metadata": parsed_metadata,
                    "distance": hit.distance,
                    "score": 1 - hit.distance,  # Convert distance to similarity score
                })

            return search_results
        except Exception as e:
            raise RuntimeError(f"Failed to search in Milvus: {str(e)}") from e

    def reset_collection(self) -> None:
        """Drop and recreate collection."""
        try:
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                print(f"✅ Dropped collection '{self.collection_name}'")
            self._create_collection()
        except Exception as e:
            raise RuntimeError(f"Failed to reset collection: {str(e)}") from e

    def get_collection_stats(self) -> dict:
        """Get statistics about the collection."""
        self._ensure_collection_exists()
        try:
            stats = {
                "collection_name": self.collection_name,
                "num_entities": self.collection.num_entities,
                "embed_dim": self.embed_dim,
            }
            return stats
        except Exception as e:
            raise RuntimeError(f"Failed to get collection stats: {str(e)}") from e

    def _parse_metadata(self, value: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        """Parse metadata JSON strings, falling back to the original value."""
        if isinstance(value, dict):
            return value
        if not value:
            return ""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


# Global retriever instance (lazy loaded)
_retriever_instance: Optional[MilvusRetriever] = None


def get_retriever() -> MilvusRetriever:
    """Get or create global retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = MilvusRetriever()
    return _retriever_instance


__all__ = ["MilvusRetriever", "get_retriever"]
