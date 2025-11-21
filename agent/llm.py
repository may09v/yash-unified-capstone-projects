"""LLM factory helpers based on ChatLiteLLM and Azure OpenAI."""

from __future__ import annotations

import litellm
from langchain_litellm import ChatLiteLLM

from src.config.settings import settings

# Azure OpenAI may reject unsupported OpenAI-only params. This flag makes
# LiteLLM strip anything the backend cannot understand automatically.
litellm.drop_params = True


def create_llm() -> ChatLiteLLM:
    """Instantiate a configured ChatLiteLLM client."""

    return ChatLiteLLM(
        model=settings.AZURE_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        verbose=settings.LLM_VERBOSE,
    )


def get_llm() -> ChatLiteLLM:
    """Return a singleton LLM instance for reuse across requests."""

    if not hasattr(get_llm, "_instance"):
        get_llm._instance = create_llm()
    return get_llm._instance  # type: ignore[attr-defined]


__all__ = ["get_llm", "create_llm"]
