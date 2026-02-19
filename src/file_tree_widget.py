"""Dateibaum-Panel für Markdown-relevante Dateien."""

from __future__ import annotations

import fnmatch
import os

from PyQt6.QtCore import Qt, QSortFilterProxyModel, pyqtSignal
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

_NAME_FILTERS    = [
    "*.md", "*.markdown",
    "*.txt",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp", "*.bmp",
]
_FILTER_PATTERNS = [p.lower() for p in _NAME_FILTERS]
_OPENABLE_EXTS   = {".md", ".markdown", ".txt"}


# ── Proxy-Modell ──────────────────────────────────────────────────────────────

class _HideEmptyDirsProxy(QSortFilterProxyModel):
    """Blendet Verzeichnisse aus, die keine relevanten Dateien enthalten.

    Das Wurzelverzeichnis wird immer akzeptiert, damit ``mapFromSource``
    auch direkt nach ``setRootPath`` einen gültigen Proxy-Index liefert
    (QFileSystemModel lädt Unterordner verzögert).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRecursiveFilteringEnabled(True)
        self._root: str = ""

    def set_root(self, path: str) -> None:
        self._root = os.path.normpath(path)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        model = self.sourceModel()
        idx   = model.index(source_row, 0, source_parent)

        if model.isDir(idx):
            # Wurzel immer akzeptieren → mapFromSource liefert stets gültigen Index
            if os.path.normpath(model.filePath(idx)) == self._root:
                return True
            # Alle anderen Verzeichnisse: nur zeigen, wenn ein Nachkomme passt
            return False

        # Dateien: QFileSystemModel hat bereits nach _NAME_FILTERS gefiltert
        return True


# ── Widget ────────────────────────────────────────────────────────────────────

class FileTreeWidget(QWidget):
    """Zeigt Dateien im Verzeichnis der aktuellen Datei, gefiltert nach Typ."""

    file_activated = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumWidth(150)
        self.setMaximumWidth(420)
        self._root_dir = ""
        self._build_ui()

    # ── UI-Aufbau ─────────────────────────────────────────────────────────────

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
        self._dir_label.setToolTip("Aktuelles Stammverzeichnis")
        self._dir_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self._dir_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        hlay.addWidget(self._dir_label)

        btn = QToolButton()
        btn.setText("…")
        btn.setToolTip("Verzeichnis wählen")
        btn.clicked.connect(self._choose_root)
        hlay.addWidget(btn)

        return bar

    def _build_tree(self) -> QTreeView:
        self._fs_model = QFileSystemModel()
        self._fs_model.setNameFilters(_NAME_FILTERS)
        self._fs_model.setNameFilterDisables(False)

        self._proxy = _HideEmptyDirsProxy()
        self._proxy.setSourceModel(self._fs_model)

        # Nach jedem Ladeschritt: Filter neu auswerten + Root-Index sicherstellen
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

    # ── Öffentliche API ───────────────────────────────────────────────────────

    def set_root(self, path: str) -> None:
        """Setzt das Stammverzeichnis; Elternverzeichnisse werden nie angezeigt."""
        directory = path if os.path.isdir(path) else os.path.dirname(os.path.abspath(path))
        self._root_dir = os.path.normpath(directory)

        self._proxy.set_root(self._root_dir)
        self._fs_model.setRootPath(self._root_dir)
        self._apply_root_index()

        label = os.path.basename(self._root_dir) or self._root_dir
        self._dir_label.setText(label)
        self._dir_label.setToolTip(self._root_dir)

    # ── Intern ────────────────────────────────────────────────────────────────

    def _apply_root_index(self) -> None:
        """Setzt den Root-Index des Tree-Views auf den Proxy-Index des Wurzelverzeichnisses."""
        src_idx   = self._fs_model.index(self._root_dir)
        proxy_idx = self._proxy.mapFromSource(src_idx)
        self._tree.setRootIndex(proxy_idx)

    def _on_directory_loaded(self, loaded_path: str) -> None:
        self._proxy.invalidateFilter()
        # Root-Index nach dem Laden erneut setzen (lazy-loading-Sicherung)
        if os.path.normpath(loaded_path) == self._root_dir:
            self._apply_root_index()

    def _choose_root(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Verzeichnis wählen")
        if path:
            self.set_root(path)

    def _on_activated(self, proxy_index) -> None:
        src_index = self._proxy.mapToSource(proxy_index)
        path      = self._fs_model.filePath(src_index)
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in _OPENABLE_EXTS:
                self.file_activated.emit(path)
