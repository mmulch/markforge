"""Settings dialog for Markdown Editor."""

from __future__ import annotations

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from credentials import get_secret, set_secret
from i18n import LANGUAGES, SPELL_CHECK_LANGUAGES, UI_LANGUAGES, tr
from themes import APP_THEMES, EDITOR_THEMES, PREVIEW_THEMES


_SECRET_KEYS = ("git/https_token", "git/ssh_passphrase", "proxy/password")


def _migrate_plaintext_credentials(s: QSettings) -> None:
    """One-time migration: move plaintext secrets from QSettings into the OS keyring."""
    for key in _SECRET_KEYS:
        old_val = s.value(key, "")
        if old_val:
            set_secret(key, old_val)
            s.remove(key)


class SettingsDialog(QDialog):
    """Dialog for editing application settings (language, themes, …)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Settings"))
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(12)

        form = QFormLayout()

        # ── Language ──────────────────────────────────────────────────────────
        self._lang_combo = QComboBox()
        for code in UI_LANGUAGES:
            self._lang_combo.addItem(LANGUAGES[code], code)

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

        # ── Spell Check Languages ─────────────────────────────────────────────
        spell_grp = QGroupBox(tr("Spell Check Languages"))
        spell_vbox = QVBoxLayout(spell_grp)

        spell_hint = QLabel(tr("Active spell check languages (shown in View menu):"))
        spell_hint.setStyleSheet("font-size: 12px;")
        spell_vbox.addWidget(spell_hint)

        self._spell_lang_list = QListWidget()
        self._spell_lang_list.setFixedHeight(140)

        s_spell = QSettings("MarkdownEditor", "MarkdownEditor")
        enabled_langs = s_spell.value("spell_langs_enabled", list(SPELL_CHECK_LANGUAGES))
        if isinstance(enabled_langs, str):
            enabled_langs = [enabled_langs]

        for code in SPELL_CHECK_LANGUAGES:
            item = QListWidgetItem(LANGUAGES[code])
            item.setData(Qt.ItemDataRole.UserRole, code)
            item.setCheckState(
                Qt.CheckState.Checked if code in enabled_langs
                else Qt.CheckState.Unchecked
            )
            self._spell_lang_list.addItem(item)

        spell_vbox.addWidget(self._spell_lang_list)
        root.addWidget(spell_grp)

        # ── Git Authentication ─────────────────────────────────────────────────
        git_grp = QGroupBox(tr("Git Authentication"))
        git_layout = QVBoxLayout(git_grp)

        auth_form = QFormLayout()

        self._git_auth_combo = QComboBox()
        self._git_auth_combo.addItem(tr("HTTPS (embedded)"), "https")
        self._git_auth_combo.addItem(tr("HTTPS (git binary)"),       "git")
        self._git_auth_combo.addItem(tr("SSH (key file)"),           "ssh")
        auth_form.addRow(tr("Auth method:"), self._git_auth_combo)
        git_layout.addLayout(auth_form)

        # HTTPS sub-group
        self._https_grp = QGroupBox()
        https_form = QFormLayout(self._https_grp)
        self._git_username_edit = QLineEdit()
        self._git_username_edit.setPlaceholderText("your-username")
        self._git_token_edit = QLineEdit()
        self._git_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._git_token_edit.setPlaceholderText("ghp_…")
        https_form.addRow(tr("Username:"), self._git_username_edit)
        https_form.addRow(tr("Token:"),    self._git_token_edit)
        git_layout.addWidget(self._https_grp)

        # Git identity sub-group (git binary only)
        self._git_identity_grp = QGroupBox()
        identity_form = QFormLayout(self._git_identity_grp)
        self._git_name_edit  = QLineEdit()
        self._git_name_edit.setPlaceholderText("Your Name")
        self._git_email_edit = QLineEdit()
        self._git_email_edit.setPlaceholderText("you@example.com")
        identity_form.addRow(tr("Name:"),  self._git_name_edit)
        identity_form.addRow(tr("Email:"), self._git_email_edit)
        git_layout.addWidget(self._git_identity_grp)

        # SSH sub-group
        self._ssh_grp = QGroupBox()
        ssh_form = QFormLayout(self._ssh_grp)
        ssh_key_row = QHBoxLayout()
        self._git_ssh_key_edit = QLineEdit()
        self._git_ssh_key_edit.setPlaceholderText("~/.ssh/id_ed25519")
        ssh_browse_btn = QPushButton("…")
        ssh_browse_btn.setFixedWidth(30)
        ssh_browse_btn.clicked.connect(self._browse_ssh_key)
        ssh_key_row.addWidget(self._git_ssh_key_edit)
        ssh_key_row.addWidget(ssh_browse_btn)
        self._git_passphrase_edit = QLineEdit()
        self._git_passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)
        ssh_form.addRow(tr("SSH key:"),    ssh_key_row)
        ssh_form.addRow(tr("Passphrase:"), self._git_passphrase_edit)
        git_layout.addWidget(self._ssh_grp)

        root.addWidget(git_grp)

        # Load saved git settings
        s = QSettings("MarkdownEditor", "MarkdownEditor")
        _migrate_plaintext_credentials(s)
        saved_method = s.value("git/auth_method", "https")
        idx = self._git_auth_combo.findData(saved_method)
        if idx >= 0:
            self._git_auth_combo.setCurrentIndex(idx)
        self._git_username_edit.setText(s.value("git/https_username", ""))
        self._git_token_edit.setText(get_secret("git/https_token"))
        self._git_name_edit.setText(s.value("git/user_name",          ""))
        self._git_email_edit.setText(s.value("git/user_email",        ""))
        self._git_ssh_key_edit.setText(s.value("git/ssh_key_path",    ""))
        self._git_passphrase_edit.setText(get_secret("git/ssh_passphrase"))

        # Wire toggle
        self._git_auth_combo.currentIndexChanged.connect(self._on_auth_changed)
        self._on_auth_changed()

        # ── HTTP Proxy ────────────────────────────────────────────────────────
        proxy_grp = QGroupBox(tr("HTTP Proxy"))
        proxy_form = QFormLayout(proxy_grp)

        self._proxy_url_edit = QLineEdit()
        self._proxy_url_edit.setPlaceholderText("http://proxy.company.com:8080")
        proxy_form.addRow(tr("Proxy URL:"), self._proxy_url_edit)

        self._proxy_user_edit = QLineEdit()
        self._proxy_user_edit.setPlaceholderText("domain\\username")
        proxy_form.addRow(tr("Proxy username:"), self._proxy_user_edit)

        self._proxy_pass_edit = QLineEdit()
        self._proxy_pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        proxy_form.addRow(tr("Proxy password:"), self._proxy_pass_edit)

        proxy_hint = QLabel(tr("Leave empty to use system proxy settings."))
        proxy_hint.setStyleSheet("color: #888; font-size: 12px;")
        proxy_form.addRow(proxy_hint)

        s2 = QSettings("MarkdownEditor", "MarkdownEditor")
        self._proxy_url_edit.setText(s2.value("proxy/url",      ""))
        self._proxy_user_edit.setText(s2.value("proxy/username", ""))
        self._proxy_pass_edit.setText(get_secret("proxy/password"))

        root.addWidget(proxy_grp)

        # ── Auto-Save ─────────────────────────────────────────────────────────
        autosave_grp = QGroupBox(tr("Auto-Save"))
        autosave_form = QFormLayout(autosave_grp)

        self._autosave_enabled_cb = QCheckBox()
        autosave_form.addRow(tr("Enable auto-save"), self._autosave_enabled_cb)

        self._autosave_interval_spin = QSpinBox()
        self._autosave_interval_spin.setRange(5, 600)
        self._autosave_interval_spin.setSuffix(" s")
        autosave_form.addRow(tr("Interval (seconds):"), self._autosave_interval_spin)

        self._autosave_focus_cb = QCheckBox()
        autosave_form.addRow(tr("Save on focus loss"), self._autosave_focus_cb)

        s3 = QSettings("MarkdownEditor", "MarkdownEditor")
        self._autosave_enabled_cb.setChecked(s3.value("autosave/enabled", False, type=bool))
        self._autosave_interval_spin.setValue(int(s3.value("autosave/interval", 30)))
        self._autosave_focus_cb.setChecked(s3.value("autosave/on_focus_loss", False, type=bool))

        # Disable controls when auto-save is off
        self._autosave_enabled_cb.toggled.connect(self._on_autosave_toggled)
        self._on_autosave_toggled(self._autosave_enabled_cb.isChecked())

        root.addWidget(autosave_grp)

        # ── Buttons ───────────────────────────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _on_autosave_toggled(self, checked: bool) -> None:
        self._autosave_interval_spin.setEnabled(checked)
        self._autosave_focus_cb.setEnabled(checked)

    def _on_auth_changed(self) -> None:
        method = self._git_auth_combo.currentData()
        self._https_grp.setVisible(method in ("https", "git"))
        self._git_identity_grp.setVisible(method == "git")
        self._ssh_grp.setVisible(method == "ssh")

    def _browse_ssh_key(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Select SSH Key File"),
            "~/.ssh",
        )
        if path:
            self._git_ssh_key_edit.setText(path)

    def _save_and_accept(self) -> None:
        lang = self._lang_combo.currentData()
        QSettings("Markforge", "Markforge").setValue("language", lang)

        theme_settings = QSettings("MarkdownEditor", "MarkdownEditor")
        theme_settings.setValue("editor_theme",  self._editor_theme_combo.currentText())
        theme_settings.setValue("preview_theme", self._preview_theme_combo.currentText())
        theme_settings.setValue("app_theme",     self._app_theme_combo.currentText())

        enabled_langs = []
        for i in range(self._spell_lang_list.count()):
            item = self._spell_lang_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                enabled_langs.append(item.data(Qt.ItemDataRole.UserRole))
        theme_settings.setValue("spell_langs_enabled", enabled_langs)

        # Git credentials (non-sensitive in QSettings, secrets in OS keyring)
        theme_settings.setValue("git/auth_method",    self._git_auth_combo.currentData())
        theme_settings.setValue("git/https_username", self._git_username_edit.text())
        set_secret("git/https_token",                 self._git_token_edit.text())
        theme_settings.setValue("git/user_name",      self._git_name_edit.text())
        theme_settings.setValue("git/user_email",     self._git_email_edit.text())
        theme_settings.setValue("git/ssh_key_path",   self._git_ssh_key_edit.text())
        set_secret("git/ssh_passphrase",              self._git_passphrase_edit.text())

        # Proxy
        theme_settings.setValue("proxy/url",      self._proxy_url_edit.text().strip())
        theme_settings.setValue("proxy/username", self._proxy_user_edit.text().strip())
        set_secret("proxy/password",              self._proxy_pass_edit.text())

        # Auto-save
        theme_settings.setValue("autosave/enabled",       self._autosave_enabled_cb.isChecked())
        theme_settings.setValue("autosave/interval",      self._autosave_interval_spin.value())
        theme_settings.setValue("autosave/on_focus_loss", self._autosave_focus_cb.isChecked())

        self.accept()
