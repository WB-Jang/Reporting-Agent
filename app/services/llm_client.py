"""Singleton LLM client using langchain-openai (ChatOpenAI).

Falls back gracefully when the package or the endpoint is unavailable.
"""

from __future__ import annotations

from typing import Optional
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Optional dependency ---------------------------------------------------------
try:
    from langchain_openai import ChatOpenAI  # type: ignore
    _LANGCHAIN_AVAILABLE = True
except ImportError:
    _LANGCHAIN_AVAILABLE = False
    logger.warning("langchain-openai is not installed — LLM features disabled.")

_client: Optional[object] = None  # ChatOpenAI instance (lazy singleton)


def get_llm_client():
    """Return the shared ChatOpenAI instance, or None if unavailable."""
    global _client
    if _client is not None:
        return _client

    if not _LANGCHAIN_AVAILABLE:
        return None

    from app import config

    try:
        _client = ChatOpenAI(
            base_url=config.LLM_BASE_URL,
            api_key=config.LLM_API_KEY,
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
            streaming=config.LLM_STREAMING,
        )
        logger.info("LLM client initialised (model=%s, url=%s)", config.LLM_MODEL, config.LLM_BASE_URL)
        return _client
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Failed to create LLM client: %s", exc)
        return None


def reset_client() -> None:
    """Reset the singleton (useful for config changes or testing)."""
    global _client
    _client = None
