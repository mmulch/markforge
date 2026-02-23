"""Main window of the Markdown editor."""

from __future__ import annotations

import os
import shutil

from PyQt6.QtCore import QSettings, QThread, QTimer, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QSplitter,
    QToolBar,
)

from editor_widget import EditorWidget
from file_tree_widget import FileTreeWidget
from git_dialogs import GitCommitDialog, GitOpenDialog, GitSquashDialog
from git_manager import GitFileInfo, CommitSpec  # noqa: F401
from i18n import tr
from insert_media_dialogs import InsertImageDialog, InsertLinkDialog
from insert_plantuml_dialog import InsertPlantUMLDialog
from insert_table_dialog import InsertTableDialog
from markdown_help_dialog import MarkdownHelpDialog
from plantuml_help_dialog import PlantUMLHelpDialog
from preview_widget import PreviewWidget
from settings_dialog import SettingsDialog


class _PdfWorker(QThread):
    """Runs pymupdf4llm.to_markdown() in a background thread."""

    finished = pyqtSignal(str)
    failed   = pyqtSignal(str, bool)   # message, is_import_error

    def __init__(self, path: str, parent=None) -> None:
        super().__init__(parent)
        self._path = path

    def run(self) -> None:
        try:
            import pymupdf4llm
            self.finished.emit(pymupdf4llm.to_markdown(self._path))
        except ImportError:
            self.failed.emit("", True)
        except Exception as exc:
            self.failed.emit(str(exc), False)


class _GitCloneWorker(QThread):
    """Clones a git repo in the background and resolves the target file path."""

    finished = pyqtSignal(object)        # GitFileInfo with local_* fields set
    failed   = pyqtSignal(str, str)      # error message, tmpdir (for cleanup)
    progress = pyqtSignal(int, str)      # percent, status message

    def __init__(self, info: GitFileInfo, settings: QSettings, parent=None) -> None:
        super().__init__(parent)
        self._info     = info
        self._settings = settings

    def run(self) -> None:
        from git_manager import clone_repo
        tmpdir = ""
        try:
            tmpdir = clone_repo(self._info, self._settings, self._on_progress)
            local_file = os.path.join(tmpdir, self._info.file_path)
            if not os.path.isfile(local_file):
                raise FileNotFoundError(
                    tr("File not found in repository:\n{path}", path=self._info.file_path)
                )
            self._info.local_repo_path = tmpdir
            self._info.local_file_path = local_file
            self.finished.emit(self._info)
        except Exception as exc:
            self.failed.emit(str(exc), tmpdir)

    def _on_progress(self, pct: int, msg: str) -> None:
        self.progress.emit(pct, msg)


