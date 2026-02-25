"""Find & Replace bar widget for MarkForge."""

from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor, QTextDocument
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from i18n import tr

_MAX_MATCHES = 10_000


class FindReplaceBar(QWidget):
    """Collapsible find/replace bar that sits above the editor splitter."""

    def __init__(self, editor, parent=None) -> None:
        super().__init__(parent)
        self._editor = editor
        self._matches: list[QTextCursor] = []
        self._current: int = -1

        self._build_ui()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(4, 2, 4, 2)
        vbox.setSpacing(2)

        # ── Row 1: find ───────────────────────────────────────────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(4)

        self._find_edit = QLineEdit()
        self._find_edit.setPlaceholderText(tr("Find…"))
        self._find_edit.setMaximumWidth(260)
        row1.addWidget(self._find_edit)

        self._prev_btn = QPushButton("↑")
        self._prev_btn.setToolTip(tr("Find previous (Shift+Enter)"))
        self._prev_btn.setFixedWidth(28)
        row1.addWidget(self._prev_btn)

        self._next_btn = QPushButton("↓")
        self._next_btn.setToolTip(tr("Find next (Enter)"))
        self._next_btn.setFixedWidth(28)
        row1.addWidget(self._next_btn)

        self._match_lbl = QLabel()
        self._match_lbl.setMinimumWidth(80)
        row1.addWidget(self._match_lbl)

        self._case_cb = QCheckBox("Aa")
        self._case_cb.setToolTip(tr("Match case"))
        row1.addWidget(self._case_cb)

        self._word_cb = QCheckBox("[W]")
        self._word_cb.setToolTip(tr("Whole words"))
        row1.addWidget(self._word_cb)

        row1.addStretch()

        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedWidth(28)
        self._close_btn.setToolTip(tr("Close (Escape)"))
        row1.addWidget(self._close_btn)

        vbox.addLayout(row1)

        # ── Row 2: replace ────────────────────────────────────────────────────
        self._replace_row = QWidget()
        row2 = QHBoxLayout(self._replace_row)
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(4)

        self._replace_edit = QLineEdit()
        self._replace_edit.setPlaceholderText(tr("Replace…"))
        self._replace_edit.setMaximumWidth(260)
        row2.addWidget(self._replace_edit)

        self._replace_btn = QPushButton(tr("Replace"))
        row2.addWidget(self._replace_btn)

        self._replace_all_btn = QPushButton(tr("Replace All"))
        row2.addWidget(self._replace_all_btn)

        row2.addStretch()
        vbox.addWidget(self._replace_row)
        self._replace_row.hide()

        # ── Connections ───────────────────────────────────────────────────────
        self._find_edit.textChanged.connect(self._update_matches)
        self._find_edit.returnPressed.connect(self._find_next)
        self._case_cb.toggled.connect(self._update_matches)
        self._word_cb.toggled.connect(self._update_matches)
        self._prev_btn.clicked.connect(self._find_prev)
        self._next_btn.clicked.connect(self._find_next)
        self._close_btn.clicked.connect(self.close_bar)
        self._replace_btn.clicked.connect(self._replace)
        self._replace_all_btn.clicked.connect(self._replace_all)

        # Shift+Return in the find field → find previous
        self._find_edit.installEventFilter(self)

    # ── Public API ────────────────────────────────────────────────────────────

    def show_find(self) -> None:
        """Show bar in find-only mode."""
        self._replace_row.hide()
        self._show_and_fill()

    def show_replace(self) -> None:
        """Show bar with replace row visible."""
        self._replace_row.show()
        self._show_and_fill()

    def close_bar(self) -> None:
        """Hide bar, clear highlights, return focus to editor."""
        self.hide()
        self._editor.set_search_highlights([])
        self._editor.setFocus()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _show_and_fill(self) -> None:
        self.show()
        # Pre-fill with single-line editor selection
        cursor = self._editor.textCursor()
        sel = cursor.selectedText()
        if sel and "\n" not in sel and "\u2029" not in sel:
            self._find_edit.setText(sel)
        self._find_edit.setFocus()
        self._find_edit.selectAll()
        self._update_matches()

    def _find_flags(self) -> QTextDocument.FindFlag:
        flags = QTextDocument.FindFlag(0)
        if self._case_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self._word_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def _update_matches(self) -> None:
        term = self._find_edit.text()
        doc = self._editor.document()
        self._matches = []

        if term:
            flags = self._find_flags()
            cursor = QTextCursor(doc)
            while True:
                cursor = doc.find(term, cursor, flags)
                if cursor.isNull():
                    break
                self._matches.append(QTextCursor(cursor))
                if len(self._matches) >= _MAX_MATCHES:
                    break

        # Pick closest match to current editor cursor
        if self._matches:
            editor_pos = self._editor.textCursor().position()
            self._current = 0
            for i, m in enumerate(self._matches):
                if m.selectionStart() >= editor_pos:
                    self._current = i
                    break
        else:
            self._current = -1

        self._highlight_all()
        self._update_match_label()

    def _find_next(self) -> None:
        if not self._matches:
            return
        self._current = (self._current + 1) % len(self._matches)
        self._go_to_current()

    def _find_prev(self) -> None:
        if not self._matches:
            return
        self._current = (self._current - 1) % len(self._matches)
        self._go_to_current()

    def _go_to_current(self) -> None:
        if self._current < 0 or self._current >= len(self._matches):
            return
        self._editor.setTextCursor(self._matches[self._current])
        self._editor.ensureCursorVisible()
        self._highlight_all()
        self._update_match_label()

    def _highlight_all(self) -> None:
        from themes import EDITOR_THEMES
        theme = EDITOR_THEMES.get(
            self._editor._theme_name, EDITOR_THEMES["VS Code Dark"]
        )
        dim_color     = QColor(theme["find_match"])
        current_color = QColor(theme["find_current"])

        sels = []
        for i, m in enumerate(self._matches):
            sel = QTextEdit.ExtraSelection()
            fmt = QTextCharFormat()
            fmt.setBackground(current_color if i == self._current else dim_color)
            sel.format = fmt
            sel.cursor = m
            sels.append(sel)

        self._editor.set_search_highlights(sels)

    def _update_match_label(self) -> None:
        if not self._find_edit.text():
            self._match_lbl.setText("")
        elif not self._matches:
            self._match_lbl.setText(tr("No results"))
        else:
            self._match_lbl.setText(
                tr("{cur} / {total}", cur=self._current + 1, total=len(self._matches))
            )

    def _replace(self) -> None:
        if self._current < 0 or self._current >= len(self._matches):
            return
        replacement = self._replace_edit.text()
        self._matches[self._current].insertText(replacement)
        self._update_matches()

    def _replace_all(self) -> None:
        if not self._matches:
            return
        replacement = self._replace_edit.text()
        doc = self._editor.document()
        cursor = QTextCursor(doc)
        cursor.beginEditBlock()
        count = 0
        # Iterate in reverse order to preserve positions
        for m in reversed(self._matches):
            m.insertText(replacement)
            count += 1
        cursor.endEditBlock()
        self._match_lbl.setText(tr("{n} replaced", n=count))
        self._matches = []
        self._current = -1
        self._editor.set_search_highlights([])

    # ── Event filter (Shift+Return → find prev) ───────────────────────────────

    def eventFilter(self, obj, event) -> bool:
        if obj is self._find_edit:
            if event.type() == QEvent.Type.KeyPress:
                if (event.key() == Qt.Key.Key_Return
                        and event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                    self._find_prev()
                    return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close_bar()
        else:
            super().keyPressEvent(event)
