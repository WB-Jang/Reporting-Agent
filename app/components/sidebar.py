"""Left sidebar component.

Provides:
  - Report execution buttons (one per entry in REPORT_CATALOG)
  - Chat mode toggle buttons (Free chat / RAG / Report)
  - File upload / manager panel
"""

from __future__ import annotations

from nicegui import ui

from app.models.chat_models import ChatMode
from app.models.report_models import REPORT_CATALOG
from app.utils.logging import get_logger

logger = get_logger(__name__)


class Sidebar:
    """Renders the left drawer content and wires mode-change callbacks."""

    def __init__(self, chat_window) -> None:
        """
        Parameters
        ----------
        chat_window:
            The :class:`~app.components.chat_window.ChatWindow` instance
            whose :meth:`set_mode` will be called on user interactions.
        """
        self._chat = chat_window
        self._mode_label: ui.badge | None = None

    def build(self) -> None:
        """Render the sidebar content inside the current layout context."""
        # ── Report buttons ─────────────────────────────────────────────
        ui.label("📊 보고서 작성").classes("text-subtitle2 text-bold q-mb-xs")
        with ui.column().classes("w-full gap-1"):
            for report_id, meta in REPORT_CATALOG.items():
                ui.button(
                    meta.label,
                    on_click=lambda rid=report_id: self._start_report(rid),
                ).classes("w-full").props("color=primary unelevated")

        ui.separator().classes("q-my-md")

        # ── Mode toggle ────────────────────────────────────────────────
        ui.label("🔧 채팅 모드").classes("text-subtitle2 text-bold q-mb-xs")
        with ui.column().classes("w-full gap-1"):
            ui.button(
                "💬 자유대화",
                on_click=lambda: self._set_mode(ChatMode.FREE_CHAT),
            ).classes("w-full").props("color=secondary outline")
            ui.button(
                "📚 RAG 질의",
                on_click=lambda: self._set_mode(ChatMode.RAG_QUERY),
            ).classes("w-full").props("color=secondary outline")

        ui.separator().classes("q-my-md")

        # ── File manager ───────────────────────────────────────────────
        from app.components.file_manager import FileManager

        FileManager().build()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _start_report(self, report_id: str) -> None:
        logger.info("Starting report: %s", report_id)
        self._chat.set_mode(ChatMode.REPORT_EXEC, report_id=report_id)

    def _set_mode(self, mode: ChatMode) -> None:
        logger.info("Switching chat mode to: %s", mode)
        self._chat.set_mode(mode)
