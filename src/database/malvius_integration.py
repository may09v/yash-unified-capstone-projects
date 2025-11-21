import os
from dotenv import load_dotenv, find_dotenv
from pymilvus import MilvusClient
from openai import OpenAI

load_dotenv()


class MilvusDB:
    def __init__(self, collection_name=None, dimension=1536):
        self.collection_name = collection_name or os.getenv("MILVUS_COLLECTION_NAME", "vector_db")
        self.dimension = dimension
        
        self.uri = os.getenv("MILVUS_URI")
        self.token = os.getenv("MILVUS_TOKEN")
        if not self.uri or not self.token:
            raise ValueError("Missing MILVUS_URI or MILVUS_TOKEN in .env file")
        
        self.client = MilvusClient(uri=self.uri, token=self.token)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print(f"🔗 Connected to Milvus collection '{self.collection_name}'")

    def _get_embedding(self, text):
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def build_vectorstore_from_docs(self, docs):
        if self.client.has_collection(self.collection_name):
            print(f"⚠️ Dropping existing collection '{self.collection_name}'...")
            self.client.drop_collection(self.collection_name)
        
        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=self.dimension,
            namespace="IT_HELP_DESK"
        )
        
        print(f"🧠 Creating Milvus vector store with {len(docs)} documents...")
        data = []
        for i, doc in enumerate(docs):
            text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            
            data.append({
                "id": i,
                "vector": self._get_embedding(text),
                "text": text,
                "metadata": str(metadata)
            })
        
        self.client.insert(collection_name=self.collection_name, data=data)
        print("✅ Vector store built successfully!")
        print(f"Collection: {self.collection_name}")
        print(f"Document count: {len(docs)}")

    def insert_vectors(self, data):
        print(f"📝 Inserting {len(data)} vectors...")
        self.client.insert(collection_name=self.collection_name, data=data)

    def query(self, filter_expr):
        print(f"🔍 Querying collection with filter: {filter_expr}")
        result = self.client.query(collection_name=self.collection_name, filter=filter_expr)
        print("✅ Query Result:", result)
        return result

    def search(self, query_text, limit=10):
        if not self.client.has_collection(self.collection_name):
            raise Exception(f"Collection '{self.collection_name}' does not exist. Please build the vectorstore first.")
        
        print(f"🔍 Searching for: {query_text}")
        query_vector = self._get_embedding(query_text)
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            limit=limit,
            output_fields=["text", "metadata"]
        )
        print(f"📊 Search returned {len(results[0]) if results else 0} results")
        if results and len(results[0]) > 0:
            print(f"🔝 Top result distance: {results[0][0].get('distance', 'N/A')}")
        return results[0] if results else []

    def upsert_vector(self, data):
        print("🔄 Upserting vector...")
        self.client.upsert(collection_name=self.collection_name, data=data)

    def delete_vectors(self, ids):
        print(f"🗑️ Deleting vectors with IDs: {ids}")
        self.client.delete(collection_name=self.collection_name, ids=ids)
