"""Report execution orchestrator.

This module provides a mock implementation that simulates multi-step report
generation.  Replace the body of ``ReportRunner.run()`` with the actual
business-logic calls (e.g. ``langgraph_agent``) once they are available.
"""

from __future__ import annotations

import asyncio
import time
from typing import Callable, Optional
from app.models.report_models import ReportMeta
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Type alias for progress callbacks
ProgressCallback = Callable[[str], None]


class ReportRunner:
    """Orchestrates the execution of a single report.

    Parameters
    ----------
    report_meta:
        Metadata describing the report to run.
    params:
        Collected parameter values (``{param_name: value}``).
    on_progress:
        Optional callback invoked with each progress message so the caller
        (e.g. the chat window) can display live updates.
    """

    def __init__(
        self,
        report_meta: ReportMeta,
        params: dict,
        on_progress: Optional[ProgressCallback] = None,
    ) -> None:
        self.report_meta = report_meta
        self.params = params
        self.on_progress = on_progress or (lambda msg: None)

    def _emit(self, message: str) -> None:
        """Send a progress message to the caller."""
        logger.info("[%s] %s", self.report_meta.report_id, message)
        self.on_progress(message)

    def run(self) -> str:
        """Execute the report and return a result summary string.

        This is currently a **mock** implementation that simulates progress
        steps with short sleeps.  Swap the step bodies for real calls to the
        Reporting-agent business logic when ready.
        """
        report_id = self.report_meta.report_id
        self._emit(f"⏳ **{self.report_meta.label}** 보고서 실행을 시작합니다…")

        # --- Step 1: Data loading (stub) ---
        time.sleep(0.3)
        self._emit(f"📂 데이터 로딩 중… (파라미터: {self.params})")

        # --- Step 2: Processing (stub) ---
        time.sleep(0.3)
        self._emit("⚙️ 데이터 처리 중…")

        # --- Step 3: Report generation (stub) ---
        time.sleep(0.3)
        self._emit("📝 보고서 생성 중…")

        # --- Completed ---
        result = (
            f"✅ **{self.report_meta.label}** 보고서 작성이 완료되었습니다.\n"
            f"출력 경로: `data/output/{report_id}_result.xlsx`"
        )
        self._emit(result)
        return result

    async def run_async(self) -> str:
        """Async wrapper around :meth:`run` using a thread executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run)
