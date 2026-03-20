"""RAG query service — ChromaDB retrieval + LLM answer.

Falls back gracefully when ChromaDB or the LLM is unavailable.
"""

from __future__ import annotations

from typing import Generator
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Optional dependency ---------------------------------------------------------
try:
    import chromadb  # type: ignore
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False
    logger.warning("chromadb is not installed — RAG features disabled.")

_chroma_client = None  # lazy singleton


def _get_chroma_client():
    """Return a ChromaDB client (lazy singleton)."""
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client

    if not _CHROMA_AVAILABLE:
        return None

    from app import config
    from app.utils.paths import VECTOR_DB_DIR

    try:
        if config.CHROMA_MODE == "http":
            _chroma_client = chromadb.HttpClient(
                host=config.CHROMA_HOST, port=config.CHROMA_PORT
            )
        else:
            _chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        logger.info("ChromaDB client initialised (mode=%s)", config.CHROMA_MODE)
        return _chroma_client
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Failed to connect to ChromaDB: %s", exc)
        return None


def query_rag(user_question: str, n_results: int = 3) -> Generator[str, None, None]:
    """Retrieve relevant documents and stream an LLM answer.

    Parameters
    ----------
    user_question:
        The user's question text.
    n_results:
        Number of document chunks to retrieve from ChromaDB.

    Yields
    ------
    str
        Token chunks forming the final answer.
    """
    from app import config
    from app.services.llm_client import get_llm_client

    chroma = _get_chroma_client()
    context_text = ""

    if chroma is None:
        yield "⚠️ ChromaDB에 연결할 수 없습니다. RAG 기능을 사용하려면 vectordb를 먼저 구성하세요.\n\n"
        # Fall through to LLM-only answer
    else:
        try:
            collection = chroma.get_or_create_collection(config.CHROMA_COLLECTION)
            results = collection.query(query_texts=[user_question], n_results=n_results)
            docs = results.get("documents", [[]])[0]
            if docs:
                context_text = "\n\n".join(docs)
                logger.info("RAG retrieved %d document(s)", len(docs))
            else:
                yield "ℹ️ 관련 문서를 찾지 못했습니다. 일반 답변을 제공합니다.\n\n"
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("ChromaDB query error: %s", exc)
            yield f"⚠️ ChromaDB 조회 중 오류 발생: {exc}\n\n"

    # Build LLM prompt with or without context --------------------------------
    client = get_llm_client()
    if client is None:
        yield "[LLM 미연결] 질문을 받았으나 LLM 엔드포인트에 연결할 수 없습니다."
        return

    try:
        from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore

        system_content = (
            "당신은 보고서 작성 전문가입니다. 아래 참고 자료를 바탕으로 질문에 답변하세요. "
            "참고 자료가 없는 경우 일반 지식으로 답변하세요."
        )
        if context_text:
            system_content += f"\n\n[참고 자료]\n{context_text}"

        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_question),
        ]
        for chunk in client.stream(messages):
            token = chunk.content
            if token:
                yield token
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("RAG LLM streaming error: %s", exc)
        yield f"\n\n⚠️ LLM 응답 중 오류 발생: {exc}"
