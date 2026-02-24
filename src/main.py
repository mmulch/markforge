#!/usr/bin/env python3
"""Entry point for the Markdown editor."""

from __future__ import annotations

import logging
import os
import pathlib
import sys
import traceback


# ── Logging setup (must happen before any other import) ───────────────────────

def _log_path() -> pathlib.Path:
    if sys.platform == "win32":
        base = pathlib.Path(os.environ.get("APPDATA", pathlib.Path.home()))
    else:
        base = pathlib.Path.home() / ".config"
    log_dir = base / "MarkForge"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "markforge.log"


_LOG_FILE = _log_path()
logging.basicConfig(
    filename=str(_LOG_FILE),
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    encoding="utf-8",
)
_log = logging.getLogger(__name__)
_log.info("MarkForge starting — Python %s on %s", sys.version, sys.platform)
_log.info("Log file: %s", _LOG_FILE)


def _excepthook(exc_type, exc_value, exc_tb):
    _log.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))
    with open(_LOG_FILE, "a", encoding="utf-8") as fh:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=fh)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook

# ── Application ───────────────────────────────────────────────────────────────

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QApplication

# QtWebEngineWidgets must be imported before QCoreApplication is created.
try:
    import PyQt6.QtWebEngineWidgets  # noqa: F401
except ImportError:
    pass

import i18n
from themes import apply_app_theme


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Editor")
    app.setOrganizationName("MarkdownEditor")

    i18n.setup(QSettings("Markforge", "Markforge").value("language", "en"))
    if i18n.is_rtl():
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    apply_app_theme(
        QSettings("MarkdownEditor", "MarkdownEditor").value("app_theme", "System"),
        app,
    )

    # Show splash before the heavy MainWindow / WebEngine import
    from splash_screen import SplashScreen
    from i18n import tr

    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Importing mainwindow triggers WebEngine DLL loading — the slow part
    splash.set_progress(25, tr("Initializing interface …"))
    from mainwindow import MainWindow

    # Building the window (creates WebEngine widget etc.)
    splash.set_progress(65, tr("Loading …"))
    window = MainWindow()

    splash.set_progress(100, tr("Ready"))
    window.show()           # show window first …
    splash.finish(window)   # … then let QSplashScreen hide itself after first paint
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
