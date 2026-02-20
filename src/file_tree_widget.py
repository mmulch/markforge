"""File tree panel for Markdown-related files."""

from __future__ import annotations

import os

from PyQt6.QtCore import Qt, QSortFilterProxyModel, QTimer, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from i18n import tr

_NAME_FILTERS  = [
    "*.md", "*.markdown",
    "*.txt",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp", "*.bmp",
]
_OPENABLE_EXTS = {".md", ".markdown", ".txt"}


# ── Proxy-Modell ──────────────────────────────────────────────────────────────

class _HideEmptyDirsProxy(QSortFilterProxyModel):
    """Hides directories that contain no relevant files.

    The root directory is always accepted so that ``mapFromSource``
    returns a valid proxy index immediately after ``setRootPath``
    (QFileSystemModel loads sub-directories lazily).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRecursiveFilteringEnabled(True)
        self._root: str = ""

    def set_root(self, path: str) -> None:
        self._root = os.path.normpath(path)
        self.invalidateRowsFilter()

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        model = self.sourceModel()
        idx   = model.index(source_row, 0, source_parent)

        if model.isDir(idx):
            # Always accept root → mapFromSource always returns a valid index
            if os.path.normpath(model.filePath(idx)) == self._root:
                return True
            # All other directories: only show if a descendant matches
            return False

        # Files: QFileSystemModel has already filtered by _NAME_FILTERS
        return True


# ── Widget ────────────────────────────────────────────────────────────────────

class FileTreeWidget(QWidget):
    """Shows files in the directory of the current file, filtered by type."""

    file_activated = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumWidth(150)
        self.setMaximumWidth(420)
        self._root_dir       = ""
        self._pending_select = ""
        self._build_ui()

    # ── UI setup ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_tree())

    def _build_header(self) -> QWidget:
        bar  = QWidget()
        hlay = QHBoxLayout(bar)
        hlay.setContentsMargins(8, 4, 4, 4)

        self._dir_label = QLabel("–")
        self._dir_label.setToolTip(tr("Current root directory"))
        self._dir_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self._dir_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        hlay.addWidget(self._dir_label)

        btn = QToolButton()
        btn.setText("…")
        btn.setToolTip(tr("Choose Directory"))
        btn.clicked.connect(self._choose_root)
        hlay.addWidget(btn)

        return bar

    def _build_tree(self) -> QTreeView:
        self._fs_model = QFileSystemModel()
        self._fs_model.setNameFilters(_NAME_FILTERS)
        self._fs_model.setNameFilterDisables(False)

        self._proxy = _HideEmptyDirsProxy()
        self._proxy.setSourceModel(self._fs_model)

        # Re-evaluate filter and ensure root index after each load step
        self._fs_model.directoryLoaded.connect(self._on_directory_loaded)

        self._tree = QTreeView()
        self._tree.setModel(self._proxy)
        self._tree.setHeaderHidden(True)
        self._tree.hideColumn(1)
        self._tree.hideColumn(2)
        self._tree.hideColumn(3)
        self._tree.setAnimated(True)
        self._tree.setIndentation(14)
        self._tree.setUniformRowHeights(True)
        self._tree.activated.connect(self._on_activated)

        return self._tree

    # ── Public API ────────────────────────────────────────────────────────────

    def set_root(self, path: str) -> None:
        """Sets the root directory; parent directories are never shown."""
        directory = path if os.path.isdir(path) else os.path.dirname(os.path.abspath(path))
        self._root_dir = os.path.normpath(directory)

        self._proxy.set_root(self._root_dir)
        self._fs_model.setRootPath(self._root_dir)

        # Explicitly kick off loading — without this the model waits until the
        # view requests children, but the view won't do so if the root index
        # hasn't been set yet (chicken-and-egg on first visit).
        root_src_idx = self._fs_model.index(self._root_dir)
        if self._fs_model.canFetchMore(root_src_idx):
            self._fs_model.fetchMore(root_src_idx)

        self._apply_root_index()
        QTimer.singleShot(0,   self._apply_root_index)
        QTimer.singleShot(300, self._apply_root_index)  # extra fallback

        label = os.path.basename(self._root_dir) or self._root_dir
        self._dir_label.setText(label)
        self._dir_label.setToolTip(self._root_dir)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _apply_root_index(self) -> None:
        """Sets the tree view root index to the proxy index of the root directory."""
        src_idx   = self._fs_model.index(self._root_dir)
        proxy_idx = self._proxy.mapFromSource(src_idx)
        if proxy_idx.isValid():
            self._tree.setRootIndex(proxy_idx)

    def _on_directory_loaded(self, _: str) -> None:
        # Use invalidateRowsFilter() instead of invalidateFilter() so that the
        # proxy re-evaluates filterAcceptsRow for every row WITHOUT triggering a
        # full model reset (beginResetModel/endResetModel).  A full reset clears
        # the tree view's root index and rebuilds the proxy mapping from scratch;
        # on the first directory load the subsequent mapFromSource() call could
        # return an invalid index because the mapping hadn't been rebuilt yet.
        # invalidateRowsFilter() preserves the existing mapping and root index.
        self._proxy.invalidateRowsFilter()
        self._apply_root_index()
        QTimer.singleShot(0, self._do_select)

    def select_file(self, path: str) -> None:
        """Selects and scrolls to *path* in the tree.

        If the model hasn't loaded the directory yet, the selection is deferred
        until ``directoryLoaded`` fires or a short timer expires.
        """
        self._pending_select = os.path.normpath(path)
        self._do_select()
        # Fallback: retry after async model has populated the directory
        QTimer.singleShot(250, self._do_select)

    def _do_select(self) -> None:
        """Applies the pending selection if the model index is already valid."""
        if not self._pending_select:
            return
        src_idx = self._fs_model.index(self._pending_select)
        if not src_idx.isValid():
            return
        proxy_idx = self._proxy.mapFromSource(src_idx)
        if proxy_idx.isValid():
            self._tree.setCurrentIndex(proxy_idx)
            self._tree.scrollTo(proxy_idx)
            self._pending_select = ""

    def _choose_root(self) -> None:
        path = QFileDialog.getExistingDirectory(self, tr("Choose Directory"))
        if path:
            self.set_root(path)

    def _on_activated(self, proxy_index) -> None:
        src_index = self._proxy.mapToSource(proxy_index)
        path      = self._fs_model.filePath(src_index)
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in _OPENABLE_EXTS:
                self.file_activated.emit(path)
