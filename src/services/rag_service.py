import os
import yaml
from typing import List, Dict, Any, Optional
from langchain_core.embeddings import Embeddings
from pymilvus import MilvusClient, DataType
from litellm import completion, embedding
import hashlib
 
def load_config():
    """Load config from project root config folder"""
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    config_path = os.path.join(project_root, 'config', 'milvus_config.yaml')
   
    with open(config_path, 'r') as file:
        config_content = file.read()
   
    config_content = os.path.expandvars(config_content)
    return yaml.safe_load(config_content)
 
# Load configuration
config = load_config()
 
# Configuration
LLM_PROVIDER = "azure"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
 
# Azure Configuration
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
 
# Milvus Configuration
MILVUS_URI = config['connection']['uri']
MILVUS_TOKEN = config['connection']['token']
COLLECTION_NAME = config.get('collections', {}).get('visa_kb', {}).get('name', 'default_name')
COLLECTION_DIMENSION = config['collections'].get('visa_kb', {}).get('dimension', 'default_name')
print(COLLECTION_NAME,"collection name in rag services ",config.get('collections', {}) ,COLLECTION_DIMENSION)


class LiteLLMEmbeddings(Embeddings):
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = f"{LLM_PROVIDER}/{model_name}"
   
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            response = embedding(
                model=self.model,
                input=texts,
                **self._get_provider_config()
            )
            return [item['embedding'] for item in response.data]
        except Exception:
            return self._fallback_embeddings(texts)
   
    def embed_query(self, text: str) -> List[float]:
        try:
            response = embedding(
                model=self.model,
                input=[text],
                **self._get_provider_config()
            )
            return response.data[0]['embedding']
        except Exception:
            return self._fallback_embeddings([text])[0]
   
    def _get_provider_config(self) -> Dict[str, Any]:
        if LLM_PROVIDER == "azure":
            return {
                "api_key": AZURE_API_KEY,
                "api_base": AZURE_ENDPOINT,
                "api_version": AZURE_API_VERSION
            }
        return {}
   
    def _fallback_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            hash_obj = hashlib.sha256(text.encode())
            hash_hex = hash_obj.hexdigest()
            embedding = [
                float(int(hash_hex[i:i+2], 16)) / 255.0
                for i in range(0, min(COLLECTION_DIMENSION*2, len(hash_hex)), 2)
            ]
            if len(embedding) < COLLECTION_DIMENSION:
                embedding.extend([0.0] * (COLLECTION_DIMENSION - len(embedding)))
            embeddings.append(embedding[:COLLECTION_DIMENSION])
        return embeddings
 
