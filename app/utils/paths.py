"""Absolute path helpers for the application."""

import pathlib

# Root of the repository
BASE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent.parent

# Input data files (report source files uploaded by users)
DATA_DIR: pathlib.Path = BASE_DIR / "data"

# ChromaDB persistence directory
VECTOR_DB_DIR: pathlib.Path = BASE_DIR / "vectordb" / "chroma_data"

# Scheduler / DueDate JSON
SCHEDULER_DIR: pathlib.Path = BASE_DIR / "scheduler"
DUE_DATES_FILE: pathlib.Path = SCHEDULER_DIR / "due_dates.json"

# Uploaded files staging area
UPLOAD_DIR: pathlib.Path = DATA_DIR / "uploads"


def ensure_dirs() -> None:
    """Create required directories if they do not exist."""
    for directory in (DATA_DIR, VECTOR_DB_DIR, SCHEDULER_DIR, UPLOAD_DIR):
        directory.mkdir(parents=True, exist_ok=True)
