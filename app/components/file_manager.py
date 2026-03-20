"""File manager component.

Provides a simple UI for listing, uploading, and deleting files
inside the ``data/uploads`` directory.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from nicegui import ui, events
from app.utils.paths import UPLOAD_DIR
from app.utils.logging import get_logger

logger = get_logger(__name__)


class FileManager:
    """Renders an upload panel and a refreshable file list."""

    def __init__(self) -> None:
        self._file_list_container: ui.column | None = None

    def build(self) -> None:
        """Render the file manager inside the current layout context."""
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        with ui.card().classes("w-full q-mt-md"):
            ui.label("📁 파일 관리").classes("text-subtitle1 text-bold q-mb-sm")

            # Upload widget
            ui.upload(
                label="파일 업로드",
                multiple=True,
                on_upload=self._handle_upload,
            ).classes("w-full").props("flat bordered")

            ui.separator()

            # File list
            self._file_list_container = ui.column().classes("w-full gap-1")
            self._refresh_file_list()

    def _handle_upload(self, event: events.UploadEventArguments) -> None:
        """Save the uploaded file to UPLOAD_DIR."""
        dest = UPLOAD_DIR / event.name
        try:
            with dest.open("wb") as fh:
                fh.write(event.content.read())
            logger.info("Uploaded file saved: %s", dest)
            ui.notify(f"✅ '{event.name}' 업로드 완료", type="positive")
        except OSError as exc:
            logger.error("Failed to save uploaded file: %s", exc)
            ui.notify(f"❌ 업로드 실패: {exc}", type="negative")
        self._refresh_file_list()

    def _refresh_file_list(self) -> None:
        """Redraw the list of files currently in UPLOAD_DIR."""
        if self._file_list_container is None:
            return
        self._file_list_container.clear()
        files = sorted(UPLOAD_DIR.glob("*")) if UPLOAD_DIR.exists() else []

        with self._file_list_container:
            if not files:
                ui.label("업로드된 파일이 없습니다.").classes("text-caption text-grey-6")
                return
            for file_path in files:
                if not file_path.is_file():
                    continue
                size_kb = file_path.stat().st_size / 1024
                with ui.row().classes("items-center gap-2 w-full no-wrap"):
                    ui.icon("description").classes("text-grey-7")
                    ui.label(file_path.name).classes("text-body2 flex-grow")
                    ui.label(f"{size_kb:.1f} KB").classes("text-caption text-grey-6")
                    ui.button(
                        icon="delete",
                        on_click=lambda p=file_path: self._delete_file(p),
                    ).props("flat dense color=negative")

    def _delete_file(self, file_path: Path) -> None:
        """Delete *file_path* and refresh the list."""
        try:
            file_path.unlink()
            logger.info("Deleted file: %s", file_path)
            ui.notify(f"🗑️ '{file_path.name}' 삭제 완료", type="info")
        except OSError as exc:
            logger.error("Failed to delete file: %s", exc)
            ui.notify(f"❌ 삭제 실패: {exc}", type="negative")
        self._refresh_file_list()
