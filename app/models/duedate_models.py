"""DueDate / alert data models."""

from enum import Enum
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


class AlertLevel(str, Enum):
    """Alert urgency based on days remaining until due date."""

    NONE = "none"      # > 7 days
    D7 = "d7"          # ≤ 7 days
    D3 = "d3"          # ≤ 3 days
    D1 = "d1"          # ≤ 1 day  (includes overdue)


@dataclass
class DueDateEntry:
    """A single scheduled due date entry."""

    report_id: str
    report_label: str
    due_date: date
    source: str = "manual"           # "manual" | "outlook"
    note: str = ""
    alerts_sent: dict = field(default_factory=lambda: {"d7": False, "d3": False, "d1": False})

    @property
    def days_remaining(self) -> int:
        """Return number of days from today until due_date (negative if overdue)."""
        return (self.due_date - date.today()).days

    @property
    def alert_level(self) -> AlertLevel:
        """Compute the current alert level."""
        days = self.days_remaining
        if days <= 1:
            return AlertLevel.D1
        if days <= 3:
            return AlertLevel.D3
        if days <= 7:
            return AlertLevel.D7
        return AlertLevel.NONE

    @property
    def alert_color(self) -> str:
        """Return a CSS color string matching the alert level."""
        mapping = {
            AlertLevel.D1: "red",
            AlertLevel.D3: "orange",
            AlertLevel.D7: "green",
            AlertLevel.NONE: "grey",
        }
        return mapping[self.alert_level]
