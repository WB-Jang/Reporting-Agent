"""DueDate service — loads/saves due_dates.json and computes alerts.

Outlook scanning is provided as a stub; enable it by setting
``OUTLOOK_ENABLED=true`` and supplying credentials in the environment.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import List
from app.models.duedate_models import DueDateEntry, AlertLevel
from app.utils.paths import DUE_DATES_FILE, SCHEDULER_DIR
from app.utils.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# JSON serialisation helpers
# ---------------------------------------------------------------------------

def _entry_to_dict(entry: DueDateEntry) -> dict:
    return {
        "report_id": entry.report_id,
        "report_label": entry.report_label,
        "due_date": entry.due_date.isoformat(),
        "source": entry.source,
        "note": entry.note,
        "alerts_sent": entry.alerts_sent,
    }


def _dict_to_entry(data: dict) -> DueDateEntry:
    return DueDateEntry(
        report_id=data["report_id"],
        report_label=data["report_label"],
        due_date=date.fromisoformat(data["due_date"]),
        source=data.get("source", "manual"),
        note=data.get("note", ""),
        alerts_sent=data.get("alerts_sent", {"d7": False, "d3": False, "d1": False}),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_due_dates() -> List[DueDateEntry]:
    """Load all DueDate entries from ``due_dates.json``."""
    SCHEDULER_DIR.mkdir(parents=True, exist_ok=True)
    if not DUE_DATES_FILE.exists():
        return []
    try:
        with DUE_DATES_FILE.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        return [_dict_to_entry(d) for d in raw]
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("Failed to load due_dates.json: %s", exc)
        return []


def save_due_dates(entries: List[DueDateEntry]) -> None:
    """Persist *entries* to ``due_dates.json``."""
    SCHEDULER_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with DUE_DATES_FILE.open("w", encoding="utf-8") as fh:
            json.dump([_entry_to_dict(e) for e in entries], fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        logger.error("Failed to save due_dates.json: %s", exc)


def get_active_alerts(entries: List[DueDateEntry]) -> List[DueDateEntry]:
    """Return only entries whose alert level is not NONE."""
    return [e for e in entries if e.alert_level != AlertLevel.NONE]


def add_or_update_entry(entries: List[DueDateEntry], new_entry: DueDateEntry) -> List[DueDateEntry]:
    """Add a new entry or update an existing one with the same ``report_id``."""
    updated = [e for e in entries if e.report_id != new_entry.report_id]
    updated.append(new_entry)
    return updated


# ---------------------------------------------------------------------------
# Outlook stub
# ---------------------------------------------------------------------------

def scan_outlook_for_due_dates() -> List[DueDateEntry]:
    """Scan Outlook mailbox for report due-date emails.

    This is a **stub** implementation.  To enable:
    1. Set ``OUTLOOK_ENABLED=true`` in the environment.
    2. Provide ``OUTLOOK_EMAIL``, ``OUTLOOK_PASSWORD``, ``OUTLOOK_SERVER``.
    3. Install ``exchangelib`` and implement the parsing logic here.
    """
    from app import config

    if not config.OUTLOOK_ENABLED:
        logger.debug("Outlook scanning is disabled (OUTLOOK_ENABLED=false).")
        return []

    logger.warning("Outlook scanning stub called — not yet implemented.")
    return []
