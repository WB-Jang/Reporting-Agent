"""Home page — main layout composition.

Assembles the header, left drawer, and main content area using
:class:`~app.components.dashboard.DueDateDashboard` and
:class:`~app.components.chat_window.ChatWindow`.
"""

from __future__ import annotations

from nicegui import ui

from app.components.chat_window import ChatWindow
from app.components.dashboard import DueDateDashboard
from app.components.sidebar import Sidebar
from app import config


def build_home_page() -> None:
    """Register and render the home page at the root URL ``/``."""

    @ui.page("/")
    def home() -> None:
        ui.query("body").style("margin:0; overflow:hidden;")

        # ── Header ────────────────────────────────────────────────────
        with ui.header(elevated=True).classes("items-center justify-between"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("description").classes("text-h5")
                ui.label(config.APP_TITLE).classes("text-h6 text-bold")
            ui.space()
            ui.label("대외기관 보고서 자동화 시스템").classes("text-caption text-grey-4")

        # ── Left drawer ───────────────────────────────────────────────
        chat = ChatWindow()

        with ui.left_drawer(value=True, bordered=True).classes(
            "bg-grey-1 q-pa-md"
        ).style("width:280px; overflow-y:auto;"):
            Sidebar(chat).build()

        # ── Main content ──────────────────────────────────────────────
        with ui.column().classes("w-full q-pa-md gap-4").style(
            "height:calc(100vh - 64px); overflow:hidden;"
        ):
            # Top: DueDate dashboard
            DueDateDashboard().build()

            # Bottom: Chat window (flex-grow to fill remaining space)
            with ui.column().classes("flex-grow w-full").style(
                "min-height:0; overflow:hidden;"
            ):
                chat.build()
