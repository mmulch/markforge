"""Git-related dialogs for MarkForge."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from git_manager import CommitSpec, GitFileInfo, parse_git_url
from i18n import tr


class GitOpenDialog(QDialog):
    """Dialog for entering a GitHub/Bitbucket file URL to open."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Open File from Git"))
        self.setMinimumWidth(520)
        self._info: GitFileInfo | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        form = QFormLayout()

        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText(
            "https://github.com/owner/repo/blob/main/README.md"
        )
        form.addRow(tr("GitHub / Bitbucket file URL:"), self._url_edit)

        self._ref_edit = QLineEdit()
        self._ref_edit.setPlaceholderText("(auto-detected from URL)")
        form.addRow(tr("Ref (branch/tag/commit):"), self._ref_edit)

        layout.addLayout(form)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #888; font-size: 12px;")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self._ok_btn = btns.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_btn.setEnabled(False)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._url_edit.textChanged.connect(self._on_url_changed)

    def _on_url_changed(self, text: str) -> None:
        text = text.strip()
        if not text:
            self._status_label.setText("")
            self._ok_btn.setEnabled(False)
            self._info = None
            return
        try:
            info = parse_git_url(text)
            self._info = info
            self._status_label.setStyleSheet("color: #4caf50; font-size: 12px;")
            host_hint = (
                f" ({info.base_url})"
                if info.platform in ("github_enterprise", "bitbucket_server")
                else ""
            )
            self._status_label.setText(
                f"{info.platform}{host_hint} · {info.owner}/{info.repo} · {info.file_path}"
            )
            # Pre-fill ref field with auto-detected branch if user hasn't typed
            if not self._ref_edit.text():
                self._ref_edit.setPlaceholderText(info.branch)
            self._ok_btn.setEnabled(True)
        except ValueError as exc:
            self._info = None
            self._status_label.setStyleSheet("color: #e57373; font-size: 12px;")
            self._status_label.setText(str(exc))
            self._ok_btn.setEnabled(False)

    def get_info(self) -> GitFileInfo | None:
        """Return the parsed GitFileInfo, applying any ref override."""
        if self._info is None:
            return None
        ref = self._ref_edit.text().strip()
        if ref:
            self._info.branch = ref
        return self._info


class GitCommitDialog(QDialog):
    """Dialog for composing a git commit message and choosing push options."""

    def __init__(self, info: GitFileInfo, parent=None) -> None:
        super().__init__(parent)
        self._info = info
        self.setWindowTitle(tr("Git Commit & Push"))
        self.setMinimumWidth(500)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Commit message
        msg_form = QFormLayout()
        self._msg_edit = QPlainTextEdit()
        self._msg_edit.setFixedHeight(80)
        self._msg_edit.setPlaceholderText("Update README.md")
        msg_form.addRow(tr("Commit message:"), self._msg_edit)
        layout.addLayout(msg_form)

        # Push-to group
        push_grp = QGroupBox(tr("Push to"))
        push_layout = QVBoxLayout(push_grp)

        self._current_radio = QRadioButton(
            tr("Current branch ({branch})", branch=self._info.branch)
        )
        self._current_radio.setChecked(True)
        push_layout.addWidget(self._current_radio)

        new_branch_row_layout = QFormLayout()
        self._new_radio = QRadioButton(tr("New branch:"))
        self._new_branch_edit = QLineEdit()
        self._new_branch_edit.setPlaceholderText("feature/my-changes")
        self._new_branch_edit.setEnabled(False)
        new_branch_row_layout.addRow(self._new_radio, self._new_branch_edit)
        push_layout.addLayout(new_branch_row_layout)

        layout.addWidget(push_grp)

        # PR section (shown only when new_radio is checked)
        self._pr_grp = QGroupBox()
        pr_form = QFormLayout(self._pr_grp)

        self._pr_check = QCheckBox(tr("Create Pull Request"))
        pr_form.addRow(self._pr_check)

        self._pr_title_edit = QLineEdit()
        self._pr_title_edit.setEnabled(False)
        pr_form.addRow(tr("PR title:"), self._pr_title_edit)

        self._pr_target_edit = QLineEdit()
        self._pr_target_edit.setText(self._info.branch)
        self._pr_target_edit.setEnabled(False)
        pr_form.addRow(tr("Target branch:"), self._pr_target_edit)

        self._pr_grp.setVisible(False)
        layout.addWidget(self._pr_grp)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
        )
        commit_btn = QPushButton(tr("Git Commit & Push"))
        commit_btn.setDefault(True)
        btns.addButton(commit_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        # Wire signals
        self._new_radio.toggled.connect(self._on_new_branch_toggled)
        self._pr_check.toggled.connect(self._on_pr_toggled)

    def _on_new_branch_toggled(self, checked: bool) -> None:
        self._new_branch_edit.setEnabled(checked)
        self._pr_grp.setVisible(checked)
        if not checked:
            self._pr_check.setChecked(False)

    def _on_pr_toggled(self, checked: bool) -> None:
        self._pr_title_edit.setEnabled(checked)
        self._pr_target_edit.setEnabled(checked)

    def _save_and_accept(self) -> None:
        from PyQt6.QtWidgets import QMessageBox
        msg = self._msg_edit.toPlainText().strip()
        if not msg:
            QMessageBox.warning(
                self, tr("Git Commit & Push"),
                tr("Commit message:") + " cannot be empty.",
            )
            self._msg_edit.setFocus()
            return

        if self._new_radio.isChecked() and not self._new_branch_edit.text().strip():
            QMessageBox.warning(
                self, tr("Git Commit & Push"),
                tr("New branch:") + " cannot be empty.",
            )
            self._new_branch_edit.setFocus()
            return

        if self._pr_check.isChecked() and not self._pr_title_edit.text().strip():
            QMessageBox.warning(
                self, tr("Git Commit & Push"),
                tr("PR title:") + " cannot be empty.",
            )
            self._pr_title_edit.setFocus()
            return

        self.accept()

    def get_spec(self) -> CommitSpec:
        """Return the filled-in CommitSpec."""
        push_mode  = "new_branch" if self._new_radio.isChecked() else "current_branch"
        new_branch = self._new_branch_edit.text().strip() if self._new_radio.isChecked() else ""
        create_pr  = self._pr_check.isChecked()
        return CommitSpec(
            message    = self._msg_edit.toPlainText().strip(),
            push_mode  = push_mode,
            new_branch = new_branch,
            create_pr  = create_pr,
            pr_title   = self._pr_title_edit.text().strip() if create_pr else "",
            pr_target  = self._pr_target_edit.text().strip() if create_pr else "",
        )
