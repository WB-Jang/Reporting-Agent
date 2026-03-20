"""Free-chat service — streams tokens from the on-premise LLM.

When the LLM is unavailable a simple echo/fallback message is yielded instead
so that the UI always receives some response.
"""

from __future__ import annotations

from typing import Generator
from app.utils.logging import get_logger

logger = get_logger(__name__)

_FALLBACK_PREFIX = "[LLM 미연결] 현재 LLM 엔드포인트에 접근할 수 없습니다. 입력하신 내용: "


def stream_chat(user_message: str, history: list | None = None) -> Generator[str, None, None]:
    """Yield response tokens for *user_message*.

    Parameters
    ----------
    user_message:
        The latest user input.
    history:
        Optional list of previous ``(role, content)`` tuples for context.

    Yields
    ------
    str
        Successive token/chunk strings to be appended to the assistant reply.
    """
    from app.services.llm_client import get_llm_client

    client = get_llm_client()
    if client is None:
        yield _FALLBACK_PREFIX + user_message
        return

    # Build message list for ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage  # type: ignore

    messages = [
        SystemMessage(content="당신은 업무 보고서 자동화를 돕는 AI 어시스턴트입니다. 친절하고 정확하게 답변하세요.")
    ]
    for role, content in (history or []):
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=user_message))

    try:
        for chunk in client.stream(messages):
            token = chunk.content
            if token:
                yield token
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("LLM streaming error: %s", exc)
        yield f"\n\n⚠️ LLM 응답 중 오류가 발생했습니다: {exc}"
