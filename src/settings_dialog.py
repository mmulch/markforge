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
from themes import APP_THEMES, EDITOR_THEMES, PREVIEW_THEMES


class SettingsDialog(QDialog):
    """Dialog for editing application settings (language, themes, …)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Settings"))
        self.setMinimumWidth(360)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(12)

        form = QFormLayout()

        # ── Language ──────────────────────────────────────────────────────────
        self._lang_combo = QComboBox()
        self._lang_combo.addItem("Deutsch", "de")
        self._lang_combo.addItem("English", "en")

        lang_settings = QSettings("Markforge", "Markforge")
        current_lang = lang_settings.value("language", "en")
        idx = self._lang_combo.findData(current_lang)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)

        form.addRow(tr("Language:"), self._lang_combo)

        # ── Theme settings ────────────────────────────────────────────────────
        theme_settings = QSettings("MarkdownEditor", "MarkdownEditor")

        self._editor_theme_combo = QComboBox()
        for name in EDITOR_THEMES:
            self._editor_theme_combo.addItem(name)
        current_editor_theme = theme_settings.value("editor_theme", "VS Code Dark")
        idx = self._editor_theme_combo.findText(current_editor_theme)
        if idx >= 0:
            self._editor_theme_combo.setCurrentIndex(idx)
        form.addRow(tr("Editor theme:"), self._editor_theme_combo)

        self._preview_theme_combo = QComboBox()
        for name in PREVIEW_THEMES:
            self._preview_theme_combo.addItem(name)
        current_preview_theme = theme_settings.value("preview_theme", "GitHub Dark")
        idx = self._preview_theme_combo.findText(current_preview_theme)
        if idx >= 0:
            self._preview_theme_combo.setCurrentIndex(idx)
        form.addRow(tr("Preview theme:"), self._preview_theme_combo)

        self._app_theme_combo = QComboBox()
        for name in APP_THEMES:
            self._app_theme_combo.addItem(name)
        current_app_theme = theme_settings.value("app_theme", "System")
        idx = self._app_theme_combo.findText(current_app_theme)
        if idx >= 0:
            self._app_theme_combo.setCurrentIndex(idx)
        form.addRow(tr("App theme:"), self._app_theme_combo)

        root.addLayout(form)

        lang_info = QLabel(tr("Restart required to apply language changes."))
        lang_info.setStyleSheet("color: #888; font-size: 12px;")
        root.addWidget(lang_info)

        app_theme_info = QLabel(tr("App theme requires restart."))
        app_theme_info.setStyleSheet("color: #888; font-size: 12px;")
        root.addWidget(app_theme_info)

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

        theme_settings = QSettings("MarkdownEditor", "MarkdownEditor")
        theme_settings.setValue("editor_theme",  self._editor_theme_combo.currentText())
        theme_settings.setValue("preview_theme", self._preview_theme_combo.currentText())
        theme_settings.setValue("app_theme",     self._app_theme_combo.currentText())
        self.accept()
