from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility
)
import asyncio
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google_embedding_client import connect_gemini_embedding
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'milvus_config.yaml'

def load_milvus_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)
milvus_config = load_milvus_config()

MILVUS_HOST = milvus_config["MILVUS_HOST"]
MILVUS_PORT = milvus_config["MILVUS_PORT"]
MILVUS_DATABASE = milvus_config["MILVUS_DATABASE"]  

# Collection & embedding parameters
COLLECTION_NAME = "deep_research_competitor_analysis"
EMBED_DIM = 3072


import numpy as np

def normalize(vectors):
    vectors = np.array(vectors)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / (norms + 1e-10)  # Avoid division by zero



class MilvusVectorStore:
    def __init__(self):
        # Connect to Milvus server with host and port
        connections.connect(
            alias="default",
            host=MILVUS_HOST,
            port=MILVUS_PORT,
            db_name="default",
            secure=False  
        )

        # # Create the database if it does not exist, then switch to it
        # if not utility.has_database(MILVUS_DATABASE):
        #     utility.create_database(MILVUS_DATABASE)
        #     print(f"Created database '{MILVUS_DATABASE}'")
        # else:
        #     print(f"Database '{MILVUS_DATABASE}' exists")
        # connections.switch_database(MILVUS_DATABASE)
        # print(f"Switched to database '{MILVUS_DATABASE}'")

        # Define collection schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBED_DIM),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2048)
        ]
        schema = CollectionSchema(fields=fields, description="Research documents collection")
        # Create or load collection
        if utility.has_collection(COLLECTION_NAME):
            self.collection = Collection(name=COLLECTION_NAME, using="default")
            print(f"Loaded existing collection '{COLLECTION_NAME}'")
        else:
            self.collection = Collection(name=COLLECTION_NAME, schema=schema, using="default")
            print(f"Created new collection '{COLLECTION_NAME}'")

    def insert_documents(self, embeddings, texts):
        # Insert list of embeddings and corresponding texts
        embeddings = normalize(embeddings)
        self.collection.insert([embeddings, texts])
        self.collection.flush()
        print(f"Inserted {len(texts)} documents")

    def create_index(self):
        # Create IVF_FLAT index for vector search if not exists
        if not self.collection.has_index():
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 128}
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
            print("Index created on 'embedding' field")
        else:
            print("Index already exists")

    def load_collection(self):
        # Load data to memory for search
        self.collection.load()
        print("Collection loaded into memory")

    def search(self, query_embeddings, top_k=5, similarity_threshold=0.6):
        # Search vector similarity; returns list of matched texts
        query_embeddings = normalize(query_embeddings)
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=query_embeddings,
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["text"]
        )
        hits = results[0] if results else []
        filtered_results = []
        for hit in hits:
            score = hit.distance
            if score >= similarity_threshold:
                filtered_results.append(hit.entity.get("text"))
        return filtered_results
        # return [hit.entity.get("text") for hit in hits]

async def store_in_vector_store(input_text):
    try:
        gemini_embedding = connect_gemini_embedding()
        embeddings_model = gemini_embedding['model'] if gemini_embedding['status'] else None
        if embeddings_model is None:
            raise Exception("Failed to connect to Gemini Embedding model.")

        # Split input into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(input_text)

        def blocking_store():
            store = MilvusVectorStore()
            doc_embeddings = embeddings_model.embed_documents(chunks)
            store.insert_documents(doc_embeddings, chunks)
            store.create_index()
            store.load_collection()
            return True

        result = await asyncio.to_thread(blocking_store)
        return result

    except Exception as e:
        print(f"Error in storing documents: {e}")
        return False

# Async search function
async def search_in_vector_store(user_input, top_k=5, similarity_threshold=0.5):
    try:
        gemini_embedding = connect_gemini_embedding()
        embeddings_model = gemini_embedding["model"] if gemini_embedding["status"] else None
        if embeddings_model is None:
            raise Exception("Failed to connect to Gemini Embedding model.")

        store = MilvusVectorStore()

        query_embedding = embeddings_model.embed_query(user_input)
        results = store.search([query_embedding], top_k=top_k)

        result_text = ""
        for text in results:
            result_text += text + "\n"

        return result_text

    except Exception as e:
        print(f"Error in searching documents: {e}")
        return ""

