"""Git-related dialogs for MarkForge."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QThread, pyqtSignal
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

from git_manager import (CommitInfo, CommitSpec, GitFileInfo,
                         fetch_default_branch, fetch_branches,
                         parse_git_url, parse_git_repo_url)
from i18n import tr


class _BranchDetectWorker(QThread):
    """Background thread that queries the platform API for the default branch."""
    detected = pyqtSignal(str)   # emits branch name, or "" on failure

    def __init__(self, info: GitFileInfo, settings, parent=None) -> None:
        super().__init__(parent)
        self._info     = info
        self._settings = settings

    def run(self) -> None:
        branch = fetch_default_branch(self._info, self._settings)
        self.detected.emit(branch)


class GitOpenDialog(QDialog):
    """Dialog for entering a GitHub/Bitbucket file URL to open."""

    def __init__(self, settings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Open File from Git"))
        self.setMinimumWidth(520)
        self._info: GitFileInfo | None = None
        self._settings = settings
        self._branch_worker: _BranchDetectWorker | None = None
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
        # Cancel any in-progress branch detection
        if self._branch_worker and self._branch_worker.isRunning():
            self._branch_worker.detected.disconnect()
            self._branch_worker.quit()
            self._branch_worker = None

        text = text.strip()
        if not text:
            self._status_label.setText("")
            self._ok_btn.setEnabled(False)
            self._info = None
            return
        try:
            info = parse_git_url(text)
            self._info = info
            host_hint = (
                f" ({info.base_url})"
                if info.platform in ("github_enterprise", "bitbucket_server")
                else ""
            )
            summary = f"{info.platform}{host_hint} · {info.owner}/{info.repo} · {info.file_path}"

            if not info.branch:
                # Branch not in URL — query the API in the background
                self._status_label.setStyleSheet("color: #888; font-size: 12px;")
                self._status_label.setText(tr("Detecting default branch…") + "  " + summary)
                self._ref_edit.setPlaceholderText(tr("detecting…"))
                self._ok_btn.setEnabled(False)
                self._branch_worker = _BranchDetectWorker(info, self._settings, self)
                self._branch_worker.detected.connect(self._on_branch_detected)
                self._branch_worker.start()
            else:
                self._status_label.setStyleSheet("color: #4caf50; font-size: 12px;")
                self._status_label.setText(summary)
                if not self._ref_edit.text():
                    self._ref_edit.setPlaceholderText(info.branch)
                self._ok_btn.setEnabled(True)
        except ValueError as exc:
            self._info = None
            self._status_label.setStyleSheet("color: #e57373; font-size: 12px;")
            self._status_label.setText(str(exc))
            self._ok_btn.setEnabled(False)

    def _on_branch_detected(self, branch: str) -> None:
        if self._info is None:
            return
        if branch:
            self._info.branch = branch
            if not self._ref_edit.text():
                self._ref_edit.setPlaceholderText(branch)
            self._status_label.setStyleSheet("color: #4caf50; font-size: 12px;")
            host_hint = (
                f" ({self._info.base_url})"
                if self._info.platform in ("github_enterprise", "bitbucket_server")
                else ""
            )
            self._status_label.setText(
                f"{self._info.platform}{host_hint} · "
                f"{self._info.owner}/{self._info.repo} · {self._info.file_path}"
            )
            self._ok_btn.setEnabled(True)
        else:
            # Detection failed — let the user type the branch manually
            self._ref_edit.setPlaceholderText(tr("enter branch name"))
            self._status_label.setStyleSheet("color: #e57373; font-size: 12px;")
            self._status_label.setText(
                tr("Could not detect default branch. Enter it manually above.")
            )
            self._ok_btn.setEnabled(True)

    def get_info(self) -> GitFileInfo | None:
        """Return the parsed GitFileInfo, applying any ref override."""
        if self._info is None:
            return None
        ref = self._ref_edit.text().strip()
        if ref:
            self._info.branch = ref
        return self._info


class GitOpenFolderDialog(QDialog):
    """Dialog for entering a GitHub/Bitbucket repository URL to open as a folder."""

    def __init__(self, settings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Open Git Branch"))
        self.setMinimumWidth(520)
        self._info: GitFileInfo | None = None
        self._settings = settings
        self._branch_worker: _BranchDetectWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        form = QFormLayout()

        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("https://github.com/owner/repo")
        form.addRow(tr("GitHub / Bitbucket repository URL:"), self._url_edit)

        self._ref_edit = QLineEdit()
        self._ref_edit.setPlaceholderText("(auto-detected)")
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
        if self._branch_worker and self._branch_worker.isRunning():
            self._branch_worker.detected.disconnect()
            self._branch_worker.quit()
            self._branch_worker = None

        text = text.strip()
        if not text:
            self._status_label.setText("")
            self._ok_btn.setEnabled(False)
            self._info = None
            return
        try:
            info = parse_git_repo_url(text)
            self._info = info
            host_hint = (
                f" ({info.base_url})"
                if info.platform in ("github_enterprise", "bitbucket_server")
                else ""
            )
            summary = f"{info.platform}{host_hint} · {info.owner}/{info.repo}"

            if not info.branch:
                self._status_label.setStyleSheet("color: #888; font-size: 12px;")
                self._status_label.setText(tr("Detecting default branch…") + "  " + summary)
                self._ref_edit.setPlaceholderText(tr("detecting…"))
                self._ok_btn.setEnabled(False)
                self._branch_worker = _BranchDetectWorker(info, self._settings, self)
                self._branch_worker.detected.connect(self._on_branch_detected)
                self._branch_worker.start()
            else:
                self._status_label.setStyleSheet("color: #4caf50; font-size: 12px;")
                self._status_label.setText(summary)
                if not self._ref_edit.text():
                    self._ref_edit.setPlaceholderText(info.branch)
                self._ok_btn.setEnabled(True)
        except ValueError as exc:
            self._info = None
            self._status_label.setStyleSheet("color: #e57373; font-size: 12px;")
            self._status_label.setText(str(exc))
            self._ok_btn.setEnabled(False)

    def _on_branch_detected(self, branch: str) -> None:
        if self._info is None:
            return
        host_hint = (
            f" ({self._info.base_url})"
            if self._info.platform in ("github_enterprise", "bitbucket_server")
            else ""
        )
        summary = f"{self._info.platform}{host_hint} · {self._info.owner}/{self._info.repo}"
        if branch:
            self._info.branch = branch
            if not self._ref_edit.text():
                self._ref_edit.setPlaceholderText(branch)
            self._status_label.setStyleSheet("color: #4caf50; font-size: 12px;")
            self._status_label.setText(summary)
            self._ok_btn.setEnabled(True)
        else:
            self._ref_edit.setPlaceholderText(tr("enter branch name"))
            self._status_label.setStyleSheet("color: #e57373; font-size: 12px;")
            self._status_label.setText(
                tr("Could not detect default branch. Enter it manually above.")
            )
            self._ok_btn.setEnabled(True)

    def get_info(self) -> GitFileInfo | None:
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


class _BranchListWorker(QThread):
    """Background thread that fetches the list of remote branches."""
    finished = pyqtSignal(list)   # list[str]
    failed   = pyqtSignal(str)

    def __init__(self, info: GitFileInfo, settings, parent=None) -> None:
        super().__init__(parent)
        self._info     = info
        self._settings = settings

    def run(self) -> None:
        try:
            branches = fetch_branches(self._info, self._settings)
            self.finished.emit(branches)
        except Exception as exc:
            self.failed.emit(str(exc))


class GitBranchSwitchDialog(QDialog):
    """Dialog for switching branches or pulling latest changes."""

    def __init__(self, info: GitFileInfo, settings, parent=None) -> None:
        super().__init__(parent)
        self._info     = info
        self._settings = settings
        self._action:  str = ""       # "switch" or "pull"
        self._branch:  str = ""
        self._worker: _BranchListWorker | None = None
        self.setWindowTitle(tr("Switch Branch"))
        self.setMinimumWidth(420)
        self.setMinimumHeight(360)
        self._build_ui()
        self._load_branches()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Current branch header
        self._lbl_current = QLabel(
            tr("Current branch: <b>{branch}</b>", branch=self._info.branch)
        )
        layout.addWidget(self._lbl_current)

        # Pull Latest button
        self._pull_btn = QPushButton(tr("Pull Latest"))
        self._pull_btn.setToolTip(
            tr("Pull latest changes for '{branch}'", branch=self._info.branch)
        )
        self._pull_btn.clicked.connect(self._on_pull)
        layout.addWidget(self._pull_btn)

        # Filter
        self._filter_edit = QLineEdit()
        self._filter_edit.setPlaceholderText(tr("Filter branches …"))
        self._filter_edit.textChanged.connect(self._apply_filter)
        layout.addWidget(self._filter_edit)

        # Branch list
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self._list)

        # Status
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._status_lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        self._switch_btn = QPushButton(tr("Switch"))
        self._switch_btn.setDefault(True)
        self._switch_btn.setEnabled(False)
        self._switch_btn.clicked.connect(self._on_switch)
        cancel_btn = QPushButton(tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self._switch_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self._list.currentItemChanged.connect(self._on_selection_changed)

    def _load_branches(self) -> None:
        self._status_lbl.setStyleSheet("color: #888; font-size: 12px;")
        self._status_lbl.setText(tr("Loading …"))
        self._worker = _BranchListWorker(self._info, self._settings, self)
        self._worker.finished.connect(self._on_branches_loaded)
        self._worker.failed.connect(self._on_branches_failed)
        self._worker.start()

    def _on_branches_loaded(self, branches: list) -> None:
        self._worker = None
        self._all_branches = branches
        self._populate(branches)
        self._status_lbl.setStyleSheet("color: #888; font-size: 12px;")
        self._status_lbl.setText(
            tr("{n} branches found", n=len(branches))
        )

    def _on_branches_failed(self, msg: str) -> None:
        self._worker = None
        self._status_lbl.setStyleSheet("color: #e57373; font-size: 12px;")
        self._status_lbl.setText(msg)

    def _populate(self, branches: list[str]) -> None:
        from PyQt6.QtWidgets import QListWidgetItem
        from PyQt6.QtGui import QFont
        self._list.clear()
        for name in branches:
            if name == self._info.branch:
                label = f"{name}  ({tr('current')})"
            else:
                label = name
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, name)
            if name == self._info.branch:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self._list.addItem(item)

    def _apply_filter(self, text: str) -> None:
        text = text.strip().lower()
        if not hasattr(self, "_all_branches"):
            return
        if not text:
            self._populate(self._all_branches)
        else:
            filtered = [b for b in self._all_branches if text in b.lower()]
            self._populate(filtered)

    def _on_selection_changed(self) -> None:
        item = self._list.currentItem()
        if item is None:
            self._switch_btn.setEnabled(False)
            return
        branch = item.data(Qt.ItemDataRole.UserRole)
        self._switch_btn.setEnabled(branch != self._info.branch)

    def _on_double_click(self, item) -> None:
        branch = item.data(Qt.ItemDataRole.UserRole)
        if branch and branch != self._info.branch:
            self._action = "switch"
            self._branch = branch
            self.accept()

    def _on_switch(self) -> None:
        item = self._list.currentItem()
        if item is None:
            return
        branch = item.data(Qt.ItemDataRole.UserRole)
        if branch == self._info.branch:
            return
        self._action = "switch"
        self._branch = branch
        self.accept()

    def _on_pull(self) -> None:
        self._action = "pull"
        self._branch = self._info.branch
        self.accept()

    def get_result(self) -> tuple[str, str]:
        """Return (action, branch).  action is 'switch' or 'pull'."""
        return self._action, self._branch
