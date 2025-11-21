# db.py (Final Version — Persistent Milvus + Safe Rebuild)
import os
from dotenv import load_dotenv, find_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from pymilvus import MilvusClient


# ----------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------
load_dotenv(find_dotenv(), override=True)


class MilvusDB:
    """
    Unified Milvus handler for:
    - Safe persistent vectorstore use
    - Optional rebuild
    - Retriever loading
    - CRUD operations
    """

    def __init__(self, collection_name="vector_db", dimension=1536):
        self.collection_name = collection_name
        self.dimension = dimension

        self.uri = os.getenv("MILVUS_URI")
        self.token = os.getenv("MILVUS_TOKEN")

        if not self.uri or not self.token:
            raise ValueError("Missing MILVUS_URI or MILVUS_TOKEN in .env")

        # pymilvus client (admin ops)
        self.client = MilvusClient(uri=self.uri, token=self.token)
        print(f"🔗 Connected to Milvus collection → {self.collection_name}")

    # ----------------------------------------------------------------
    # Build or rebuild a vectorstore
    # ----------------------------------------------------------------
    def build_vectorstore_from_docs(self, docs, recreate=True):
        """
        Build a vectorstore from docs.
        recreate=True  → drop + rebuild
        recreate=False → DO NOT DROP, append/update
        """

        embeddings = OpenAIEmbeddings()

        if recreate:
            # SAFE REBUILD
            if self.client.has_collection(self.collection_name):
                print(f"⚠️ Dropping existing collection '{self.collection_name}'...")
                self.client.drop_collection(self.collection_name)
        else:
            # SAFE REUSE
            if self.client.has_collection(self.collection_name):
                print(f"♻️ Reusing existing Milvus collection (no rebuild).")
                return self.get_existing_vectorstore()

        print(f"🧠 Creating Milvus vector store with {len(docs)} docs (recreate={recreate})...")

        vectorstore = Milvus.from_documents(
            documents=docs,
            embedding=embeddings,
            connection_args={
                "uri": self.uri,
                "token": self.token,
                "secure": True,
            },
            collection_name=self.collection_name,
        )

        print(f"✅ Vector store built → {self.collection_name}")
        return vectorstore

    # ----------------------------------------------------------------
    # Load existing vectorstore WITHOUT rebuilding
    # ----------------------------------------------------------------
    def get_existing_vectorstore(self):
        """Attach to existing Milvus collection without recreating it."""
        embeddings = OpenAIEmbeddings()

        if not self.client.has_collection(self.collection_name):
            raise ValueError(
                f"❌ Collection '{self.collection_name}' does not exist. Build it first!"
            )

        print(f"🔗 Loading existing vectorstore → {self.collection_name}")

        return Milvus(
            embedding_function=embeddings,
            connection_args={
                "uri": self.uri,
                "token": self.token,
                "secure": True,
            },
            collection_name=self.collection_name,
        )

    # ----------------------------------------------------------------
    # Retriever creation (from existing)
    # ----------------------------------------------------------------
    def get_retriever(self, search_k=10):
        """Return retriever for existing Milvus vectorstore."""
        vectorstore = self.get_existing_vectorstore()
        return vectorstore.as_retriever(search_kwargs={"k": search_k})

    # ----------------------------------------------------------------
    # CRUD operations
    # ----------------------------------------------------------------
    def insert_vectors(self, data):
        self.client.insert(collection_name=self.collection_name, data=data)

    def query(self, filter_expr):
        return self.client.query(collection_name=self.collection_name, filter=filter_expr)

    def upsert_vector(self, data):
        self.client.upsert(collection_name=self.collection_name, data=data)

    def delete_vectors(self, ids):
        self.client.delete(collection_name=self.collection_name, ids=ids)