class RAGService:
    def __init__(self):
        self.llm_model = f"{LLM_PROVIDER}/{LLM_MODEL}"
        self.collection_name = COLLECTION_NAME
        self.collection_dimension = COLLECTION_DIMENSION
        self.vectorstore = None
        self.is_connected = False
        self.client = None
       
        try:
            self.setup_milvus_collection()
            self.setup_vector_store()
            self.load_knowledge_base()
            self.is_connected = True
        except Exception as e:
            print(f"❌ RAG Service initialization failed: {e}")
            self.is_connected = False
 
    def setup_milvus_collection(self):
        self.client = MilvusClient(uri=MILVUS_URI, token=MILVUS_TOKEN)
 
        if not self.client.has_collection(self.collection_name):
            schema = self.client.create_schema(auto_id=True, enable_dynamic_field=True)
            schema.add_field(field_name="pk", datatype=DataType.INT64, is_primary=True, auto_id=True)
            schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.collection_dimension)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="doc_type", datatype=DataType.VARCHAR, max_length=100)
            schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=100)
           
            self.client.create_collection(collection_name=self.collection_name, schema=schema)
 
        self.client.load_collection(collection_name=self.collection_name)
 
    def setup_vector_store(self):
        self.embedding_function = LiteLLMEmbeddings()
       
        try:
            from langchain_milvus import MilvusVectorStore
            self.vectorstore = MilvusVectorStore(
                embedding_function=self.embedding_function,
                collection_name=self.collection_name,
                connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
                auto_id=True
            )
        except ImportError:
            from langchain_community.vectorstores import Milvus
            self.vectorstore = Milvus(
                embedding_function=self.embedding_function,
                collection_name=self.collection_name,
                connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
                auto_id=True
            )
 
    def load_knowledge_base(self):
        if self.get_document_count() > 0:
            return
 
        visa_documents = [
            "USA visa requires passport valid for 6 months, DS-160 form, and interview appointment",
            "UK visa requires biometric enrollment, financial proof, and accommodation details",
            "Schengen visa needs travel insurance covering 30,000 EUR and flight itinerary",
            "Business visa requires invitation letter from host company and company NOC",
            "Student visa needs admission letter and financial capability proof",
            "Tourist visa processing time is typically 15-30 working days",
            "Visa fees vary by country: USA $185, UK £115, Schengen €80",
            "Document checklist: passport photos, bank statements, employment verification",
            "Emergency visa processing available with additional fees and valid reasons",
            "Visa extension possible for valid reasons with proper documentation",
            "USA embassy in New Delhi: Shantipath, Chanakyapuri, New Delhi 110021, contact: +91-11-2419-8000",
            "UK embassy in Delhi: Shantipath, Chanakyapuri, New Delhi 110021, contact: +91-11-2419-2100",
            "Schengen visa application center in Delhi: DLF Corporate Park, Gurugram",
            "Recent update: USA introduced new visa fees effective January 2024",
            "UK updated biometric requirements for all visa categories in December 2023",
            "Work visa for USA requires H1B approval, valid job offer, and specialized occupation",
            "Canada work permit needs LMIA approval and job offer from Canadian employer",
            "Australia work visa categories include TSS 482, ENS 186, and working holiday visas",
            "Germany Blue Card for highly skilled workers requires salary threshold of €56,800",
            "Singapore Employment Pass needs monthly salary of SGD 5,000 minimum"
        ]
 
        metadata = [{"doc_type": "visa_requirement", "source": "immigration_db"} for _ in visa_documents]
        self.vectorstore.add_texts(texts=visa_documents, metadatas=metadata)
 
    def add_documents(self, documents: List[str], metadata: List[Dict] = None) -> bool:
        try:
            if not self.is_connected:
                return False
 
            if metadata is None:
                metadata = [{"source": "uploaded", "doc_type": "general"} for _ in documents]
 
            if len(documents) != len(metadata):
                return False
 
            self.vectorstore.add_texts(texts=documents, metadatas=metadata)
            return True
        except Exception:
            return False
 
    def _get_llm_config(self) -> Dict[str, Any]:
        if LLM_PROVIDER == "azure":
            return {
                "api_key": AZURE_API_KEY,
                "api_base": AZURE_ENDPOINT,
                "api_version": AZURE_API_VERSION
            }
        return {}
 
    def generate_completion(self, messages: List[Dict], **kwargs) -> Any:
        llm_config = self._get_llm_config()
        llm_config.update(kwargs)
        return completion(model=self.llm_model, messages=messages, **llm_config)
 
    def get_document_count(self) -> int:
        try:
            stats = self.client.get_collection_stats(self.collection_name)
            return stats.get('row_count', 0)
        except Exception:
            return 0
 
    def retrieve_relevant_info(self, query: str, k: int = 3):
        if not self.is_connected:
            return []
       
        query = self._clean_query(query)
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        return retriever.invoke(query)
 
    def generate_response(self, query: str, context_docs: Optional[List] = None) -> Dict[str, Any]:
        query = self._clean_query(query)
       
        if not self.is_connected:
            return {"answer": "RAG service unavailable", "sources": [], "tokens_used": 0}
 
        if context_docs is None:
            context_docs = self.retrieve_relevant_info(query)
 
        context = "\n".join([doc.page_content for doc in context_docs])
        prompt = f"""You are a professional Visa Desk Assistant. Answer based ONLY on this context:
 
{context}
 
Question: {query}
 
Provide clear, structured answer about visa requirements. If information not in context, say so."""
 
        try:
            response = self.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
 
            return {
                "answer": response.choices[0].message.content,
                "sources": context_docs,
                "tokens_used": response.usage.total_tokens,
                "model": LLM_MODEL,
                "provider": LLM_PROVIDER
            }
        except Exception:
            fallback_answer = "Based on available information:\n\n" + "\n".join(
                [f"• {doc.page_content}" for doc in context_docs[:3]]
            ) if context_docs else "I don't have specific information about this."
           
            return {
                "answer": fallback_answer,
                "sources": context_docs,
                "tokens_used": 0,
                "model": "fallback",
                "provider": "fallback"
            }
 
    def _clean_query(self, query):
        """Extract query string from SearchRequest objects and clean it"""
        if hasattr(query, 'query'):
            query = query.query
        elif not isinstance(query, str):
            query = str(query)
        return query.strip()
 
    def query_visa_requirements(self, country: str, visa_type: str, additional_context: str = None) -> Dict[str, Any]:
        query_text = f"Visa requirements for {visa_type} visa to {country}"
        if additional_context:
            query_text += f". {additional_context}"
 
        result = self.generate_response(query_text)
        return {
            "answer": result["answer"],
            "sources": [{"content": doc.page_content, "metadata": doc.metadata} for doc in result["sources"]],
            "retrieved_chunks": len(result["sources"]),
            "tokens_used": result.get("tokens_used", 0),
            "model_used": result.get("model", "unknown"),
            "provider_used": result.get("provider", "unknown")
        }
 
    def health_check(self) -> Dict[str, Any]:
        try:
            count = self.get_document_count()
            return {
                "connected": self.is_connected,
                "vector_store_ready": self.vectorstore is not None,
                "documents_loaded": count,
                "collection_name": self.collection_name,
                "llm_provider": LLM_PROVIDER,
                "llm_model": LLM_MODEL,
                "embedding_model": EMBEDDING_MODEL
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}