class _GitPushWorker(QThread):
    """Commits and pushes changes in the background."""

    finished = pyqtSignal()
    failed   = pyqtSignal(str)
    progress = pyqtSignal(int, str)

    def __init__(
        self,
        info:     GitFileInfo,
        spec:     CommitSpec,
        settings: QSettings,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._info     = info
        self._spec     = spec
        self._settings = settings

    def run(self) -> None:
        from git_manager import commit_and_push
        try:
            commit_and_push(self._info, self._spec, self._settings, self._on_progress)
            self.finished.emit()
        except Exception as exc:
            self.failed.emit(str(exc))

    def _on_progress(self, pct: int, msg: str) -> None:
        self.progress.emit(pct, msg)


class _GitSquashWorker(QThread):
    """Squashes and force-pushes commits in the background."""

    finished = pyqtSignal()
    failed   = pyqtSignal(str)
    progress = pyqtSignal(int, str)

    def __init__(self, info: GitFileInfo, squash_count: int,
                 message: str, settings: QSettings, parent=None) -> None:
        super().__init__(parent)
        self._info         = info
        self._squash_count = squash_count
        self._message      = message
        self._settings     = settings

    def run(self) -> None:
        from git_manager import squash_and_push
        try:
            squash_and_push(self._info, self._squash_count,
                            self._message, self._settings, self._on_progress)
            self.finished.emit()
        except Exception as exc:
            self.failed.emit(str(exc))

    def _on_progress(self, pct: int, msg: str) -> None:
        self.progress.emit(pct, msg)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._file:       str | None = None
        self._draft_name: str | None = None
        self._modified = False
        self._settings = QSettings("MarkdownEditor", "MarkdownEditor")

        self._pdf_worker:      _PdfWorker | None      = None
        self._pdf_progress:    QProgressDialog | None = None
        self._pdf_output_path: str                    = ""

        self._git_file_info:      GitFileInfo | None      = None
        self._git_clone_worker:   _GitCloneWorker | None  = None
        self._git_clone_progress: QProgressDialog | None  = None
        self._git_push_worker:    _GitPushWorker | None    = None
        self._git_push_progress:  QProgressDialog | None  = None
        self._git_squash_worker:  _GitSquashWorker | None = None
        self._git_squash_progress: QProgressDialog | None = None
        # Per-session push tracking (reset when a new git file is opened)
        self._git_push_count:        int = 0
        self._git_last_commit_msg:   str = ""
        self._git_pending_commit_msg: str = ""

        self._build_ui()
        self._build_menu()
        self._build_toolbar()
        self._build_statusbar()
        self._connect_signals()
        self._restore_settings()

        self.resize(1280, 800)
        self._update_title()
        self._set_editor_active(False)

    # ── UI setup ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._editor   = EditorWidget()
        self._preview  = PreviewWidget()
        self._splitter.addWidget(self._editor)
        self._splitter.addWidget(self._preview)
        self._splitter.setSizes([640, 640])

        self._outer_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._file_tree = FileTreeWidget()
        self._file_tree.set_root(os.getcwd())
        self._outer_splitter.addWidget(self._file_tree)
        self._outer_splitter.addWidget(self._splitter)
        self._outer_splitter.setSizes([200, 1080])
        self._outer_splitter.setStretchFactor(0, 0)
        self._outer_splitter.setStretchFactor(1, 1)

        self.setCentralWidget(self._outer_splitter)

    def _build_menu(self) -> None:
        mb = self.menuBar()

        # ── File ───────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&File"))
        self._act_new         = self._mk_action(tr("&New"),            QKeySequence.StandardKey.New,  m)
        self._act_open        = self._mk_action(tr("&Open …"),        QKeySequence.StandardKey.Open, m)
        self._act_open_folder = self._mk_action(tr("Open &Folder …"), "Ctrl+Shift+O",                m)
        self._act_import_pdf  = self._mk_action(tr("&Import PDF …"),  "Ctrl+Shift+I",                m)
        self._act_open_git    = self._mk_action(tr("Open from &Git …"), "Ctrl+Shift+G",              m)
        self._act_git_squash  = self._mk_action(tr("Git &Squash …"),   "Ctrl+Shift+Q",              m)
        self._act_git_squash.setEnabled(False)
        m.addSeparator()
        self._act_save    = self._mk_action(tr("&Save"),           QKeySequence.StandardKey.Save,   m)
        self._act_save_as = self._mk_action(tr("Save &As …"),      QKeySequence.StandardKey.SaveAs, m)
        self._act_export_pdf = self._mk_action(tr("Export as PDF …"), "Ctrl+Shift+E", m)
        m.addSeparator()
        quit_act = self._mk_action(tr("&Quit"), QKeySequence.StandardKey.Quit, m)
        quit_act.triggered.connect(self.close)

        # ── Edit ───────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&Edit"))
        undo  = self._mk_action(tr("&Undo"),  QKeySequence.StandardKey.Undo,  m)
        redo  = self._mk_action(tr("&Redo"),  QKeySequence.StandardKey.Redo,  m)
        m.addSeparator()
        cut   = self._mk_action(tr("Cu&t"),   QKeySequence.StandardKey.Cut,   m)
        copy  = self._mk_action(tr("&Copy"),  QKeySequence.StandardKey.Copy,  m)
        paste = self._mk_action(tr("&Paste"), QKeySequence.StandardKey.Paste, m)
        undo.triggered.connect(self._editor.undo)
        redo.triggered.connect(self._editor.redo)
        cut.triggered.connect(self._editor.cut)
        copy.triggered.connect(self._editor.copy)
        paste.triggered.connect(self._editor.paste)

        # ── Insert ─────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&Insert"))
        self._act_insert_link     = self._mk_action(tr("&Link …"),      "Ctrl+K",       m)
        self._act_insert_image    = self._mk_action(tr("&Image …"),     "Ctrl+Shift+K", m)
        self._act_insert_plantuml = self._mk_action(tr("&PlantUML …"),  "Ctrl+Shift+U", m)
        m.addSeparator()
        self._act_insert_table    = self._mk_action(tr("&Table …"),     "Ctrl+Shift+T", m)

        # ── View ───────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&View"))
        self._act_filetree = self._mk_action(
            tr("Show file tree"), "Ctrl+B", m, checkable=True
        )
        self._act_filetree.setChecked(True)
        self._act_preview = self._mk_action(
            tr("Show preview"), "Ctrl+Shift+P", m, checkable=True
        )
        self._act_preview.setChecked(True)
        m.addSeparator()
        self._act_wrap = self._mk_action(tr("Word wrap"), None, m, checkable=True)
        self._act_wrap.setChecked(True)
        m.addSeparator()
        settings_act = self._mk_action(tr("Settings …"), None, m)
        settings_act.triggered.connect(self._open_settings)

        # ── Help ───────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&Help"))
        markdown_help = self._mk_action(tr("&Markdown …"), None, m)
        markdown_help.triggered.connect(self._show_markdown_help)
        plantuml_help = self._mk_action(tr("&PlantUML …"), None, m)
        plantuml_help.triggered.connect(self._show_plantuml_help)
        m.addSeparator()
        about = self._mk_action(tr("&About …"), None, m)
        about.triggered.connect(self._about)

    def _build_toolbar(self) -> None:
        tb = QToolBar(tr("Toolbar"))
        tb.setMovable(False)
        self.addToolBar(tb)
        tb.addAction(self._act_new)
        tb.addAction(self._act_open)
        tb.addAction(self._act_save)
        tb.addSeparator()
        tb.addAction(self._act_preview)

    def _build_statusbar(self) -> None:
        self._lbl_words = QLabel(tr("{n} words", n=0))
        self._lbl_pos   = QLabel(tr("Line {line}, Col {col}", line=1, col=1))
        sb = self.statusBar()
        sb.addPermanentWidget(self._lbl_words)
        sb.addPermanentWidget(self._lbl_pos)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _mk_action(
        self,
        label: str,
        shortcut: QKeySequence.StandardKey | str | None,
        menu,
        *,
        checkable: bool = False,
    ) -> QAction:
        act = QAction(label, self)
        if shortcut is not None:
            act.setShortcut(QKeySequence(shortcut))
        act.setCheckable(checkable)
        menu.addAction(act)
        return act

    # ── Signal connections ────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._act_new.triggered.connect(self._new)
        self._act_open.triggered.connect(self._open)
        self._act_open_folder.triggered.connect(self._open_folder)
        self._act_import_pdf.triggered.connect(self._import_pdf)
        self._act_open_git.triggered.connect(self._open_from_git)
        self._act_git_squash.triggered.connect(self._git_squash)
        self._act_save.triggered.connect(self._save)
        self._act_save_as.triggered.connect(self._save_as)
        self._act_export_pdf.triggered.connect(self._export_pdf)
        self._preview.pdf_saved.connect(self._on_pdf_saved)
        self._act_insert_link.triggered.connect(self._insert_link)
        self._act_insert_image.triggered.connect(self._insert_image)
        self._act_insert_plantuml.triggered.connect(self._insert_plantuml)
        self._act_insert_table.triggered.connect(self._insert_table)
        self._act_filetree.toggled.connect(self._file_tree.setVisible)
        self._act_preview.toggled.connect(self._preview.setVisible)
        self._act_wrap.toggled.connect(self._editor.set_word_wrap)
        self._file_tree.file_activated.connect(self._load)
        self._preview.open_file.connect(self._load)

        self._editor.textChanged.connect(self._on_change)
        self._editor.cursorPositionChanged.connect(self._update_pos)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._refresh_preview)

    # ── Slots / callbacks ─────────────────────────────────────────────────────

    def _on_change(self) -> None:
        self._modified = True
        self._update_title()
        self._update_words()
        self._timer.start()

    def _refresh_preview(self) -> None:
        self._preview.set_markdown(self._editor.toPlainText(), self._doc_base_url())

    def _doc_base_url(self) -> QUrl:
        """Base URL for the preview: directory of the currently open file."""
        if self._file:
            directory = os.path.dirname(os.path.abspath(self._file))
        else:
            directory = os.path.abspath(os.getcwd())
        return QUrl.fromLocalFile(directory + "/")

    def _update_pos(self) -> None:
        cur = self._editor.textCursor()
        self._lbl_pos.setText(
            tr("Line {line}, Col {col}",
               line=cur.blockNumber() + 1,
               col=cur.columnNumber() + 1)
        )

    def _update_words(self) -> None:
        txt = self._editor.toPlainText().strip()
        n   = len(txt.split()) if txt else 0
        self._lbl_words.setText(tr("{n} words", n=n))

    def _set_editor_active(self, active: bool) -> None:
        """Enable/disable the editor and all actions that require an open document."""
        self._editor.setEnabled(active)
        self._editor.setPlaceholderText(
            "" if active
            else "\n" + tr("Open or create a Markdown file to start editing.")
        )
        for act in (
            self._act_save, self._act_save_as, self._act_export_pdf,
            self._act_insert_link, self._act_insert_image,
            self._act_insert_plantuml, self._act_insert_table,
        ):
            act.setEnabled(active)

    def _update_title(self) -> None:
        name = (
            os.path.basename(self._file) if self._file
            else (self._draft_name or tr("Untitled"))
        )
        mod  = "*" if self._modified else ""
        self.setWindowTitle(f"{mod}{name} — MarkForge")

    # ── File operations ───────────────────────────────────────────────────────

    def _new(self) -> None:
        if not self._maybe_save():
            return
        save_dir = self._file_tree._root_dir or os.getcwd()
        name, ok = QInputDialog.getText(
            self, tr("New File"),
            tr("File name:\nFolder: {path}", path=save_dir),
            text="Untitled.md",
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        if "." not in name:
            name += ".md"
        full_path = os.path.join(save_dir, name)
        if not os.path.exists(full_path):
            try:
                with open(full_path, "w", encoding="utf-8"):
                    pass
            except OSError as exc:
                QMessageBox.critical(
                    self, tr("Error"),
                    tr("Could not create file:\n{exc}", exc=exc),
                )
                return
        self._load(full_path)

    def _open(self) -> None:
        if not self._maybe_save():
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Open File"),
            "",
            tr("Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*)"),
        )
        if path:
            self._load(path)

    def _open_folder(self) -> None:
        if not self._maybe_save():
            return
        path = QFileDialog.getExistingDirectory(self, tr("Open Folder"))
        if path:
            self._file_tree.set_root(path)
            self._file_tree.setVisible(True)
            self._act_filetree.setChecked(True)

    def _import_pdf(self) -> None:
        if self._pdf_worker is not None:
            return  # import already running
        if not self._maybe_save():
            return

        # ── Step 1: choose PDF ─────────────────────────────────────────────
        pdf_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Import PDF"),
            "",
            tr("PDF files (*.pdf);;All files (*)"),
        )
        if not pdf_path:
            return

        # ── Step 2: choose output file name ───────────────────────────────
        save_dir   = self._file_tree._root_dir or os.getcwd()
        draft_name = os.path.splitext(os.path.basename(pdf_path))[0] + ".md"
        name, ok = QInputDialog.getText(
            self, tr("Import PDF"),
            tr("File name:\nFolder: {path}", path=save_dir),
            text=draft_name,
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        if "." not in name:
            name += ".md"
        self._pdf_output_path = os.path.join(save_dir, name)

        # ── Step 3: show progress dialog and start worker ─────────────────
        self._pdf_progress = QProgressDialog(
            tr("Importing PDF …"), tr("Cancel"), 0, 0, self
        )
        self._pdf_progress.setWindowTitle(tr("Import PDF"))
        self._pdf_progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._pdf_progress.setAutoClose(False)
        self._pdf_progress.setAutoReset(False)
        self._pdf_progress.canceled.connect(self._on_pdf_canceled)
        self._pdf_progress.show()

        self._pdf_worker = _PdfWorker(pdf_path, self)
        self._pdf_worker.finished.connect(self._on_pdf_done)
        self._pdf_worker.failed.connect(self._on_pdf_failed)
        self._pdf_worker.start()

    def _on_pdf_done(self, md: str) -> None:
        """Called in the main thread when PDF conversion succeeds."""
        self._pdf_progress.close()
        self._pdf_progress = None
        self._pdf_worker   = None

        if not md:
            QMessageBox.critical(
                self, tr("Error"),
                tr("The PDF could not be converted (no readable text found)."),
            )
            return

        try:
            with open(self._pdf_output_path, "w", encoding="utf-8") as fh:
                fh.write(md)
        except OSError as exc:
            QMessageBox.critical(
                self, tr("Error"),
                tr("Could not write file:\n{exc}", exc=exc),
            )
            return

        self._load(self._pdf_output_path)

    def _on_pdf_failed(self, msg: str, is_import: bool) -> None:
        """Called in the main thread when PDF conversion fails."""
        self._pdf_progress.close()
        self._pdf_progress = None
        self._pdf_worker   = None

        if is_import:
            QMessageBox.critical(
                self, tr("Error"),
                tr("pymupdf4llm is not installed.\nInstall it with: pip install pymupdf4llm"),
            )
        else:
            QMessageBox.critical(
                self, tr("Error"),
                tr("Could not import PDF:\n{exc}", exc=msg),
            )

    def _on_pdf_canceled(self) -> None:
        """Called when the user clicks Cancel in the progress dialog."""
        if self._pdf_worker is not None:
            self._pdf_worker.finished.disconnect(self._on_pdf_done)
            self._pdf_worker.failed.disconnect(self._on_pdf_failed)
            self._pdf_worker.terminate()
            self._pdf_worker.wait()
            self._pdf_worker = None
        if self._pdf_progress is not None:
            self._pdf_progress.close()
            self._pdf_progress = None

    # ── Git open ──────────────────────────────────────────────────────────────

    def _open_from_git(self) -> None:
        if self._git_clone_worker is not None:
            return  # clone already running

        if not self._maybe_save():
            return

        # Warn if no credentials configured (non-blocking — user can continue)
        s = QSettings("MarkdownEditor", "MarkdownEditor")
        user  = s.value("git/https_username", "")
        token = s.value("git/https_token",    "")
        key   = s.value("git/ssh_key_path",   "")
        if not user and not token and not key:
            reply = QMessageBox.information(
                self,
                tr("Open from Git"),
                tr(
                    "No credentials configured. Public repositories will still work.\n"
                    "Configure credentials in View → Settings."
                ),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return

        dlg = GitOpenDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        info = dlg.get_info()
        if info is None:
            return

        self._git_clone_progress = QProgressDialog(
            tr("Cloning repository …"), tr("Cancel"), 0, 100, self
        )
        self._git_clone_progress.setWindowTitle(tr("Open from Git"))
        self._git_clone_progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._git_clone_progress.setAutoClose(False)
        self._git_clone_progress.setAutoReset(False)
        self._git_clone_progress.canceled.connect(self._on_clone_canceled)
        self._git_clone_progress.show()

        self._git_clone_worker = _GitCloneWorker(info, s, self)
        self._git_clone_worker.finished.connect(self._on_clone_done)
        self._git_clone_worker.failed.connect(self._on_clone_failed)
        self._git_clone_worker.progress.connect(self._on_clone_progress)
        self._git_clone_worker.start()

    def _on_clone_progress(self, pct: int, msg: str) -> None:
        dlg = self._git_clone_progress
        if dlg is not None:
            dlg.setValue(pct)
            if msg:
                dlg.setLabelText(tr("Cloning repository …") + f"\n{msg}")

    def _on_clone_done(self, info: GitFileInfo) -> None:
        if self._git_clone_progress is not None:
            self._git_clone_progress.close()
            self._git_clone_progress = None
        self._git_clone_worker = None
        self._git_file_info = info
        # Reset per-session push tracking for this new git session
        self._git_push_count         = 0
        self._git_last_commit_msg    = ""
        self._git_pending_commit_msg = ""
        self._update_squash_action()
        self._load(info.local_file_path)
        # Re-apply git marker (set_root inside _load clears it)
        self._file_tree.mark_git_root(info.local_repo_path, info.repo)

    def _on_clone_failed(self, msg: str, tmpdir: str) -> None:
        if self._git_clone_progress is not None:
            self._git_clone_progress.close()
            self._git_clone_progress = None
        self._git_clone_worker = None
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        QMessageBox.critical(
            self, tr("Open from Git"), tr("Clone failed:\n{exc}", exc=msg)
        )

    def _on_clone_canceled(self) -> None:
        if self._git_clone_worker is not None:
            try:
                self._git_clone_worker.finished.disconnect(self._on_clone_done)
                self._git_clone_worker.failed.disconnect(self._on_clone_failed)
                self._git_clone_worker.progress.disconnect(self._on_clone_progress)
            except RuntimeError:
                pass
            self._git_clone_worker.terminate()
            self._git_clone_worker.wait()
            self._git_clone_worker = None
        if self._git_clone_progress is not None:
            self._git_clone_progress.close()
            self._git_clone_progress = None

    # ── Git save (commit & push) ───────────────────────────────────────────────

    def _git_save(self) -> None:
        if self._git_push_worker is not None:
            return  # push already running
        if self._git_file_info is None:
            return

        s_amend = QSettings("MarkdownEditor", "MarkdownEditor")
        amend_available = (
            s_amend.value("git/auth_method", "https") in ("ssh", "git")
            and self._git_push_count >= 1
        )
        dlg = GitCommitDialog(
            self._git_file_info, self,
            amend_available=amend_available,
            prev_message=self._git_last_commit_msg,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        spec = dlg.get_spec()
        self._git_pending_commit_msg = spec.message

        self._git_push_progress = QProgressDialog(
            tr("Pushing to remote …"), tr("Cancel"), 0, 100, self
        )
        self._git_push_progress.setWindowTitle(tr("Git Push"))
        self._git_push_progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._git_push_progress.setAutoClose(False)
        self._git_push_progress.setAutoReset(False)
        self._git_push_progress.canceled.connect(self._on_push_canceled)
        self._git_push_progress.show()

        s = QSettings("MarkdownEditor", "MarkdownEditor")
        self._git_push_worker = _GitPushWorker(self._git_file_info, spec, s, self)
        self._git_push_worker.finished.connect(self._on_push_done)
        self._git_push_worker.failed.connect(self._on_push_failed)
        self._git_push_worker.progress.connect(self._on_push_progress)
        self._git_push_worker.start()

    def _on_push_progress(self, pct: int, msg: str) -> None:
        dlg = self._git_push_progress
        if dlg is not None:
            dlg.setValue(pct)
            if msg:
                dlg.setLabelText(tr("Pushing to remote …") + f"\n{msg}")

    def _on_push_done(self) -> None:
        if self._git_push_progress is not None:
            self._git_push_progress.close()
            self._git_push_progress = None
        self._git_push_worker = None
        self._git_push_count += 1
        self._git_last_commit_msg   = self._git_pending_commit_msg
        self._git_pending_commit_msg = ""
        self.statusBar().showMessage(tr("Pushed to remote."), 4000)

    def _on_push_failed(self, msg: str) -> None:
        if self._git_push_progress is not None:
            self._git_push_progress.close()
            self._git_push_progress = None
        self._git_push_worker = None

        msg_lower = msg.lower()
        if "rejected" in msg_lower or "non-fast-forward" in msg_lower:
            QMessageBox.warning(
                self,
                tr("Git Push"),
                tr("Push rejected (non-fast-forward).\nTry saving again using 'New branch'."),
            )
        else:
            QMessageBox.critical(
                self, tr("Git Push"), tr("Git push failed:\n{exc}", exc=msg)
            )

    def _on_push_canceled(self) -> None:
        if self._git_push_worker is not None:
            try:
                self._git_push_worker.finished.disconnect(self._on_push_done)
                self._git_push_worker.failed.disconnect(self._on_push_failed)
                self._git_push_worker.progress.disconnect(self._on_push_progress)
            except RuntimeError:
                pass
            self._git_push_worker.terminate()
            self._git_push_worker.wait()
            self._git_push_worker = None
        if self._git_push_progress is not None:
            self._git_push_progress.close()
            self._git_push_progress = None

    # ── Git squash ────────────────────────────────────────────────────────────

    def _update_squash_action(self) -> None:
        s = QSettings("MarkdownEditor", "MarkdownEditor")
        enabled = (
            self._git_file_info is not None
            and s.value("git/auth_method", "https") in ("ssh", "git")
        )
        self._act_git_squash.setEnabled(enabled)

    def _git_squash(self) -> None:
        if self._git_squash_worker is not None:
            return
        if self._git_file_info is None:
            return

        s = QSettings("MarkdownEditor", "MarkdownEditor")
        if s.value("git/auth_method", "https") not in ("ssh", "git"):
            QMessageBox.information(
                self, tr("Git Squash Commits"),
                tr("Git squash is only available with SSH or git-binary authentication."),
            )
            return

        dlg = GitSquashDialog(self._git_file_info, s, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        squash_count, message = dlg.get_result()

        self._git_squash_progress = QProgressDialog(
            tr("Squashing commits …"), tr("Cancel"), 0, 100, self
        )
        self._git_squash_progress.setWindowTitle(tr("Git Squash Commits"))
        self._git_squash_progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._git_squash_progress.setAutoClose(False)
        self._git_squash_progress.setAutoReset(False)
        self._git_squash_progress.canceled.connect(self._on_squash_canceled)
        self._git_squash_progress.show()

        self._git_squash_worker = _GitSquashWorker(
            self._git_file_info, squash_count, message, s, self
        )
        self._git_squash_worker.finished.connect(self._on_squash_done)
        self._git_squash_worker.failed.connect(self._on_squash_failed)
        self._git_squash_worker.progress.connect(self._on_squash_progress)
        self._git_squash_worker.start()

    def _on_squash_progress(self, pct: int, msg: str) -> None:
        dlg = self._git_squash_progress
        if dlg is not None:
            dlg.setValue(pct)
            if msg:
                dlg.setLabelText(tr("Squashing commits …") + f"\n{msg}")

    def _on_squash_done(self) -> None:
        if self._git_squash_progress is not None:
            self._git_squash_progress.close()
            self._git_squash_progress = None
        self._git_squash_worker = None
        # After squash there is exactly one MarkForge commit on the branch
        self._git_push_count      = 1
        self._git_last_commit_msg = ""
        self.statusBar().showMessage(tr("Squash complete."), 4000)

    def _on_squash_failed(self, msg: str) -> None:
        if self._git_squash_progress is not None:
            self._git_squash_progress.close()
            self._git_squash_progress = None
        self._git_squash_worker = None
        QMessageBox.critical(
            self, tr("Git Squash Commits"),
            tr("Git squash failed:\n{exc}", exc=msg),
        )

    def _on_squash_canceled(self) -> None:
        if self._git_squash_worker is not None:
            try:
                self._git_squash_worker.finished.disconnect(self._on_squash_done)
                self._git_squash_worker.failed.disconnect(self._on_squash_failed)
                self._git_squash_worker.progress.disconnect(self._on_squash_progress)
            except RuntimeError:
                pass
            self._git_squash_worker.terminate()
            self._git_squash_worker.wait()
            self._git_squash_worker = None
        if self._git_squash_progress is not None:
            self._git_squash_progress.close()
            self._git_squash_progress = None

    def _load(self, path: str) -> None:
        # Clear git context if we're loading a file outside the current git repo
        if self._git_file_info is not None:
            if not path.startswith(self._git_file_info.local_repo_path):
                self._git_file_info = None
                self._file_tree.clear_git_marker()
                self._update_squash_action()

        try:
            with open(path, encoding="utf-8") as fh:
                self._editor.setPlainText(fh.read())
        except OSError as exc:
            QMessageBox.critical(
                self, tr("Error"), tr("Could not open file:\n{exc}", exc=exc)
            )
            return
        self._file       = path
        self._draft_name = None
        self._modified   = False
        self._set_editor_active(True)
        self._update_title()
        self._file_tree.set_root(os.path.dirname(os.path.abspath(path)))
        self._file_tree.select_file(path)
        self._refresh_preview()

    def _save(self) -> None:
        if self._file and self._git_file_info is not None:
            self._write(self._file)   # persist to local temp file first
            self._git_save()
        elif self._file:
            self._write(self._file)
        else:
            self._save_as()

    def _save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("Save As"),
            self._draft_name or "",
            tr("Markdown files (*.md);;Text files (*.txt);;All files (*)"),
        )
        if path:
            self._write(path)

    def _write(self, path: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._editor.toPlainText())
        except OSError as exc:
            QMessageBox.critical(
                self, tr("Error"), tr("Could not save file:\n{exc}", exc=exc)
            )
            return
        prev_file        = self._file
        self._file       = path
        self._draft_name = None
        self._modified   = False
        self._update_title()
        self.statusBar().showMessage(tr("Saved."), 3000)
        if prev_file is None:
            # First save of a new or imported document → update the tree
            self._file_tree.set_root(os.path.dirname(os.path.abspath(path)))
            self._file_tree.select_file(path)

    def _export_pdf(self) -> None:
        default = ""
        if self._file:
            import os as _os
            base = _os.path.splitext(self._file)[0]
            default = base + ".pdf"
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("Export as PDF"),
            default,
            tr("PDF files (*.pdf);;All files (*)"),
        )
        if path:
            self._preview.export_to_pdf(path)

    def _on_pdf_saved(self, path: str, success: bool) -> None:
        if success:
            self.statusBar().showMessage(tr("PDF saved: {path}", path=path), 5000)
        else:
            QMessageBox.critical(
                self, tr("Error"), tr("Could not save PDF:\n{path}", path=path)
            )

    def _maybe_save(self) -> bool:
        """Returns True if the current content may be discarded."""
        if not self._modified:
            return True
        reply = QMessageBox.question(
            self,
            tr("Unsaved Changes"),
            tr("Do you want to save the changes?"),
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Save:
            self._save()
            return True
        return reply == QMessageBox.StandardButton.Discard

    # ── Settings ──────────────────────────────────────────────────────────────

    def _restore_settings(self) -> None:
        if geo := self._settings.value("geometry"):
            self.restoreGeometry(geo)
        if sizes := self._settings.value("splitter"):
            self._splitter.setSizes([int(s) for s in sizes])
        if sizes := self._settings.value("outer_splitter"):
            self._outer_splitter.setSizes([int(s) for s in sizes])
        self._apply_themes()

    def _apply_themes(self) -> None:
        editor_theme  = self._settings.value("editor_theme",  "VS Code Dark")
        preview_theme = self._settings.value("preview_theme", "GitHub Dark")
        self._editor.set_theme(editor_theme)
        self._preview.set_theme(preview_theme)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._apply_themes()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if not self._maybe_save():
            event.ignore()
            return
        if self._pdf_worker is not None:
            self._pdf_worker.terminate()
            self._pdf_worker.wait()

        # Stop any running git workers
        if self._git_clone_worker is not None:
            self._git_clone_worker.terminate()
            self._git_clone_worker.wait()
        if self._git_push_worker is not None:
            self._git_push_worker.terminate()
            self._git_push_worker.wait()

        # Offer to delete the temporary git clone
        if self._git_file_info is not None:
            tmpdir = self._git_file_info.local_repo_path
            if tmpdir and os.path.isdir(tmpdir):
                reply = QMessageBox.question(
                    self,
                    tr("Delete Git Temp Directory?"),
                    tr(
                        "A temporary Git clone is open:\n{path}\n\nDelete it now?",
                        path=tmpdir,
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    shutil.rmtree(tmpdir, ignore_errors=True)

        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("splitter", self._splitter.sizes())
        self._settings.setValue("outer_splitter", self._outer_splitter.sizes())
        event.accept()

    # ── Insert actions ────────────────────────────────────────────────────────

    def _insert_link(self) -> None:
        selected = self._editor.textCursor().selectedText()
        dlg = InsertLinkDialog(selected_text=selected, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        md = dlg.get_markdown()
        if md:
            self._editor.textCursor().insertText(md)
            self._editor.setFocus()

    def _insert_image(self) -> None:
        selected = self._editor.textCursor().selectedText()
        dlg = InsertImageDialog(selected_text=selected, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        md = dlg.get_markdown()
        if md:
            cursor = self._editor.textCursor()
            prefix = "\n" if cursor.columnNumber() > 0 else ""
            cursor.insertText(f"{prefix}{md}")
            self._editor.setFocus()

    def _insert_plantuml(self) -> None:
        dlg = InsertPlantUMLDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        md = dlg.get_markdown()
        if md:
            cursor = self._editor.textCursor()
            prefix = "\n" if cursor.columnNumber() > 0 else ""
            cursor.insertText(f"{prefix}{md}\n")
            self._editor.setTextCursor(cursor)
            self._editor.setFocus()

    def _insert_table(self) -> None:
        dlg = InsertTableDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        table_md = dlg.get_markdown()
        cursor   = self._editor.textCursor()

        prefix = "\n" if cursor.columnNumber() > 0 else ""
        cursor.insertText(f"{prefix}{table_md}\n")
        self._editor.setTextCursor(cursor)
        self._editor.setFocus()

    # ── Markdown help ─────────────────────────────────────────────────────────

    def _show_markdown_help(self) -> None:
        dlg = MarkdownHelpDialog(self)
        dlg.exec()

    def _show_plantuml_help(self) -> None:
        dlg = PlantUMLHelpDialog(self)
        dlg.exec()

    # ── About ─────────────────────────────────────────────────────────────────

    def _about(self) -> None:
        QMessageBox.about(
            self,
            tr("About MarkForge"),
            tr(
                "<h3>MarkForge 1.0</h3>"
                "<p>Created with <b>Python 3</b> and <b>PyQt6</b>.</p>"
                "<p>Supported extensions:<br>"
                "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
                "<hr>"
                "<p>Copyright &copy; Marcel Mulch</p>"
                "<p>License: GNU General Public License 3.0</p>"
            ),
        )
