"""Main window of the Markdown editor."""

from __future__ import annotations

import os
import shutil
import sys

from PyQt6.QtCore import QEvent, QSettings, QStandardPaths, QThread, QTimer, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QProgressDialog,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from editor_widget import EditorWidget
from file_tree_widget import FileTreeWidget
from find_replace_bar import FindReplaceBar
from outline_widget import OutlineWidget
from git_dialogs import GitCommitDialog, GitOpenDialog, GitOpenFolderDialog, GitSquashDialog
from git_manager import GitFileInfo, CommitSpec  # noqa: F401
from i18n import LANGUAGES, SPELL_CHECK_LANGUAGES, tr
from insert_media_dialogs import InsertImageDialog, InsertLinkDialog
from insert_mermaid_dialog import InsertMermaidDialog
from insert_plantuml_dialog import InsertPlantUMLDialog
from insert_table_dialog import InsertTableDialog
from markdown_help_dialog import MarkdownHelpDialog
from mermaid_help_dialog import MermaidHelpDialog
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


class _GitCloneFolderWorker(QThread):
    """Clones a git repo for folder browsing (no specific file required)."""

    finished = pyqtSignal(object)   # GitFileInfo with local_repo_path set
    failed   = pyqtSignal(str, str) # error message, tmpdir (for cleanup)
    progress = pyqtSignal(int, str) # percent, status message

    def __init__(self, info: GitFileInfo, settings: QSettings, parent=None) -> None:
        super().__init__(parent)
        self._info     = info
        self._settings = settings

    def run(self) -> None:
        from git_manager import clone_repo_full
        tmpdir = ""
        try:
            tmpdir = clone_repo_full(self._info, self._settings, self._on_progress)
            self._info.local_repo_path = tmpdir
            self._info.local_file_path = ""
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
        self._git_folder_root:    str                     = ""
        self._git_clone_worker:   _GitCloneWorker | None  = None
        self._git_clone_progress: QProgressDialog | None  = None
        self._git_clone_folder_worker:   _GitCloneFolderWorker | None = None
        self._git_clone_folder_progress: QProgressDialog | None      = None
        self._git_push_worker:    _GitPushWorker | None    = None
        self._git_push_progress:  QProgressDialog | None  = None
        self._git_squash_worker:  _GitSquashWorker | None = None
        self._git_squash_progress: QProgressDialog | None = None
        # Per-session push tracking (reset when a new git file is opened)
        self._git_push_count:        int = 0
        self._git_last_commit_msg:   str = ""
        self._git_pending_commit_msg: str = ""

        self._recent_files: list[str] = []
        self._word_goal: int = 0
        self._pre_focus: dict = {}

        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave)

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
        self._editor.set_assets_dir_provider(self._get_assets_dir)
        self._preview  = PreviewWidget()
        self._splitter.addWidget(self._editor)
        self._splitter.addWidget(self._preview)
        self._splitter.setSizes([640, 640])

        self._outline   = OutlineWidget()
        self._file_tree = FileTreeWidget()
        self._file_tree.set_root(os.getcwd())

        self._left_splitter = QSplitter(Qt.Orientation.Vertical)
        self._left_splitter.addWidget(self._outline)
        self._left_splitter.addWidget(self._file_tree)
        self._left_splitter.setSizes([200, 400])
        self._left_splitter.setStretchFactor(0, 1)
        self._left_splitter.setStretchFactor(1, 1)

        self._outer_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._outer_splitter.addWidget(self._left_splitter)
        self._outer_splitter.addWidget(self._splitter)
        self._outer_splitter.setSizes([200, 1080])
        self._outer_splitter.setStretchFactor(0, 0)
        self._outer_splitter.setStretchFactor(1, 1)

        self._find_bar = FindReplaceBar(self._editor, self)
        self._find_bar.hide()

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self._find_bar, 0)
        vbox.addWidget(self._outer_splitter, 1)
        self.setCentralWidget(container)

    def _build_menu(self) -> None:
        mb = self.menuBar()

        # ── File ───────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&File"))
        self._act_new         = self._mk_action(tr("&New"),            QKeySequence.StandardKey.New,  m)
        self._act_open        = self._mk_action(tr("&Open …"),        QKeySequence.StandardKey.Open, m)
        self._act_open_folder = self._mk_action(tr("Open &Folder …"), "Ctrl+Shift+O",                m)
        self._act_import_pdf  = self._mk_action(tr("&Import PDF …"),  "Ctrl+Shift+I",                m)
        self._act_open_git        = self._mk_action(tr("Open &File from Git …"),    "Ctrl+Shift+G", m)
        self._act_open_git_folder = self._mk_action(tr("Open Git &Branch …"), None, m)
        self._act_git_squash      = self._mk_action(tr("Git &Squash …"),           "Ctrl+Shift+Q", m)
        self._act_git_squash.setEnabled(False)
        m.addSeparator()
        self._recent_menu = m.addMenu(tr("Recent &Files"))
        self._act_clear_recent = self._recent_menu.addAction(tr("Clear Recent Files"))
        self._act_clear_recent.triggered.connect(self._clear_recent_files)
        self._recent_menu.addSeparator()
        # File entries are inserted above the separator at index 0; rebuilt in
        # _rebuild_recent_menu() whenever the list changes.
        m.addSeparator()
        self._act_save    = self._mk_action(tr("&Save"),           QKeySequence.StandardKey.Save,   m)
        self._act_save_as = self._mk_action(tr("Save &As …"),      QKeySequence.StandardKey.SaveAs, m)
        self._act_export_pdf   = self._mk_action(tr("Export as PDF …"),           "Ctrl+Shift+E", m)
        self._act_export_html  = self._mk_action(tr("Export as HTML …"),           None,           m)
        self._act_export_docx  = self._mk_action(tr("Export as DOCX (Pandoc) …"),  None,           m)
        self._act_export_epub  = self._mk_action(tr("Export as EPUB (Pandoc) …"),  None,           m)
        self._act_export_latex = self._mk_action(tr("Export as LaTeX (Pandoc) …"), None,           m)
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
        m.addSeparator()
        self._act_find    = self._mk_action(tr("&Find …"),             "Ctrl+F", m)
        self._act_replace = self._mk_action(tr("Find && &Replace …"),  "Ctrl+H", m)
        self._act_find.triggered.connect(lambda: self._find_bar.show_find())
        self._act_replace.triggered.connect(lambda: self._find_bar.show_replace())

        # ── Insert ─────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&Insert"))
        self._act_insert_link     = self._mk_action(tr("&Link …"),      "Ctrl+K",       m)
        self._act_insert_image    = self._mk_action(tr("&Image …"),     "Ctrl+Shift+K", m)
        self._act_insert_plantuml = self._mk_action(tr("&PlantUML …"),  "Ctrl+Shift+U", m)
        self._act_insert_mermaid  = self._mk_action(tr("&Mermaid …"),   "Ctrl+Shift+M", m)
        m.addSeparator()
        self._act_insert_table    = self._mk_action(tr("&Table …"),     "Ctrl+Shift+T", m)

        # ── View ───────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&View"))
        self._act_filetree = self._mk_action(
            tr("Show file tree"), "Ctrl+B", m, checkable=True
        )
        self._act_filetree.setChecked(True)
        self._act_outline = self._mk_action(
            tr("Show outline"), None, m, checkable=True
        )
        self._act_outline.setChecked(True)
        self._act_preview = self._mk_action(
            tr("Show preview"), "Ctrl+Shift+P", m, checkable=True
        )
        self._act_preview.setChecked(True)
        self._act_focus = self._mk_action(
            tr("Focus Mode"), "F11", m, checkable=True
        )
        m.addSeparator()
        self._act_wrap = self._mk_action(tr("Word wrap"), None, m, checkable=True)
        self._act_wrap.setChecked(True)
        m.addSeparator()
        self._act_spellcheck = self._mk_action(
            tr("Spell check"), None, m, checkable=True
        )
        self._act_spellcheck.setChecked(False)
        from PyQt6.QtGui import QActionGroup
        self._spell_lang_menu = m.addMenu(tr("Spell check language"))
        self._spell_lang_group = QActionGroup(self)
        self._spell_lang_group.setExclusive(True)
        self._spell_lang_group.triggered.connect(
            lambda a: self._editor.set_spell_check(
                self._act_spellcheck.isChecked(), a.data()
            )
        )
        # Populated dynamically by _rebuild_spell_lang_menu() once settings load
        m.addSeparator()
        self._act_word_goal = self._mk_action(tr("Set Word Goal …"), None, m)
        self._act_word_goal.triggered.connect(self._set_word_goal)
        m.addSeparator()
        settings_act = self._mk_action(tr("Settings …"), None, m)
        settings_act.triggered.connect(self._open_settings)

        # ── Help ───────────────────────────────────────────────────────────
        m = mb.addMenu(tr("&Help"))
        user_manual = self._mk_action(tr("&User Manual …"), None, m)
        user_manual.triggered.connect(self._show_user_manual)
        m.addSeparator()
        markdown_help = self._mk_action(tr("&Markdown …"), None, m)
        markdown_help.triggered.connect(self._show_markdown_help)
        plantuml_help = self._mk_action(tr("&PlantUML …"), None, m)
        plantuml_help.triggered.connect(self._show_plantuml_help)
        mermaid_help = self._mk_action(tr("Mermaid …"), None, m)
        mermaid_help.triggered.connect(self._show_mermaid_help)
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
        self._bar_goal  = QProgressBar()
        self._bar_goal.setFixedWidth(100)
        self._bar_goal.setFixedHeight(14)
        self._bar_goal.setTextVisible(False)
        self._bar_goal.setRange(0, 100)
        self._bar_goal.hide()
        sb = self.statusBar()
        sb.addPermanentWidget(self._lbl_words)
        sb.addPermanentWidget(self._bar_goal)
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
        self._act_open_git_folder.triggered.connect(self._open_folder_from_git)
        self._act_git_squash.triggered.connect(self._git_squash)
        self._act_save.triggered.connect(self._save)
        self._act_save_as.triggered.connect(self._save_as)
        self._act_export_pdf.triggered.connect(self._export_pdf)
        self._act_export_html.triggered.connect(self._export_html)
        self._act_export_docx.triggered.connect(lambda: self._export_pandoc("docx"))
        self._act_export_epub.triggered.connect(lambda: self._export_pandoc("epub"))
        self._act_export_latex.triggered.connect(lambda: self._export_pandoc("latex"))
        self._preview.pdf_saved.connect(self._on_pdf_saved)
        self._act_insert_link.triggered.connect(self._insert_link)
        self._act_insert_image.triggered.connect(self._insert_image)
        self._act_insert_plantuml.triggered.connect(self._insert_plantuml)
        self._act_insert_mermaid.triggered.connect(self._insert_mermaid)
        self._act_insert_table.triggered.connect(self._insert_table)
        self._act_filetree.toggled.connect(self._file_tree.setVisible)
        self._act_outline.toggled.connect(self._outline.setVisible)
        self._act_preview.toggled.connect(self._preview.setVisible)
        self._act_focus.toggled.connect(self._toggle_focus_mode)
        self._act_wrap.toggled.connect(self._editor.set_word_wrap)
        self._act_spellcheck.toggled.connect(
            lambda on: self._editor.set_spell_check(
                on,
                self._spell_lang_group.checkedAction().data()
                if self._spell_lang_group.checkedAction() else "en",
            )
        )
        self._file_tree.file_activated.connect(self._load)
        self._preview.open_file.connect(self._load)
        self._outline.jump_to_line.connect(self._jump_to_outline_line)

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
        text = self._editor.toPlainText()
        self._preview.set_markdown(text, self._doc_base_url())
        self._outline.refresh(text)

    def _jump_to_outline_line(self, lineno: int) -> None:
        """Move the editor cursor to the heading at the given 0-based line."""
        from PyQt6.QtGui import QTextCursor
        block = self._editor.document().findBlockByLineNumber(lineno)
        if block.isValid():
            cursor = QTextCursor(block)
            self._editor.setTextCursor(cursor)
            self._editor.ensureCursorVisible()
            self._editor.setFocus()

    def _doc_base_url(self) -> QUrl:
        """Base URL for the preview: directory of the currently open file."""
        if self._file:
            directory = os.path.dirname(os.path.abspath(self._file))
        else:
            directory = os.path.abspath(os.getcwd())
        return QUrl.fromLocalFile(directory + "/")

    def _get_assets_dir(self) -> str | None:
        """Return the assets/ directory next to the current file, or None if no file is open."""
        if not self._file:
            return None
        return os.path.join(os.path.dirname(os.path.abspath(self._file)), "assets")

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
        mins = max(1, round(n / 200)) if n >= 100 else None
        read = tr("{m} min read", m=mins) if mins else tr("< 1 min read")
        if self._word_goal > 0:
            self._lbl_words.setText(
                tr("{n} / {goal} words · {read}", n=n, goal=self._word_goal, read=read)
            )
            pct = min(100, round(n * 100 / self._word_goal))
            self._bar_goal.setValue(pct)
            self._bar_goal.show()
        else:
            self._lbl_words.setText(tr("{n} words · {read}", n=n, read=read))
            self._bar_goal.hide()

    def _set_editor_active(self, active: bool) -> None:
        """Enable/disable the editor and all actions that require an open document."""
        self._editor.setEnabled(active)
        self._editor.setPlaceholderText(
            "" if active
            else "\n" + tr("Open or create a Markdown file to start editing.")
        )
        for act in (
            self._act_save, self._act_save_as, self._act_export_pdf,
            self._act_export_html, self._act_export_docx,
            self._act_export_epub, self._act_export_latex,
            self._act_insert_link, self._act_insert_image,
            self._act_insert_plantuml, self._act_insert_mermaid, self._act_insert_table,
            self._act_find, self._act_replace,
        ):
            act.setEnabled(active)
        if not active:
            self._find_bar.close_bar()
            self._outline.clear()

    def _toggle_focus_mode(self, on: bool) -> None:
        """Enter or leave distraction-free focus mode (F11)."""
        if on:
            self._pre_focus = {
                "left_visible":     self._left_splitter.isVisible(),
                "preview_visible":  self._preview.isVisible(),
                "sb_visible":       self.statusBar().isVisible(),
                "filetree_checked": self._act_filetree.isChecked(),
                "outline_checked":  self._act_outline.isChecked(),
                "preview_checked":  self._act_preview.isChecked(),
                "outer_sizes":      list(self._outer_splitter.sizes()),
                "splitter_sizes":   list(self._splitter.sizes()),
            }
            self._left_splitter.setVisible(False)
            self._preview.setVisible(False)
            self.statusBar().setVisible(False)
            for act in (self._act_filetree, self._act_outline, self._act_preview):
                act.blockSignals(True)
                act.setChecked(False)
                act.blockSignals(False)
        else:
            pre = self._pre_focus
            self._left_splitter.setVisible(pre.get("left_visible", True))
            self._preview.setVisible(pre.get("preview_visible", True))
            self.statusBar().setVisible(pre.get("sb_visible", True))
            if sizes := pre.get("outer_sizes"):
                self._outer_splitter.setSizes(sizes)
            if sizes := pre.get("splitter_sizes"):
                self._splitter.setSizes(sizes)
            for act, key in (
                (self._act_filetree, "filetree_checked"),
                (self._act_outline,  "outline_checked"),
                (self._act_preview,  "preview_checked"),
            ):
                act.blockSignals(True)
                act.setChecked(pre.get(key, True))
                act.blockSignals(False)

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
        save_dir = self._file_tree._root_dir or (
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DocumentsLocation
            ) or os.path.expanduser("~")
        )
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
            self._git_folder_root = ""
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
        self._start_pdf_import(pdf_path, self._pdf_output_path)

    def _import_pdf_dropped(self, pdf_path: str, output_dir: str | None = None) -> None:
        """Start PDF import with a pre-set input path (called from drag & drop)."""
        if self._pdf_worker is not None:
            return
        if not self._maybe_save():
            return
        if output_dir is not None:
            draft_name = os.path.splitext(os.path.basename(pdf_path))[0] + ".md"
            output_path = os.path.join(output_dir, draft_name)
        else:
            save_dir = (
                os.path.dirname(os.path.abspath(self._file)) if self._file
                else self._file_tree._root_dir or os.path.dirname(pdf_path)
            )
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
            output_path = os.path.join(save_dir, name)
        self._start_pdf_import(pdf_path, output_path)

    def _start_pdf_import(self, pdf_path: str, output_path: str) -> None:
        """Show progress dialog and start the PDF worker."""
        self._pdf_output_path = output_path
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
                tr("Open File from Git"),
                tr(
                    "No credentials configured. Public repositories will still work.\n"
                    "Configure credentials in View → Settings."
                ),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return

        dlg = GitOpenDialog(s, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        info = dlg.get_info()
        if info is None:
            return

        self._git_clone_progress = QProgressDialog(
            tr("Cloning repository …"), tr("Cancel"), 0, 100, self
        )
        self._git_clone_progress.setWindowTitle(tr("Open File from Git"))
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
            self, tr("Open File from Git"), tr("Clone failed:\n{exc}", exc=msg)
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

    # ── Open Folder from Git ──────────────────────────────────────────────────

    def _open_folder_from_git(self) -> None:
        if self._git_clone_folder_worker is not None:
            return  # clone already running
        if not self._maybe_save():
            return

        s = QSettings("MarkdownEditor", "MarkdownEditor")
        user  = s.value("git/https_username", "")
        token = s.value("git/https_token",    "")
        key   = s.value("git/ssh_key_path",   "")
        if not user and not token and not key:
            reply = QMessageBox.information(
                self,
                tr("Open Git Branch"),
                tr(
                    "No credentials configured. Public repositories will still work.\n"
                    "Configure credentials in View → Settings."
                ),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return

        dlg = GitOpenFolderDialog(s, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        info = dlg.get_info()
        if info is None:
            return

        self._git_clone_folder_progress = QProgressDialog(
            tr("Cloning repository …"), tr("Cancel"), 0, 100, self
        )
        self._git_clone_folder_progress.setWindowTitle(tr("Open Git Branch"))
        self._git_clone_folder_progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._git_clone_folder_progress.setAutoClose(False)
        self._git_clone_folder_progress.setAutoReset(False)
        self._git_clone_folder_progress.canceled.connect(self._on_clone_folder_canceled)
        self._git_clone_folder_progress.show()

        self._git_clone_folder_worker = _GitCloneFolderWorker(info, s, self)
        self._git_clone_folder_worker.finished.connect(self._on_clone_folder_done)
        self._git_clone_folder_worker.failed.connect(self._on_clone_folder_failed)
        self._git_clone_folder_worker.progress.connect(self._on_clone_folder_progress)
        self._git_clone_folder_worker.start()

    def _on_clone_folder_progress(self, pct: int, msg: str) -> None:
        dlg = self._git_clone_folder_progress
        if dlg is not None:
            dlg.setValue(pct)
            if msg:
                dlg.setLabelText(tr("Cloning repository …") + f"\n{msg}")

    def _on_clone_folder_done(self, info: GitFileInfo) -> None:
        if self._git_clone_folder_progress is not None:
            self._git_clone_folder_progress.close()
            self._git_clone_folder_progress = None
        self._git_clone_folder_worker = None
        self._git_file_info  = info
        self._git_folder_root = info.local_repo_path
        # Reset per-session push tracking
        self._git_push_count         = 0
        self._git_last_commit_msg    = ""
        self._git_pending_commit_msg = ""
        self._update_squash_action()
        self._file_tree.set_root(info.local_repo_path)
        self._file_tree.setVisible(True)
        self._act_filetree.setChecked(True)
        self._file_tree.mark_git_root(info.local_repo_path, info.repo)

    def _on_clone_folder_failed(self, msg: str, tmpdir: str) -> None:
        if self._git_clone_folder_progress is not None:
            self._git_clone_folder_progress.close()
            self._git_clone_folder_progress = None
        self._git_clone_folder_worker = None
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        QMessageBox.critical(
            self, tr("Open Git Branch"), tr("Clone failed:\n{exc}", exc=msg)
        )

    def _on_clone_folder_canceled(self) -> None:
        if self._git_clone_folder_worker is not None:
            try:
                self._git_clone_folder_worker.finished.disconnect(self._on_clone_folder_done)
                self._git_clone_folder_worker.failed.disconnect(self._on_clone_folder_failed)
                self._git_clone_folder_worker.progress.disconnect(self._on_clone_folder_progress)
            except RuntimeError:
                pass
            self._git_clone_folder_worker.terminate()
            self._git_clone_folder_worker.wait()
            self._git_clone_folder_worker = None
        if self._git_clone_folder_progress is not None:
            self._git_clone_folder_progress.close()
            self._git_clone_folder_progress = None

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
                self._git_file_info  = None
                self._git_folder_root = ""
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

        # In git-folder mode, keep the tree rooted at the repo root and update
        # which file the git context is tracking.
        if self._git_folder_root and path.startswith(self._git_folder_root):
            rel = os.path.relpath(path, self._git_folder_root).replace("\\", "/")
            self._git_file_info.file_path       = rel
            self._git_file_info.local_file_path = path
            self._file_tree.set_root(self._git_folder_root)
            self._file_tree.select_file(path)
            self._file_tree.mark_git_root(self._git_folder_root, self._git_file_info.repo)
        else:
            self._file_tree.set_root(os.path.dirname(os.path.abspath(path)))
            self._file_tree.select_file(path)

        self._add_to_recent(path)
        # Defer the preview so the editor becomes visible immediately; the
        # preview (which may fetch remote resources like PlantUML) renders on
        # the next event-loop iteration.
        QTimer.singleShot(0, self._refresh_preview)

    # ── Recent files ──────────────────────────────────────────────────────────

    _MAX_RECENT = 10

    def _add_to_recent(self, path: str) -> None:
        path = os.path.abspath(path)
        if path in self._recent_files:
            self._recent_files.remove(path)
        self._recent_files.insert(0, path)
        self._recent_files = self._recent_files[: self._MAX_RECENT]
        self._rebuild_recent_menu()

    def _rebuild_recent_menu(self) -> None:
        # Remove old file actions (everything before the permanent separator)
        # The menu has: [Clear] [separator] [file actions...]
        actions = self._recent_menu.actions()
        # actions[0] = Clear, actions[1] = separator — remove everything after
        for act in actions[2:]:
            self._recent_menu.removeAction(act)

        self._recent_menu.setEnabled(bool(self._recent_files))

        for i, path in enumerate(self._recent_files):
            label = os.path.basename(path)
            prefix = f"&{i}" if i < 10 else ""
            act = self._recent_menu.addAction(f"{prefix} {label}".strip())
            act.setToolTip(path)
            act.setEnabled(os.path.isfile(path))
            act.triggered.connect(lambda checked=False, p=path: self._open_recent(p))

    def _open_recent(self, path: str) -> None:
        if not os.path.isfile(path):
            QMessageBox.warning(
                self, tr("Recent Files"),
                tr("File not found:\n{path}", path=path),
            )
            self._recent_files = [p for p in self._recent_files if p != path]
            self._rebuild_recent_menu()
            return
        if self._maybe_save():
            self._load(path)

    def _clear_recent_files(self) -> None:
        self._recent_files.clear()
        self._rebuild_recent_menu()

    def _rebuild_spell_lang_menu(self) -> None:
        """Repopulate View → Spell check language from user-selected languages in Settings."""
        # Remove all actions from group and menu
        for act in list(self._spell_lang_group.actions()):
            self._spell_lang_group.removeAction(act)
        self._spell_lang_menu.clear()

        enabled = self._settings.value("spell_langs_enabled", list(SPELL_CHECK_LANGUAGES))
        if isinstance(enabled, str):
            enabled = [enabled]

        current_lang = self._settings.value("spell_lang", "en")

        for code in SPELL_CHECK_LANGUAGES:
            if code not in enabled:
                continue
            act = self._spell_lang_menu.addAction(LANGUAGES[code])
            act.setCheckable(True)
            act.setData(code)
            self._spell_lang_group.addAction(act)
            if code == current_lang:
                act.setChecked(True)

        # Fallback: check first entry if nothing matched
        if not self._spell_lang_group.checkedAction() and self._spell_lang_group.actions():
            self._spell_lang_group.actions()[0].setChecked(True)

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

    def _export_html(self) -> None:
        default = os.path.splitext(self._file)[0] + ".html" if self._file else ""
        path, _ = QFileDialog.getSaveFileName(
            self, tr("Export as HTML"),
            default, tr("HTML files (*.html);;All files (*)")
        )
        if not path:
            return
        html = self._inline_local_images(self._preview.get_html())
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            self.statusBar().showMessage(tr("HTML saved: {path}", path=path), 5000)
        except OSError:
            QMessageBox.critical(self, tr("Error"),
                                 tr("Could not save HTML:\n{path}", path=path))

    def _inline_local_images(self, html: str) -> str:
        """Replace local <img src="..."> with base64 data URIs."""
        import base64
        import re as _re2
        if not self._file:
            return html
        base_dir = os.path.dirname(os.path.abspath(self._file))
        _mime = {
            "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "svg": "image/svg+xml",
            "webp": "image/webp", "bmp": "image/bmp",
        }
        def _sub(m):
            src = m.group(1)
            if src.startswith(("http://", "https://", "data:")):
                return m.group(0)
            img_path = src[7:] if src.startswith("file://") else os.path.join(base_dir, src)
            if not os.path.isfile(img_path):
                return m.group(0)
            ext = os.path.splitext(img_path)[1].lstrip(".").lower()
            mime = _mime.get(ext, "image/png")
            with open(img_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return f'src="data:{mime};base64,{data}"'
        return _re2.sub(r'src="([^"]*)"', _sub, html)

    def _export_pandoc(self, fmt: str) -> None:
        import shutil
        import subprocess
        import tempfile
        pandoc = shutil.which("pandoc")
        if not pandoc:
            QMessageBox.warning(self, tr("Pandoc not found"),
                tr("Pandoc is not installed or not on PATH.\n"
                   "Install it from https://pandoc.org/installing.html"))
            return
        ext   = {"docx": ".docx", "epub": ".epub", "latex": ".tex"}[fmt]
        filt  = {
            "docx":  tr("Word documents (*.docx);;All files (*)"),
            "epub":  tr("EPUB files (*.epub);;All files (*)"),
            "latex": tr("LaTeX files (*.tex);;All files (*)"),
        }[fmt]
        title = {
            "docx":  tr("Export as DOCX"),
            "epub":  tr("Export as EPUB"),
            "latex": tr("Export as LaTeX"),
        }[fmt]
        default = (os.path.splitext(self._file)[0] + ext) if self._file else ""
        path, _ = QFileDialog.getSaveFileName(self, title, default, filt)
        if not path:
            return
        base_dir = os.path.dirname(os.path.abspath(self._file)) if self._file else None
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md",
                                        delete=False, encoding="utf-8") as tmp:
            tmp.write(self._editor.toPlainText())
            tmp_path = tmp.name
        try:
            result = subprocess.run(
                [pandoc, "-f", "markdown", "-t", fmt, "-o", path, tmp_path],
                capture_output=True, text=True, timeout=30, cwd=base_dir,
            )
            if result.returncode == 0:
                self.statusBar().showMessage(tr("Exported: {path}", path=path), 5000)
            else:
                QMessageBox.critical(self, tr("Error"),
                    tr("Pandoc export failed:\n{err}", err=result.stderr[:500]))
        except Exception as e:
            QMessageBox.critical(self, tr("Error"), str(e))
        finally:
            os.unlink(tmp_path)

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
        if sizes := self._settings.value("left_splitter"):
            self._left_splitter.setSizes([int(s) for s in sizes])
        outline_visible = self._settings.value("outline_visible", True, type=bool)
        self._act_outline.setChecked(outline_visible)
        self._outline.setVisible(outline_visible)
        recent = self._settings.value("recent_files", [])
        if isinstance(recent, str):
            recent = [recent]
        self._recent_files = [p for p in recent if isinstance(p, str)]
        self._rebuild_recent_menu()
        self._rebuild_spell_lang_menu()
        spell_on = self._settings.value("spell_check", False, type=bool)
        self._act_spellcheck.setChecked(spell_on)
        self._apply_themes()
        self._apply_autosave_settings()
        self._word_goal = int(self._settings.value("word_goal", 0))
        self._update_words()

    def _apply_themes(self) -> None:
        editor_theme  = self._settings.value("editor_theme",  "VS Code Dark")
        preview_theme = self._settings.value("preview_theme", "GitHub Dark")
        self._editor.set_theme(editor_theme)
        self._preview.set_theme(preview_theme)

    def _apply_autosave_settings(self) -> None:
        """Start, stop, or reconfigure the periodic auto-save timer."""
        enabled  = self._settings.value("autosave/enabled",  False, type=bool)
        interval = int(self._settings.value("autosave/interval", 30))
        if enabled:
            self._autosave_timer.start(interval * 1000)
        else:
            self._autosave_timer.stop()

    def _autosave(self) -> None:
        """Write the current file to disk (no git commit). Skips git-managed files."""
        if not self._file or not self._modified:
            return
        if self._git_file_info is not None:
            return
        self._write(self._file)

    def _set_word_goal(self) -> None:
        val, ok = QInputDialog.getInt(
            self,
            tr("Word Goal"),
            tr("Target word count (0 to disable):"),
            self._word_goal, 0, 1_000_000, 100,
        )
        if ok:
            self._word_goal = val
            self._settings.setValue("word_goal", val)
            self._update_words()

    def changeEvent(self, event) -> None:  # type: ignore[override]
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowDeactivate:
            if self._settings.value("autosave/enabled", False, type=bool) and \
               self._settings.value("autosave/on_focus_loss", False, type=bool):
                self._autosave()

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._apply_themes()
            self._rebuild_spell_lang_menu()
            self._apply_autosave_settings()

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
        self._settings.setValue("left_splitter", self._left_splitter.sizes())
        self._settings.setValue("outline_visible", self._act_outline.isChecked())
        self._settings.setValue("recent_files", self._recent_files)
        self._settings.setValue("spell_check", self._act_spellcheck.isChecked())
        checked_lang = self._spell_lang_group.checkedAction()
        if checked_lang:
            self._settings.setValue("spell_lang", checked_lang.data())
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

    def _insert_mermaid(self) -> None:
        dlg = InsertMermaidDialog(self)
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

    # ── User manual ───────────────────────────────────────────────────────────

    def _show_user_manual(self) -> None:
        from PyQt6.QtGui import QDesktopServices
        from i18n import current as _lang
        filename = "index.html" if _lang() == "en" else f"{_lang()}.html"
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(os.path.dirname(__file__))
        docs_dir = os.path.join(base, "docs")
        path = os.path.join(docs_dir, filename)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    # ── Markdown help ─────────────────────────────────────────────────────────

    def _show_markdown_help(self) -> None:
        dlg = MarkdownHelpDialog(self)
        dlg.exec()

    def _show_plantuml_help(self) -> None:
        dlg = PlantUMLHelpDialog(self)
        dlg.exec()

    def _show_mermaid_help(self) -> None:
        dlg = MermaidHelpDialog(self)
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
