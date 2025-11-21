"""Milvus vector store for storing and retrieving transcripts."""
import json
import litellm
from typing import List, Dict, Any, Optional
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)
from src.utils.config_loader import get_config
from src.utils.logger import setup_logger
from src.utils.text_chunker import TextChunker
from src.utils.retry_handler import retry_llm_call
from src.utils.exception_handler import DatabaseError, LLMError, log_exception


class MilvusVectorStore:
    """Manage transcript storage and retrieval using Milvus with chunking support."""

    def __init__(self, user_id: Optional[str] = None):
        """Initialize Milvus vector store."""
        self.config = get_config()
        self.logger = setup_logger(__name__)

        # Configure LiteLLM for Gemini embeddings
        import os
        self.api_key = os.getenv('LLM_KEY')
        self.embedding_model = "gemini/text-embedding-004"

        # Set LiteLLM configuration
        litellm.api_key = self.api_key

        self.user_id = user_id
        self.collection_name = self.config.get('milvus.collection_name', 'RASA')
        self.dimension = 768

        # Initialize text chunker
        self.chunker = TextChunker()

        # Connect to Milvus
        self._connect()

        # Create or load collection
        self._setup_collection()
    
    def _connect(self):
        """Connect to Milvus server."""
        try:
            host = self.config.get('milvus.host', 'localhost')
            port = self.config.get('milvus.port', 19530)
            user = self.config.get('milvus.user', '')
            password = self.config.get('milvus.password', '')
            database = self.config.get('milvus.database', 'default')
            secure = self.config.get('milvus.secure', False)

            # Build connection parameters
            conn_params = {
                "alias": "default",
                "host": host,
                "port": port,
                "db_name": database
            }

            # Add authentication if provided
            if user and password:
                conn_params["user"] = user
                conn_params["password"] = password

            # Add secure connection if needed
            if secure:
                conn_params["secure"] = True

            connections.connect(**conn_params)
            self.logger.info(f"✅ Connected to Milvus at {host}:{port} (database: {database})")

        except Exception as e:
            log_exception(e, context="MilvusVectorStore._connect", extra_info={"host": host, "port": port, "database": database})
            self.logger.error(f"❌ Failed to connect to Milvus: {e}")
            raise DatabaseError(
                f"Failed to connect to Milvus database at {host}:{port}: {str(e)}",
                details={"host": host, "port": port, "database": database, "error": str(e)}
            )
    
    def _setup_collection(self):
        """Create or load the collection."""
        try:
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.logger.info(f"✅ Collection '{self.collection_name}' already exists, loaded successfully")
            else:
                # Create new collection
                self._create_collection()
                self.logger.info(f"✅ Created new collection: {self.collection_name}")

            # Load collection to memory
            self.collection.load()
            self.logger.info(f"✅ Collection '{self.collection_name}' loaded to memory")

        except DatabaseError:
            raise
        except Exception as e:
            log_exception(e, context="MilvusVectorStore._setup_collection", extra_info={"collection_name": self.collection_name})
            self.logger.error(f"❌ Failed to setup collection: {e}")
            raise DatabaseError(
                f"Failed to setup Milvus collection '{self.collection_name}': {str(e)}",
                details={"collection_name": self.collection_name, "error": str(e)}
            )
    
    def _create_collection(self):
        """Create a new Milvus collection for transcripts."""
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="transcript_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            FieldSchema(name="transcript_text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="analysis_result", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="timestamp", dtype=DataType.INT64)
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Sales conversation transcripts with embeddings"
        )

        # Create collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )

        # Create index on embedding
        index_params = {
            "metric_type": self.config.get('milvus.metric_type', 'L2'),
            "index_type": self.config.get('milvus.index_type', 'IVF_FLAT'),
            "params": {"nlist": self.config.get('milvus.nlist', 128)}
        }

        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )

        # Create index on user_id for filtering
        self.collection.create_index(
            field_name="user_id",
            index_name=f"idx_user_id_{self.collection_name}"
        )
    
    @retry_llm_call
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using LiteLLM with Gemini.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Truncate text if too long
        max_chars = 20000
        if len(text) > max_chars:
            self.logger.warning(f"Text too long ({len(text)} chars), truncating to {max_chars} chars for embedding")
            text = text[:max_chars]

        response = litellm.embedding(
            model=self.embedding_model,
            input=[text],
            api_key=self.api_key
        )

        return response.data[0]['embedding']

    def chunk_and_display(self, text: str) -> Dict[str, Any]:
        """Chunk text and display statistics (for demonstration).

        This method demonstrates the chunking functionality using LangChain text splitters.

        Args:
            text: Text to chunk

        Returns:
            Dictionary with chunks and statistics
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("CHUNKING DEMONSTRATION")
            self.logger.info("=" * 80)

            # Method 1: Recursive Character Splitter (Recommended)
            self.logger.info("\n📄 Method 1: Recursive Character Text Splitter")
            self.logger.info("-" * 80)
            recursive_chunks = self.chunker.chunk_text_recursive(text)
            recursive_stats = self.chunker.get_chunk_stats(recursive_chunks)

            self.logger.info(f"✓ Total Chunks: {recursive_stats['total_chunks']}")
            self.logger.info(f"✓ Avg Chunk Size: {recursive_stats['avg_chunk_size']} chars")
            self.logger.info(f"✓ Min/Max Size: {recursive_stats['min_chunk_size']}/{recursive_stats['max_chunk_size']} chars")

            for idx, chunk in enumerate(recursive_chunks[:2], 1):  # Show first 2 chunks
                self.logger.info(f"\nChunk {idx} Preview (first 200 chars):")
                self.logger.info(f"  {chunk[:200]}...")

            # Method 2: Token-based Splitter
            self.logger.info("\n\n📄 Method 2: Token-based Text Splitter")
            self.logger.info("-" * 80)
            token_chunks = self.chunker.chunk_text_by_tokens(text)
            token_stats = self.chunker.get_chunk_stats(token_chunks)

            self.logger.info(f"✓ Total Chunks: {token_stats['total_chunks']}")
            self.logger.info(f"✓ Avg Chunk Size: {token_stats['avg_chunk_size']} chars")
            self.logger.info(f"✓ Min/Max Size: {token_stats['min_chunk_size']}/{token_stats['max_chunk_size']} chars")

            # Method 3: Document Chunks with Metadata
            self.logger.info("\n\n📄 Method 3: Document Chunks with Metadata")
            self.logger.info("-" * 80)
            doc_chunks = self.chunker.chunk_documents(
                text,
                metadata={'source': 'demo', 'type': 'transcript'}
            )

            self.logger.info(f"✓ Total Document Chunks: {len(doc_chunks)}")
            if doc_chunks:
                self.logger.info(f"\nFirst Document Chunk Info:")
                self.logger.info(f"  Chunk Index: {doc_chunks[0]['chunk_index']}")
                self.logger.info(f"  Total Chunks: {doc_chunks[0]['total_chunks']}")
                self.logger.info(f"  Chunk Size: {doc_chunks[0]['chunk_size']} chars")
                self.logger.info(f"  Metadata: {doc_chunks[0].get('metadata', {})}")

            self.logger.info("\n" + "=" * 80)

            return {
                'recursive_chunks': recursive_chunks,
                'recursive_stats': recursive_stats,
                'token_chunks': token_chunks,
                'token_stats': token_stats,
                'document_chunks': doc_chunks
            }

        except Exception as e:
            self.logger.error(f"Error in chunking demonstration: {e}")
            return {}
    
    def store_transcript(
        self,
        transcript_id: str,
        transcript_text: str,
        analysis_result: Dict[str, Any],
        source_type: str = "text"
    ) -> bool:
        """Store transcript and its analysis in Milvus.

        Args:
            transcript_id: Unique identifier for the transcript
            transcript_text: The transcript text
            analysis_result: Analysis results dictionary
            source_type: Source type (text or audio)

        Returns:
            True if successful, False otherwise
        """
        try:
            import time

            if not transcript_id or not transcript_text:
                raise DatabaseError(
                    "Transcript ID and text are required",
                    details={"transcript_id": transcript_id, "has_text": bool(transcript_text)}
                )

            # Generate embedding
            try:
                embedding = self._get_embedding(transcript_text)
            except Exception as e:
                log_exception(e, context="MilvusVectorStore.store_transcript (embedding)")
                raise LLMError(
                    f"Failed to generate embedding: {str(e)}",
                    details={"transcript_id": transcript_id}
                )

            # Prepare data
            data = [
                [transcript_id],
                [self.user_id],
                [embedding],
                [transcript_text],
                [json.dumps(analysis_result)],
                [source_type],
                [int(time.time())]
            ]

            # Insert into collection
            self.collection.insert(data)
            self.collection.flush()

            self.logger.info(f"✅ Stored transcript: {transcript_id} for user: {self.user_id}")
            return True

        except (DatabaseError, LLMError):
            raise
        except Exception as e:
            log_exception(e, context="MilvusVectorStore.store_transcript", extra_info={"transcript_id": transcript_id})
            self.logger.error(f"❌ Failed to store transcript: {e}")
            raise DatabaseError(
                f"Failed to store transcript in database: {str(e)}",
                details={"transcript_id": transcript_id, "error": str(e)}
            )
    
    def search_similar_transcripts(
        self,
        query_text: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar transcripts.

        Args:
            query_text: Query text to search for
            top_k: Number of results to return

        Returns:
            List of similar transcripts with their analysis
        """
        try:
            if not query_text:
                self.logger.warning("Empty query text provided for search")
                return []

            # Generate query embedding
            try:
                query_embedding = self._get_embedding(query_text)
            except Exception as e:
                log_exception(e, context="MilvusVectorStore.search_similar_transcripts (embedding)")
                raise LLMError(
                    f"Failed to generate query embedding: {str(e)}",
                    details={"query_text": query_text[:100]}
                )

            # Search parameters
            search_params = {
                "metric_type": self.config.get('milvus.metric_type', 'L2'),
                "params": {"nprobe": 10}
            }

            # Perform search with user_id filter
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=f'user_id == "{self.user_id}"',
                output_fields=["transcript_id", "user_id", "transcript_text", "analysis_result", "source_type", "timestamp"]
            )

            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    try:
                        formatted_results.append({
                            "transcript_id": hit.entity.get("transcript_id"),
                            "transcript_text": hit.entity.get("transcript_text"),
                            "analysis_result": json.loads(hit.entity.get("analysis_result")),
                            "source_type": hit.entity.get("source_type"),
                            "timestamp": hit.entity.get("timestamp"),
                            "distance": hit.distance
                        })
                    except Exception as e:
                        self.logger.warning(f"Failed to format search result: {e}")
                        continue

            self.logger.info(f"✅ Found {len(formatted_results)} similar transcripts for user {self.user_id}")
            return formatted_results

        except LLMError:
            raise
        except Exception as e:
            log_exception(e, context="MilvusVectorStore.search_similar_transcripts", extra_info={"user_id": self.user_id})
            self.logger.error(f"❌ Failed to search transcripts: {e}")
            raise DatabaseError(
                f"Failed to search transcripts: {str(e)}",
                details={"user_id": self.user_id, "error": str(e)}
            )
    
    def get_transcript_by_id(self, transcript_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve transcript by ID.

        Args:
            transcript_id: Transcript identifier

        Returns:
            Transcript data or None if not found
        """
        try:
            if not transcript_id:
                self.logger.warning("Empty transcript_id provided")
                return None

            results = self.collection.query(
                expr=f'transcript_id == "{transcript_id}" && user_id == "{self.user_id}"',
                output_fields=["transcript_id", "user_id", "transcript_text", "analysis_result", "source_type", "timestamp"]
            )

            if results:
                result = results[0]
                try:
                    return {
                        "transcript_id": result.get("transcript_id"),
                        "transcript_text": result.get("transcript_text"),
                        "analysis_result": json.loads(result.get("analysis_result")),
                        "source_type": result.get("source_type"),
                        "timestamp": result.get("timestamp")
                    }
                except Exception as e:
                    log_exception(e, context="MilvusVectorStore.get_transcript_by_id (parsing)")
                    self.logger.error(f"Failed to parse transcript data: {e}")
                    return None

            self.logger.info(f"Transcript not found: {transcript_id}")
            return None

        except Exception as e:
            log_exception(e, context="MilvusVectorStore.get_transcript_by_id", extra_info={"transcript_id": transcript_id})
            self.logger.error(f"❌ Failed to retrieve transcript: {e}")
            raise DatabaseError(
                f"Failed to retrieve transcript: {str(e)}",
                details={"transcript_id": transcript_id, "error": str(e)}
            )
    
    def disconnect(self):
        """Disconnect from Milvus."""
        try:
            connections.disconnect("default")
            self.logger.info("✅ Disconnected from Milvus")
        except Exception as e:
            log_exception(e, context="MilvusVectorStore.disconnect")
            self.logger.error(f"⚠️ Error disconnecting from Milvus: {e}")

