"""Splash screen shown during application startup."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QLabel, QProgressBar, QVBoxLayout, QWidget

from i18n import tr


class SplashScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(460, 220)
        self._center()
        self._setup_ui()

    def _center(self) -> None:
        geo = QApplication.primaryScreen().geometry()
        self.move(
            (geo.width()  - self.width())  // 2,
            (geo.height() - self.height()) // 2,
        )

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 36, 32, 20)
        layout.setSpacing(0)

        title = QLabel("MarkForge")
        title.setStyleSheet(
            "color: #d4d4d4; font-size: 32px; font-weight: 600; background: transparent;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._lbl = QLabel(tr("Loading …"))
        self._lbl.setStyleSheet(
            "color: #6a9955; font-size: 11px; background: transparent;"
        )
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(3)
        self._bar.setStyleSheet(
            "QProgressBar { background-color: #3c3c3c; border: none; border-radius: 1px; }"
            "QProgressBar::chunk { background-color: #0078d4; border-radius: 1px; }"
        )

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(self._lbl)
        layout.addStretch(2)
        layout.addWidget(self._bar)

        self.setStyleSheet("SplashScreen { background-color: #1e1e1e; }")

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        p = QPainter(self)
        p.setPen(QPen(QColor("#3c3c3c"), 1))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def set_progress(self, value: int, message: str = "") -> None:
        if message:
            self._lbl.setText(message)
        self._bar.setValue(value)
        QApplication.processEvents()

    def finish(self) -> None:
        self.close()
