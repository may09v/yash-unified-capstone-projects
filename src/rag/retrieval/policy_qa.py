# File: /src/rag/retrieval/policy_qa.py
# Location: src/rag/retrieval/
# Description: Policy QA - Question answering using RAG with policy documents

"""Policy QA - Question answering using RAG with policy documents."""

from __future__ import annotations

from typing import Optional, Union, Dict, Any

from langchain_core.messages import HumanMessage
from agent.llm import get_llm
from src.rag.embeddings.gemini_embedder import get_embedder
from src.rag.retrieval.milvus_retriever import get_retriever
from src.rag.config.rag_config import rag_settings


class PolicyQA:
    """
    Question Answering system for travel policies using RAG.
    
    Retrieves relevant policy documents and generates answers using LLM.
    """

    def __init__(self):
        """Initialize QA system with embedder and retriever."""
        self.embedder = get_embedder()
        self.retriever = get_retriever()

    def query(self, question: str, use_context: bool = True) -> dict:
        """
        Answer a question about travel policies.

        Args:
            question: User question about policies
            use_context: Whether to use RAG context (True) or direct LLM (False)

        Returns:
            Dictionary with 'answer', 'sources', and 'raw_results'
        """
        try:
            print(f"❓ Question: {question}")

            # Step 1: Generate query embedding
            query_embedding = self.embedder.embed_query(question)

            # Step 2: Retrieve relevant documents
            search_results = self.retriever.search(query_embedding)

            if not search_results:
                print("❌ No relevant documents found in database.")
                context_text = "No matching policy information found."
                sources = []
            else:
                context_text = "\n\n".join(
                    [
                        f"[{self._format_metadata_reference(r['metadata'])}] {r['text']}"
                        for r in search_results
                    ]
                )
                sources = [
                    {
                        "text": r["text"][:100] + "...",
                        "metadata": r["metadata"],
                        "reference": self._format_metadata_reference(r["metadata"]),
                        "score": r["score"],
                    }
                    for r in search_results
                ]
                print(f"🔎 Found {len(search_results)} relevant context chunks.")

            # Step 3: Generate answer using LLM
            answer = self._generate_answer(question, context_text, use_context)

            return {
                "answer": answer,
                "sources": sources,
                "raw_results": search_results,
                "question": question,
                "used_context": use_context,
            }

        except Exception as e:
            print(f"❌ Error during query: {str(e)}")
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "raw_results": [],
                "question": question,
                "used_context": use_context,
                "error": str(e),
            }

    def _generate_answer(self, question: str, context: str, use_rag: bool = True) -> str:
        """
        Generate answer using ChatLiteLLM (configured LLM) with RAG-specific temperature.

        Args:
            question: User question
            context: Retrieved context from RAG
            use_rag: Whether to use RAG context

        Returns:
            Generated answer
        """
        if use_rag:
            prompt = f"""You are a helpful travel policy assistant. Use ONLY the context below to answer the user's question.
If the answer is not in the context, politely say "I don't have that information in the policy documents."

CONTEXT FROM POLICY:
{context}

USER QUESTION:
{question}

ANSWER:"""
        else:
            prompt = f"""You are a helpful travel policy assistant.

USER QUESTION:
{question}

ANSWER:"""

        try:
            llm = get_llm()
            
            # Override temperature for RAG queries with lower value for more factual responses
            if use_rag and hasattr(llm, 'temperature'):
                original_temp = llm.temperature
                llm.temperature = rag_settings.RAG_TEMPERATURE
            
            message = HumanMessage(content=prompt)
            response = llm.invoke([message])
            answer = response.content
            
            # Restore original temperature
            if use_rag and hasattr(llm, 'temperature'):
                llm.temperature = original_temp
            
            return answer

        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def query_without_rag(self, question: str) -> dict:
        """
        Answer a question using only LLM without RAG context.

        Args:
            question: User question

        Returns:
            Dictionary with answer (no sources)
        """
        return self.query(question, use_context=False)

    @staticmethod
    def _format_metadata_reference(metadata: Union[str, Dict[str, Any]]) -> str:
        """Return a human-readable tag for a chunk's metadata."""
        if isinstance(metadata, dict):
            parts = []
            source = metadata.get("source") or metadata.get("filename")
            if source:
                parts.append(str(source))
            summary = metadata.get("chunk_summary")
            if summary:
                parts.append(summary)
            region = metadata.get("country_or_region")
            if region:
                parts.append(f"Region: {region}")
            grades = metadata.get("employee_grades")
            if grades:
                grade_list = ", ".join(str(g) for g in grades if g)
                if grade_list:
                    parts.append(f"Grades: {grade_list}")
            topics = metadata.get("topics") or metadata.get("keywords")
            if topics:
                topic_list = ", ".join(str(t) for t in topics[:3])
                if topic_list:
                    parts.append(f"Topics: {topic_list}")
            return " | ".join(parts) if parts else "policy"
        return str(metadata or "policy")


# Global QA instance (lazy loaded)
_qa_instance: Optional[PolicyQA] = None


def get_policy_qa() -> PolicyQA:
    """Get or create global PolicyQA instance."""
    global _qa_instance
    if _qa_instance is None:
        _qa_instance = PolicyQA()
    return _qa_instance


__all__ = ["PolicyQA", "get_policy_qa"]
