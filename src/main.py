#!/usr/bin/env python3
"""Entry point for the Markdown editor."""

from __future__ import annotations

import sys

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QApplication

import i18n
from mainwindow import MainWindow


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Editor")
    app.setOrganizationName("MarkdownEditor")

    i18n.setup(QSettings("Markforge", "Markforge").value("language", "en"))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
