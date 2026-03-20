"""Chat-related data models."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class ChatMode(str, Enum):
    """Operating mode of the chat window."""

    FREE_CHAT = "free_chat"        # Free conversation with the LLM
    RAG_QUERY = "rag_query"        # RAG-based document retrieval + LLM answer
    REPORT_EXEC = "report_exec"    # Interactive report execution mode


class MessageRole(str, Enum):
    """Sender role of a chat message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """A single message in the chat history."""

    role: MessageRole
    content: str
    mode: ChatMode = ChatMode.FREE_CHAT
    metadata: dict = field(default_factory=dict)  # e.g. report_id, step


@dataclass
class ReportExecState:
    """State tracker for interactive report execution."""

    report_id: str
    required_params: list  # list of param names still to collect
    collected_params: dict = field(default_factory=dict)
    current_param: Optional[str] = None
    is_complete: bool = False
