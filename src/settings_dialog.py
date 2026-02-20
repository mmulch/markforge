"""Settings dialog for Markdown Editor."""

from __future__ import annotations

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)

from i18n import tr


class SettingsDialog(QDialog):
    """Dialog for editing application settings (language, …)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Settings"))
        self.setMinimumWidth(320)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(12)

        form = QFormLayout()
        self._lang_combo = QComboBox()
        self._lang_combo.addItem("Deutsch", "de")
        self._lang_combo.addItem("English", "en")

        settings = QSettings("Markforge", "Markforge")
        current_lang = settings.value("language", "en")
        idx = self._lang_combo.findData(current_lang)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)

        form.addRow(tr("Language:"), self._lang_combo)
        root.addLayout(form)

        info = QLabel(tr("Restart required to apply language changes."))
        info.setStyleSheet("color: #888; font-size: 12px;")
        root.addWidget(info)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _save_and_accept(self) -> None:
        lang = self._lang_combo.currentData()
        QSettings("Markforge", "Markforge").setValue("language", lang)
        self.accept()
