"""
RAG Service for knowledge retrieval
Integrates LiteLLM with Milvus vector store
"""

from typing import List, Dict, Any, Optional
from src.llm.litellm_client import LiteLLMClient
from src.vector_store.milvus_client import MilvusClient

class RAGService:
    def __init__(self):
        """Initialize RAG service with LLM and vector store."""
        self.llm_client = LiteLLMClient()
        self.vector_store = MilvusClient()
        self.vector_store.connect()
    
    def query_visa_requirements(
        self,
        country: str,
        visa_type: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query visa requirements using RAG.
        
        Args:
            country: Destination country
            visa_type: Type of visa
            additional_context: Optional additional context
        
        Returns:
            Dict with requirements and sources
        """
        # Create search query
        query_text = f"Visa requirements for {visa_type} visa to {country}"
        if additional_context:
            query_text += f". {additional_context}"
        
        # Get embedding
        query_embedding = self.llm_client.get_embedding(query_text)
        
        # Search visa requirements collection
        results = self.vector_store.search(
            collection_key="visa_requirements",
            query_embedding=query_embedding,
            top_k=5
        )
        
        # Build context from results
        context = self._build_context(results)
        
        # Generate response using LLM
        prompt = self._create_rag_prompt(query_text, context)
        response = self.llm_client.generate(prompt, model_type="precise")
        
        return {
            "answer": response,
            "sources": [r["metadata"] for r in results],
            "retrieved_chunks": len(results)
        }
    
    def get_embassy_information(
        self,
        country: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get embassy information for a country."""
        query_text = f"Embassy information for {country}"
        if location:
            query_text += f" in {location}"
        
        query_embedding = self.llm_client.get_embedding(query_text)
        
        results = self.vector_store.search(
            collection_key="embassy_info",
            query_embedding=query_embedding,
            top_k=3
        )
        
        context = self._build_context(results)
        prompt = f"""Based on the following information, provide embassy details for {country}:

{context}

Include: address, contact numbers, email, working hours, and application submission process."""
        
        response = self.llm_client.generate(prompt, model_type="precise")
        
        return {
            "information": response,
            "sources": [r["metadata"] for r in results]
        }
    
    def check_immigration_updates(
        self,
        country: str,
        date_from: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check for recent immigration regulation updates."""
        query_text = f"Recent immigration updates and changes for {country}"
        
        query_embedding = self.llm_client.get_embedding(query_text)
        
        filter_expr = None
        if date_from:
            filter_expr = f'metadata["date"] >= "{date_from}"'
        
        results = self.vector_store.search(
            collection_key="regulations",
            query_embedding=query_embedding,
            top_k=10,
            filter_expr=filter_expr
        )
        
        context = self._build_context(results)
        prompt = f"""Summarize recent immigration updates for {country}:

{context}

Focus on: policy changes, new requirements, processing time changes, and important advisories."""
        
        response = self.llm_client.generate(prompt, model_type="primary")
        
        return {
            "updates": response,
            "sources": [r["metadata"] for r in results],
            "count": len(results)
        }
    
    def get_document_template(
        self,
        template_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate document from template using RAG."""
        query_text = f"{template_type} template"
        
        query_embedding = self.llm_client.get_embedding(query_text)
        
        results = self.vector_store.search(
            collection_key="templates",
            query_embedding=query_embedding,
            top_k=1
        )
        
        if not results:
            raise ValueError(f"No template found for {template_type}")
        
        template_context = results[0]["text"]
        
        # Generate personalized document
        prompt = f"""Based on this template:

{template_context}

Generate a personalized document with the following details:
{self._format_context_dict(context)}

Ensure all placeholders are filled and the document is professionally formatted."""
        
        response = self.llm_client.generate(prompt, model_type="primary")
        
        return response
    
    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context string from search results."""
        context_parts = []
        for idx, result in enumerate(results, 1):
            context_parts.append(f"Source {idx}:\n{result['text']}\n")
        return "\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create RAG prompt combining query and context."""
        return f"""Answer the following query based on the provided context. Be specific and cite relevant information.

Query: {query}

Context:
{context}

Answer:"""
    
    def _format_context_dict(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for prompt."""
        return "\n".join([f"- {k}: {v}" for k, v in context.items()])
    
    def __del__(self):
        """Cleanup: disconnect from vector store."""
        if hasattr(self, 'vector_store'):
            self.vector_store.disconnect()

