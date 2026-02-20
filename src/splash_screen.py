"""Splash screen shown during application startup."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QEventLoop
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QProgressBar, QSplashScreen

from i18n import tr


class SplashScreen(QSplashScreen):
    """QSplashScreen with a thin progress bar drawn as a child widget."""

    def __init__(self) -> None:
        super().__init__(self._make_pixmap())

        self._bar = QProgressBar(self)
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(3)
        self._bar.setGeometry(0, self.pixmap().height() - 3, self.pixmap().width(), 3)
        self._bar.setStyleSheet(
            "QProgressBar { background: #3c3c3c; border: none; }"
            "QProgressBar::chunk { background: #0078d4; }"
        )

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _make_pixmap() -> QPixmap:
        w, h = 460, 220
        px = QPixmap(w, h)
        px.fill(QColor("#1e1e1e"))

        p = QPainter(px)
        p.setPen(QPen(QColor("#3c3c3c"), 1))
        p.drawRect(0, 0, w - 1, h - 1)

        f = QFont()
        f.setPixelSize(34)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor("#d4d4d4"))
        p.drawText(0, 0, w, h - 50, Qt.AlignmentFlag.AlignCenter, "MarkForge")
        p.end()
        return px

    # ── Public API ────────────────────────────────────────────────────────────

    def set_progress(self, value: int, message: str = "") -> None:
        if message:
            self.showMessage(
                message,
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                QColor("#6a9955"),
            )
        self._bar.setValue(value)
        # ExcludeUserInputEvents: repaint splash without processing clicks/keys
        QApplication.processEvents(
            QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents
        )
