"""Document outline panel — live heading navigator."""

from __future__ import annotations

import re

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from i18n import tr

_HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)(?:\s+#+\s*)?$')
_FENCE_RE   = re.compile(r'^(`{3,}|~{3,})')


def _parse_headings(text: str) -> list[tuple[int, str, int]]:
    """Return list of (level, title, line_number), skipping fenced code blocks."""
    headings: list[tuple[int, str, int]] = []
    in_fence   = False
    fence_mark = ""
    for lineno, line in enumerate(text.splitlines()):
        stripped = line.strip()
        m = _FENCE_RE.match(stripped)
        if m:
            ch = m.group(1)[0]
            if not in_fence:
                in_fence, fence_mark = True, ch
            elif ch == fence_mark:
                in_fence = False
            continue
        if in_fence:
            continue
        m = _HEADING_RE.match(stripped)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip(), lineno))
    return headings


class OutlineWidget(QWidget):
    """Collapsible sidebar listing headings extracted live from the document."""

    jump_to_line = pyqtSignal(int)  # 0-based line number

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumWidth(150)
        self.setMaximumWidth(420)
        self._build_ui()

    # ── Build UI ──────────────────────────────────────────────────────────────

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
        lbl = QLabel(tr("Outline"))
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        hlay.addWidget(lbl)
        return bar

    def _build_tree(self) -> QTreeWidget:
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(12)
        self._tree.setUniformRowHeights(True)
        self._tree.setAnimated(False)
        self._tree.itemClicked.connect(self._on_clicked)
        return self._tree

    # ── Public API ────────────────────────────────────────────────────────────

    def refresh(self, text: str) -> None:
        """Re-parse the document and rebuild the heading tree."""
        headings = _parse_headings(text)

        self._tree.blockSignals(True)
        self._tree.clear()

        # stack: list of (level, item | None); level=0 / None = invisible root
        stack: list[tuple[int, QTreeWidgetItem | None]] = [(0, None)]

        for level, title, lineno in headings:
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, lineno)
            item.setToolTip(0, title)

            # Pop until we find an ancestor with a strictly smaller level
            while len(stack) > 1 and stack[-1][0] >= level:
                stack.pop()

            parent = stack[-1][1]
            if parent is None:
                self._tree.addTopLevelItem(item)
            else:
                parent.addChild(item)

            item.setExpanded(True)
            stack.append((level, item))

        self._tree.blockSignals(False)

    def clear(self) -> None:
        """Remove all items from the tree."""
        self._tree.clear()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _on_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        lineno = item.data(0, Qt.ItemDataRole.UserRole)
        if lineno is not None:
            self.jump_to_line.emit(lineno)
