"""Git-related dialogs for MarkForge."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from git_manager import CommitInfo, CommitSpec, GitFileInfo, parse_git_url
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

    def __init__(self, info: GitFileInfo, parent=None, *,
                 amend_available: bool = False,
                 prev_message: str = "") -> None:
        super().__init__(parent)
        self._info            = info
        self._amend_available = amend_available
        self._prev_message    = prev_message
        self.setWindowTitle(tr("Git Commit & Push"))
        self.setMinimumWidth(500)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Amend checkbox (only shown from the 2nd push in a session, SSH only)
        self._amend_check: QCheckBox | None = None
        if self._amend_available:
            self._amend_check = QCheckBox(tr("Amend previous commit"))
            self._amend_check.setChecked(True)
            layout.addWidget(self._amend_check)

        # Commit message
        msg_form = QFormLayout()
        self._msg_edit = QPlainTextEdit()
        self._msg_edit.setFixedHeight(80)
        self._msg_edit.setPlaceholderText("Update README.md")
        if self._prev_message and self._amend_available:
            self._msg_edit.setPlainText(self._prev_message)
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
        if self._amend_check is not None:
            self._amend_check.toggled.connect(self._on_amend_toggled)
            # Apply initial state: amend is checked by default
            self._on_amend_toggled(True)

    def _on_amend_toggled(self, checked: bool) -> None:
        """Disable branch/PR options while amend is selected."""
        self._current_radio.setEnabled(not checked)
        self._new_radio.setEnabled(not checked)
        self._new_branch_edit.setEnabled(False)
        self._pr_grp.setVisible(False)
        if not checked:
            # Restore branch radio state
            self._new_branch_edit.setEnabled(self._new_radio.isChecked())
            self._pr_grp.setVisible(self._new_radio.isChecked())

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
        amend = (
            self._amend_check is not None and self._amend_check.isChecked()
        )
        if amend:
            return CommitSpec(
                message   = self._msg_edit.toPlainText().strip(),
                push_mode = "current_branch",
                amend     = True,
            )
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


class GitSquashDialog(QDialog):
    """Dialog for squashing multiple branch commits into one.

    Loads commits on HEAD that are not in *base_branch* (default: main).
    The user selects a contiguous range from HEAD; those commits are
    squashed into one and force-pushed.
    """

    _COL_SHA     = 0
    _COL_MESSAGE = 1
    _COL_AUTHOR  = 2
    _COL_DATE    = 3

    def __init__(self, info: GitFileInfo, settings,
                 base_branch: str = "main", parent=None) -> None:
        super().__init__(parent)
        self._info        = info
        self._settings    = settings
        self._commits: list[CommitInfo] = []
        self.setWindowTitle(tr("Git Squash Commits"))
        self.setMinimumSize(700, 520)
        self._build_ui()
        self._base_branch_edit.setText(base_branch)
        self._reload_commits()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ── Base branch row ───────────────────────────────────────────────────
        base_form = QFormLayout()
        base_row  = QHBoxLayout()
        self._base_branch_edit = QLineEdit()
        self._base_branch_edit.setPlaceholderText("main")
        self._reload_btn = QPushButton(tr("Reload"))
        self._reload_btn.clicked.connect(self._reload_commits)
        base_row.addWidget(self._base_branch_edit)
        base_row.addWidget(self._reload_btn)
        base_form.addRow(tr("Base branch:"), base_row)
        layout.addLayout(base_form)

        # ── Select-all button ─────────────────────────────────────────────────
        select_all_btn = QPushButton(tr("Select all new commits"))
        select_all_btn.clicked.connect(self._select_all)
        layout.addWidget(select_all_btn)

        # ── Commits table ─────────────────────────────────────────────────────
        self._table = QTableWidget(0, 4, self)
        self._table.setHorizontalHeaderLabels([
            tr("SHA"), tr("Message"), tr("Author"), tr("Date"),
        ])
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(self._COL_SHA,     QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(self._COL_MESSAGE, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(self._COL_AUTHOR,  QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(self._COL_DATE,    QHeaderView.ResizeMode.ResizeToContents)
        self._table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._table)

        # ── Status label ──────────────────────────────────────────────────────
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet("color: #e57373; font-size: 12px;")
        self._status_lbl.setWordWrap(True)
        layout.addWidget(self._status_lbl)

        # ── Combined commit message ───────────────────────────────────────────
        layout.addWidget(QLabel(tr("Squash commit message:")))
        self._msg_edit = QPlainTextEdit()
        self._msg_edit.setFixedHeight(90)
        self._msg_edit.setPlaceholderText(tr("Enter the combined commit message …"))
        layout.addWidget(self._msg_edit)

        # ── Buttons ───────────────────────────────────────────────────────────
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self._squash_btn = QPushButton(tr("Squash && Push"))
        self._squash_btn.setDefault(True)
        btns.addButton(self._squash_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    # ── Loading ───────────────────────────────────────────────────────────────

    def _reload_commits(self) -> None:
        from git_manager import get_branch_commits
        base = self._base_branch_edit.text().strip() or "main"
        self._status_lbl.setText(tr("Loading …"))
        self._reload_btn.setEnabled(False)
        self._squash_btn.setEnabled(False)

        # Process events so the label updates before the (possibly slow) fetch
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            commits = get_branch_commits(self._info, self._settings, base)
        except Exception as exc:
            self._status_lbl.setText(str(exc))
            self._reload_btn.setEnabled(True)
            return
        finally:
            self._reload_btn.setEnabled(True)

        self._commits = commits
        self._populate_table()

        if not commits:
            self._status_lbl.setText(
                tr("No new commits found compared to '{base}'.",
                   base=base)
            )
            self._squash_btn.setEnabled(False)
        else:
            self._status_lbl.setText("")
            self._squash_btn.setEnabled(True)

    def _populate_table(self) -> None:
        self._table.itemChanged.disconnect(self._on_item_changed)
        self._table.setRowCount(len(self._commits))
        for row, commit in enumerate(self._commits):
            sha_item = QTableWidgetItem(commit.sha[:8])
            sha_item.setCheckState(Qt.CheckState.Unchecked)
            sha_item.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
            )
            self._table.setItem(row, self._COL_SHA,     sha_item)
            self._table.setItem(row, self._COL_MESSAGE, QTableWidgetItem(commit.message))
            self._table.setItem(row, self._COL_AUTHOR,  QTableWidgetItem(commit.author))
            self._table.setItem(row, self._COL_DATE,    QTableWidgetItem(commit.date))
        self._table.itemChanged.connect(self._on_item_changed)
        self._select_all()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _select_all(self) -> None:
        self._table.itemChanged.disconnect(self._on_item_changed)
        for row in range(self._table.rowCount()):
            self._table.item(row, self._COL_SHA).setCheckState(
                Qt.CheckState.Checked
            )
        self._table.itemChanged.connect(self._on_item_changed)
        self._refresh_message()

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        if item.column() != self._COL_SHA:
            return
        self._refresh_message()

    def _refresh_message(self) -> None:
        """Re-fill the message box from all checked commits."""
        msgs = [
            self._commits[row].message
            for row in range(self._table.rowCount())
            if self._table.item(row, self._COL_SHA).checkState()
               == Qt.CheckState.Checked
        ]
        self._msg_edit.setPlainText("\n".join(msgs))

    def _checked_rows(self) -> list[int]:
        return [
            row for row in range(self._table.rowCount())
            if self._table.item(row, self._COL_SHA).checkState()
               == Qt.CheckState.Checked
        ]

    # ── Validation & accept ───────────────────────────────────────────────────

    def _save_and_accept(self) -> None:
        checked = self._checked_rows()

        if len(checked) < 2:
            QMessageBox.warning(
                self, tr("Git Squash Commits"),
                tr("Select at least 2 commits to squash."),
            )
            return

        # Must start from row 0 (HEAD) and be contiguous
        expected = list(range(checked[0], checked[-1] + 1))
        if checked[0] != 0 or checked != expected:
            QMessageBox.warning(
                self, tr("Git Squash Commits"),
                tr("The selected commits must form a contiguous range "
                   "starting from the most recent commit (HEAD)."),
            )
            return

        if not self._msg_edit.toPlainText().strip():
            QMessageBox.warning(
                self, tr("Git Squash Commits"),
                tr("Squash commit message:") + " " + tr("cannot be empty."),
            )
            self._msg_edit.setFocus()
            return

        self.accept()

    def get_result(self) -> tuple[int, str]:
        """Return (squash_count, message).

        squash_count is the number of checked commits; the squash
        uses HEAD~squash_count as the target parent.
        """
        return len(self._checked_rows()), self._msg_edit.toPlainText().strip()
