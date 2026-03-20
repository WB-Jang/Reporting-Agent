"""Application configuration — values are read from environment variables.

Copy `.env.example` to `.env` and fill in the required values, or export
the variables before starting the app.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env if present (silently ignored when missing)

# ---------------------------------------------------------------------------
# NiceGUI server
# ---------------------------------------------------------------------------
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8080"))
APP_TITLE: str = os.getenv("APP_TITLE", "대외기관 보고서 자동화 Agent")
APP_RELOAD: bool = os.getenv("APP_RELOAD", "false").lower() == "true"

# ---------------------------------------------------------------------------
# On-premise OpenAI-compatible LLM endpoint
# ---------------------------------------------------------------------------
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "dummy")   # Not validated on-prem
LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_STREAMING: bool = os.getenv("LLM_STREAMING", "true").lower() == "true"

# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------
CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8001"))
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "report_guidelines")
# Use "http" for a running ChromaDB server; "local" for persistent local DB
CHROMA_MODE: str = os.getenv("CHROMA_MODE", "local")

# ---------------------------------------------------------------------------
# DueDate / Outlook
# ---------------------------------------------------------------------------
DUEDATE_REFRESH_SECONDS: int = int(os.getenv("DUEDATE_REFRESH_SECONDS", "60"))
OUTLOOK_ENABLED: bool = os.getenv("OUTLOOK_ENABLED", "false").lower() == "true"
OUTLOOK_EMAIL: str = os.getenv("OUTLOOK_EMAIL", "")
OUTLOOK_PASSWORD: str = os.getenv("OUTLOOK_PASSWORD", "")
OUTLOOK_SERVER: str = os.getenv("OUTLOOK_SERVER", "")
