#!/usr/bin/env python3
"""Entry point for the Markdown editor."""

from __future__ import annotations

import sys

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QApplication

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
    splash.finish()

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
