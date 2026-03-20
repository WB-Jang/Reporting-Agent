"""Chat window component.

Handles all three chat modes:
  1. FREE_CHAT  — direct LLM streaming conversation
  2. RAG_QUERY  — ChromaDB retrieval + LLM answer
  3. REPORT_EXEC — interactive parameter collection → report execution
"""

from __future__ import annotations

import asyncio
import threading
from typing import List, Tuple

from nicegui import ui, run

from app.models.chat_models import ChatMessage, ChatMode, MessageRole, ReportExecState
from app.models.report_models import REPORT_CATALOG, ReportMeta
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ChatWindow:
    """Full chat UI with mode-aware message dispatch."""

    def __init__(self) -> None:
        self._messages: List[ChatMessage] = []
        self._mode: ChatMode = ChatMode.FREE_CHAT
        self._exec_state: ReportExecState | None = None
        self._scroll_area: ui.scroll_area | None = None
        self._messages_col: ui.column | None = None
        self._input: ui.input | None = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def mode(self) -> ChatMode:
        return self._mode

    def set_mode(self, mode: ChatMode, report_id: str | None = None) -> None:
        """Switch chat mode; optionally start a report execution flow."""
        self._mode = mode
        self._exec_state = None

        if mode == ChatMode.REPORT_EXEC and report_id:
            meta = REPORT_CATALOG.get(report_id)
            if meta is None:
                self._add_message(MessageRole.SYSTEM, f"⚠️ 알 수 없는 보고서 ID: {report_id}")
                return
            params = [p.name for p in meta.required_params]
            self._exec_state = ReportExecState(
                report_id=report_id,
                required_params=params.copy(),
            )
            self._add_message(
                MessageRole.SYSTEM,
                f"**{meta.label}** 보고서 작성 모드로 전환되었습니다.",
            )
            self._ask_next_param(meta)
        elif mode == ChatMode.RAG_QUERY:
            self._add_message(MessageRole.SYSTEM, "📚 RAG 질의 모드입니다. 보고서 관련 질문을 입력하세요.")
        else:
            self._add_message(MessageRole.SYSTEM, "💬 자유대화 모드입니다.")

    def build(self) -> None:
        """Render the chat window inside the current NiceGUI layout context."""
        with ui.card().classes("w-full flex-grow flex flex-col").style("height:100%"):
            ui.label("💬 채팅").classes("text-subtitle1 text-bold q-mb-sm")
            with ui.scroll_area().classes("flex-grow w-full").style("height:calc(100% - 80px)") as sa:
                self._scroll_area = sa
                self._messages_col = ui.column().classes("w-full gap-2 q-pa-sm")

            with ui.row().classes("w-full items-center gap-2 q-pt-sm"):
                self._input = (
                    ui.input(placeholder="메시지를 입력하세요…")
                    .classes("flex-grow")
                    .on("keydown.enter", self._on_send)
                )
                ui.button(icon="send", on_click=self._on_send).props("color=primary round")

        # Welcome message
        self._add_message(MessageRole.SYSTEM, "안녕하세요! 무엇을 도와드릴까요?")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add_message(self, role: MessageRole, content: str) -> None:
        """Append a message and render it."""
        msg = ChatMessage(role=role, content=content, mode=self._mode)
        self._messages.append(msg)
        self._render_message(msg)
        self._scroll_to_bottom()

    def _render_message(self, msg: ChatMessage) -> None:
        """Add a single chat bubble to the message column."""
        if self._messages_col is None:
            return
        with self._messages_col:
            sent = msg.role == MessageRole.USER
            name_map = {
                MessageRole.USER: "나",
                MessageRole.ASSISTANT: "Agent",
                MessageRole.SYSTEM: "System",
            }
            ui.chat_message(
                text=msg.content,
                name=name_map[msg.role],
                sent=sent,
                stamp="",
            ).props("bg-color=" + ("blue-2" if sent else "grey-3"))

    def _scroll_to_bottom(self) -> None:
        if self._scroll_area:
            self._scroll_area.scroll_to(percent=1.0)

    def _on_send(self) -> None:
        """Handle send-button click or Enter key."""
        if self._input is None:
            return
        text = (self._input.value or "").strip()
        if not text:
            return
        self._input.value = ""
        self._add_message(MessageRole.USER, text)
        asyncio.create_task(self._dispatch(text))

    async def _dispatch(self, user_text: str) -> None:
        """Route the user message to the appropriate handler."""
        if self._mode == ChatMode.REPORT_EXEC and self._exec_state is not None:
            await self._handle_report_exec(user_text)
        elif self._mode == ChatMode.RAG_QUERY:
            await self._handle_rag(user_text)
        else:
            await self._handle_free_chat(user_text)

    # ------------------------------------------------------------------
    # Mode handlers
    # ------------------------------------------------------------------

    async def _handle_free_chat(self, user_text: str) -> None:
        """Stream a free-chat LLM response."""
        from app.services.chat_service import stream_chat

        history: List[Tuple[str, str]] = [
            (m.role.value, m.content)
            for m in self._messages[:-1]
            if m.role in (MessageRole.USER, MessageRole.ASSISTANT)
        ]
        await self._stream_to_chat(lambda: stream_chat(user_text, history))

    async def _handle_rag(self, user_text: str) -> None:
        """Stream a RAG-augmented LLM response."""
        from app.services.rag_service import query_rag

        await self._stream_to_chat(lambda: query_rag(user_text))

    async def _handle_report_exec(self, user_text: str) -> None:
        """Collect parameters one by one, then run the report."""
        state = self._exec_state
        if state is None:
            return

        meta = REPORT_CATALOG.get(state.report_id)
        if meta is None:
            return

        # Store the answer for the current parameter
        if state.current_param:
            state.collected_params[state.current_param] = user_text
            state.required_params = [p for p in state.required_params if p != state.current_param]
            state.current_param = None

        if state.required_params:
            self._ask_next_param(meta)
        else:
            # All params collected — run the report
            state.is_complete = True
            await self._run_report(meta, state.collected_params)

    def _ask_next_param(self, meta: ReportMeta) -> None:
        """Ask the user for the next required parameter."""
        state = self._exec_state
        if state is None or not state.required_params:
            return

        param_name = state.required_params[0]
        state.current_param = param_name

        # Find the ParamSpec for display
        spec = next((p for p in meta.required_params if p.name == param_name), None)
        if spec:
            prompt = spec.prompt
            if spec.example:
                prompt += f" (예: {spec.example})"
        else:
            prompt = f"**{param_name}** 값을 입력해 주세요."

        self._add_message(MessageRole.ASSISTANT, prompt)

    async def _run_report(self, meta: ReportMeta, params: dict) -> None:
        """Execute the report with collected params, streaming progress."""
        from app.services.report_runner import ReportRunner

        # Placeholder for the streaming assistant bubble
        if self._messages_col is None:
            return

        progress_messages: list[str] = []
        bubble_label: ui.label | None = None

        with self._messages_col:
            with ui.chat_message(name="Agent", sent=False).props("bg-color=grey-3"):
                bubble_label = ui.label("").classes("whitespace-pre-wrap")

        def on_progress(msg: str) -> None:
            progress_messages.append(msg)
            if bubble_label is not None:
                bubble_label.set_text("\n".join(progress_messages))
            self._scroll_to_bottom()

        runner = ReportRunner(meta, params, on_progress=on_progress)
        try:
            await run.io_bound(runner.run)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Report execution error: %s", exc)
            self._add_message(MessageRole.SYSTEM, f"⚠️ 보고서 실행 중 오류 발생: {exc}")
        finally:
            self._exec_state = None
            self._mode = ChatMode.FREE_CHAT

    async def _stream_to_chat(self, gen_factory) -> None:
        """Create an assistant bubble and populate it with streamed tokens.

        The generator is consumed inside a thread (via ``run.io_bound``) so
        that blocking I/O does not freeze the NiceGUI event loop.  The UI
        label is updated after each yielded token.
        """
        if self._messages_col is None:
            return

        bubble_label: ui.label | None = None
        with self._messages_col:
            with ui.chat_message(name="Agent", sent=False).props("bg-color=grey-3"):
                bubble_label = ui.label("⏳").classes("whitespace-pre-wrap")

        accumulated = ""

        def _collect_tokens() -> list[str]:
            """Run the generator synchronously and return its tokens."""
            return list(gen_factory())

        try:
            token_list: list[str] = await run.io_bound(_collect_tokens)
            for token in token_list:
                accumulated += token
                if bubble_label is not None:
                    bubble_label.set_text(accumulated)
                self._scroll_to_bottom()
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Streaming error: %s", exc)
            accumulated += f"\n\n⚠️ 오류: {exc}"

        if bubble_label is not None and not accumulated:
            bubble_label.set_text("(응답 없음)")
        elif bubble_label is not None:
            bubble_label.set_text(accumulated)

        if accumulated:
            self._messages.append(
                ChatMessage(role=MessageRole.ASSISTANT, content=accumulated, mode=self._mode)
            )
