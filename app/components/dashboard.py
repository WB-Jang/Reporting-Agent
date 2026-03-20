"""DueDate alert dashboard component.

Renders DueDate alert cards in a column and registers a ``ui.timer``
that refreshes the data at the interval configured in ``config.py``.
"""

from __future__ import annotations

from nicegui import ui
from app.models.duedate_models import AlertLevel, DueDateEntry
from app.services import duedate_service
from app import config
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Alert level display config
_LEVEL_CONFIG = {
    AlertLevel.D1: ("🔴", "negative", "D-1 (긴급)"),
    AlertLevel.D3: ("🟡", "warning", "D-3 (주의)"),
    AlertLevel.D7: ("🟢", "positive", "D-7 (예정)"),
    AlertLevel.NONE: ("⚪", "grey-5", ""),
}


class DueDateDashboard:
    """Renders and periodically refreshes DueDate alert cards."""

    def __init__(self) -> None:
        self._container: ui.column | None = None
        self._entries: list[DueDateEntry] = []

    def build(self) -> None:
        """Render the dashboard inside the current NiceGUI layout context."""
        with ui.card().classes("w-full q-mb-md"):
            ui.label("📅 DueDate 알람").classes("text-subtitle1 text-bold q-mb-sm")
            self._container = ui.column().classes("w-full gap-2")
            self._refresh()

        # Periodic refresh timer
        ui.timer(
            config.DUEDATE_REFRESH_SECONDS,
            callback=self._refresh,
        )

    def _refresh(self) -> None:
        """Reload due dates and redraw the alert cards."""
        if self._container is None:
            return
        self._container.clear()
        self._entries = duedate_service.load_due_dates()
        alerts = duedate_service.get_active_alerts(self._entries)

        with self._container:
            if not alerts:
                ui.label("현재 D-7 이내의 마감 일정이 없습니다.").classes("text-grey-6 text-caption")
                return

            for entry in sorted(alerts, key=lambda e: e.days_remaining):
                icon, color, level_label = _LEVEL_CONFIG[entry.alert_level]
                days = entry.days_remaining
                days_text = f"D-{days}" if days >= 0 else f"D+{abs(days)} (기한 초과)"

                with ui.card().classes(f"w-full bg-{color} text-white q-pa-sm"):
                    with ui.row().classes("items-center gap-2 no-wrap"):
                        ui.label(icon).classes("text-lg")
                        with ui.column().classes("gap-0"):
                            ui.label(entry.report_label).classes("text-body2 text-bold")
                            ui.label(
                                f"{level_label}  |  마감: {entry.due_date.isoformat()}  ({days_text})"
                            ).classes("text-caption")
