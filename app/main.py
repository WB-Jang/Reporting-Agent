"""NiceGUI application entry point.

Run the app with:

    python -m app.main
    # or
    python app/main.py
"""

from app.utils.paths import ensure_dirs
from app.pages.home import build_home_page
from app import config
from nicegui import ui

# Ensure all required directories exist
ensure_dirs()

# Register pages
build_home_page()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        title=config.APP_TITLE,
        reload=config.APP_RELOAD,
        favicon="📊",
    )
