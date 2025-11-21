"""Policy Document Ingestion - Load policy documents into Milvus vector store."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple

import pdfplumber

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.rag.embeddings.gemini_embedder import get_embedder
from src.rag.retrieval.chunk_metadata import ChunkMetadataGenerator
from src.rag.retrieval.milvus_retriever import get_retriever


class PolicyIngestion:
    """Handles loading and ingesting policy documents into vector store."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        """
        Initialize policy ingestion.

        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.embedder = get_embedder()
        self.retriever = get_retriever()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        self.metadata_generator = ChunkMetadataGenerator()

    def load_document(self, file_path: str, metadata: str = "") -> List[Tuple[str, str]]:
        """
        Load and chunk a markdown policy file.

        Args:
            file_path: Path to markdown file
            metadata: Metadata/source info for chunks

        Returns:
            List of (text, metadata) tuples
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Policy file not found: {file_path}")

        print(f"📄 Loading policy document: {file_path}")

        suffix = Path(file_path).suffix.lower()

        if suffix == ".pdf":
            content = self._extract_pdf_text(file_path)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        chunks = self.splitter.split_text(content)
        print(f"✂️ Split into {len(chunks)} chunks")

        # Create metadata with file name
        file_name = Path(file_path).stem
        source_metadata = metadata or file_name

        return [(chunk, source_metadata) for chunk in chunks]

    def load_policy_documents(self, policy_dir: str = ".") -> None:
        """
        Load all policy markdown files from directory.

        Args:
            policy_dir: Directory containing policy files
        """
        policy_dir = Path(policy_dir)

        # Find markdown files
        policy_files = list(policy_dir.glob("*Travel*Policy*.md"))

        if not policy_files:
            print(f"⚠️ No policy files found in {policy_dir}")
            return

        print(f"🔍 Found {len(policy_files)} policy file(s)")
        self._process_and_store_chunks(policy_files)

    def ingest_files(self, file_paths: List[str]) -> None:
        """Ingest a specific list of files."""

        policy_files = [Path(path) for path in file_paths if Path(path).is_file()]

        if not policy_files:
            print("⚠️ No valid files provided for ingestion")
            return

        self._process_and_store_chunks(policy_files)

    def _process_and_store_chunks(self, policy_files: List[Path]) -> None:
        all_chunks: List[str] = []
        all_metadata: List[str] = []

        chunk_counter = 0
        for policy_file in policy_files:
            chunks_with_metadata = self.load_document(
                str(policy_file),
                metadata=policy_file.stem
            )
            for chunk, source_label in chunks_with_metadata:
                metadata_payload = self.metadata_generator.generate_metadata(
                    chunk_text=chunk,
                    source_name=source_label,
                    file_path=str(policy_file),
                    chunk_index=chunk_counter,
                )
                all_chunks.append(chunk)
                all_metadata.append(json.dumps(metadata_payload, ensure_ascii=False))
                chunk_counter += 1

        if not all_chunks:
            print("⚠️ No policy content loaded")
            return

        print(f"📦 Total chunks to ingest: {len(all_chunks)}")

        # Generate embeddings
        print("🔄 Generating embeddings...")
        embeddings = self.embedder.embed_batch(all_chunks, task_type="RETRIEVAL_DOCUMENT")
        print(f"✅ Generated {len(embeddings)} embeddings")

        # Store in Milvus
        print("💾 Storing in Milvus...")
        self.retriever.add_documents(all_chunks, embeddings, all_metadata)
        print("✅ Ingestion complete!")

        # Print stats
        stats = self.retriever.get_collection_stats()
        print(f"\n📊 Collection Stats:")
        print(f"   - Collection: {stats['collection_name']}")
        print(f"   - Documents: {stats['num_entities']}")
        print(f"   - Embedding Dim: {stats['embed_dim']}")

    @staticmethod
    def _extract_pdf_text(file_path: str) -> str:
        """Extract text from a PDF using pdfplumber."""

        text_chunks: List[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text() or ""
                except Exception as exc:  # pragma: no cover - pdf quirks
                    print(f"⚠️ Failed to extract text from page {page_number} in {file_path}: {exc}")
                    page_text = ""
                text_chunks.append(page_text)
        return "\n".join(text_chunks)


def ingest_policies(policy_dir: str = ".") -> None:
    """
    Main function to ingest policy documents.

    Args:
        policy_dir: Directory containing policy markdown files
    """
    try:
        ingestion = PolicyIngestion()
        ingestion.load_policy_documents(policy_dir)
    except Exception as e:
        print(f"❌ Ingestion failed: {str(e)}")
        raise


def ingest_files(file_paths: List[str]) -> None:
    """Convenience wrapper to ingest a provided list of files."""

    try:
        ingestion = PolicyIngestion()
        ingestion.ingest_files(file_paths)
    except Exception as e:
        print(f"❌ Ingestion failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Ingest from current directory
    ingest_policies()
