"""Policy Retrieval Tool - Integration for travel agent."""

from __future__ import annotations

from src.rag.retrieval.policy_qa import get_policy_qa


def query_travel_policy(question: str) -> str:
    """
    Query travel policy documents for policy-related questions.

    Args:
        question: Question about travel policies

    Returns:
        Answer with relevant policy information
    """
    try:
        qa_system = get_policy_qa()
        result = qa_system.query(question)

        # Format result for tool output
        answer = result.get("answer", "No answer generated")
        sources = result.get("sources", [])

        formatted_output = f"📋 Answer: {answer}\n\n"

        if sources:
            formatted_output += "📚 Policy Sources:\n"
            for i, source in enumerate(sources, 1):
                metadata = source.get("metadata", "Policy")
                score = source.get("score", 0)
                text_preview = source.get("text", "")[:100]
                formatted_output += f"  {i}. [{metadata}] (Relevance: {score:.2%})\n"
                formatted_output += f"     {text_preview}...\n"

        return formatted_output

    except Exception as e:
        return f"❌ Error querying policy: {str(e)}"


# Define as a tool dictionary for LangGraph
POLICY_RETRIEVAL_TOOL = {
    "name": "query_travel_policy",
    "description": "Query travel policy documents to answer policy-related questions. Use this for questions about entitlements, allowances, rules, and procedures.",
    "function": query_travel_policy,
}


__all__ = ["query_travel_policy", "POLICY_RETRIEVAL_TOOL"]
