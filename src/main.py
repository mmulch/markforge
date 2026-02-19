#!/usr/bin/env python3
"""Einstiegspunkt für den Markdown-Editor."""

from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from mainwindow import MainWindow


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown-Editor")
    app.setOrganizationName("MarkdownEditor")

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
