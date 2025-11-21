import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_classic.text_splitter import CharacterTextSplitter
from src.database.malvius_integration import MilvusDB

load_dotenv()


# -----------------------------------------------------------
# Load & Chunk Knowledge Base
# -----------------------------------------------------------

def load_and_prepare_docs(base_path="knowledgebase/handle"):
    """Load and split text documents into chunks."""
    loader = DirectoryLoader(
        base_path,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
    chunks = text_splitter.split_documents(documents)

    print(f"📄 Loaded {len(chunks)} text chunks from {len(documents)} documents.")
    return chunks


# -----------------------------------------------------------
# Persistent Objects
# -----------------------------------------------------------

_milvus_db = None
_retriever = None

COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "ticket_creation_knowledge")
EMBED_DIM = 1536
SEARCH_K = 8


# -----------------------------------------------------------
# 1. Load existing vectorstore (NO REBUILD)
# -----------------------------------------------------------

def load_existing_vectorstore():
    """Attach to existing Milvus collection WITHOUT rebuilding."""
    global _milvus_db, _retriever

    if _retriever is not None:
        return _retriever

    print("🔗 Loading existing Milvus collection (no rebuild)...")
    _milvus_db = MilvusDB(collection_name=COLLECTION_NAME, dimension=EMBED_DIM)
    
    if not _milvus_db.client.has_collection(COLLECTION_NAME):
        raise Exception("Collection does not exist")
    
    _retriever = _milvus_db
    print("✅ Milvus retriever loaded.")
    return _retriever


# -----------------------------------------------------------
# 2. Full rebuild (ON DEMAND ONLY)
# -----------------------------------------------------------

def rebuild_vectorstore(base_path="knowledgebase/handle"):
    """Rebuild Milvus vectorstore completely (called only on endpoint)."""
    global _milvus_db, _retriever

    print("🧹 Rebuilding Milvus vectorstore...")
    print(f"📂 Loading documents from: {base_path}")
    chunks = load_and_prepare_docs(base_path)
    print(f"✅ Loaded {len(chunks)} chunks")
    
    _milvus_db = MilvusDB(collection_name=COLLECTION_NAME, dimension=EMBED_DIM)
    print("🔄 Building vectorstore from documents...")
    _milvus_db.build_vectorstore_from_docs(chunks)
    _retriever = _milvus_db
    print("✨ Vectorstore rebuilt successfully.")
    return _retriever


# -----------------------------------------------------------
# Public API
# -----------------------------------------------------------

def get_retriever():
    """
    Load existing Milvus vectorstore.
    If the collection or index does not exist → build automatically once.
    """
    global _retriever

    if _retriever:
        return _retriever

    try:
        print("🔍 Trying to load existing Milvus collection...")
        retr = load_existing_vectorstore()
        if retr:
            print("✅ Loaded existing Milvus retriever.")
            return retr
    except Exception as e:
        print(f"⚠️ Existing vectorstore load failed: {e}")
        import traceback
        traceback.print_exc()

    print("⚠️ No Milvus collection found — building vectorstore...")
    try:
        _retriever = rebuild_vectorstore()
        print("🎉 Auto-build completed. Retriever ready.")
        return _retriever
    except Exception as e:
        print(f"❌ Auto-build failed: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Milvus retriever initialization failed: {e}")



def init_rag():
    """Alias used by main.py"""
    return get_retriever()
