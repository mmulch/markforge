"""Editor widget with line numbers and Markdown syntax highlighting."""

from __future__ import annotations

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPalette,
    QTextCharFormat,
    QTextFormat,
    QTextOption,
)
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from highlighter import MarkdownHighlighter
from themes import EDITOR_THEMES


class _LineNumberArea(QWidget):
    """Narrow gutter widget on the left side of the editor for line numbers."""

    def __init__(self, editor: EditorWidget) -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        self._editor._paint_line_numbers(event)


class EditorWidget(QPlainTextEdit):
    """Plain-text editor with line numbers, current-line highlight, and Markdown syntax highlighting."""

    def __init__(self) -> None:
        super().__init__()
        self._theme_name = "VS Code Dark"
        self._gutter = _LineNumberArea(self)
        self._highlighter = MarkdownHighlighter(self.document())
        self._search_selections: list = []

        self._apply_theme()

        self.blockCountChanged.connect(self._update_gutter_width)
        self.updateRequest.connect(self._update_gutter)
        self.cursorPositionChanged.connect(self._highlight_current_line)

        self._update_gutter_width(0)
        self._highlight_current_line()

    # ── Appearance ────────────────────────────────────────────────────────────

    def _apply_theme(self) -> None:
        font = QFont("Monospace", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(40.0)
        self.setWordWrapMode(QTextOption.WrapMode.WordWrap)

        theme = EDITOR_THEMES.get(self._theme_name, EDITOR_THEMES["VS Code Dark"])
        bg = QColor(theme["bg"])
        fg = QColor(theme["fg"])
        self._GUTTER_BG    = QColor(theme["gutter_bg"])
        self._GUTTER_FG    = QColor(theme["gutter_fg"])
        self._LINE_HL      = QColor(theme["line_hl"])
        self._FIND_MATCH   = QColor(theme["find_match"])
        self._FIND_CURRENT = QColor(theme["find_current"])

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Base, bg)
        pal.setColor(QPalette.ColorRole.Text, fg)
        self.setPalette(pal)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_word_wrap(self, enabled: bool) -> None:
        mode = QTextOption.WrapMode.WordWrap if enabled else QTextOption.WrapMode.NoWrap
        self.setWordWrapMode(mode)

    def set_theme(self, theme_name: str) -> None:
        if self._theme_name == theme_name:
            return
        self._theme_name = theme_name
        self._apply_theme()
        old = self.blockSignals(True)
        self._highlighter.set_theme(theme_name)
        self.blockSignals(old)
        self._update_extra_selections()
        self._gutter.update()

    def set_spell_check(self, enabled: bool, lang: str) -> None:
        from spell_checker import spell_check as _sc
        sc = _sc()
        if lang != sc.language:
            sc.set_language(lang)
        sc.set_enabled(enabled)
        self._highlighter.rehighlight()

    def set_search_highlights(self, selections: list) -> None:
        self._search_selections = selections
        self._update_extra_selections()

    # ── Line numbers ──────────────────────────────────────────────────────────

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        return 16 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_gutter_width(self, _: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_gutter(self, rect: QRect, dy: int) -> None:
        if dy:
            self._gutter.scroll(0, dy)
        else:
            self._gutter.update(0, rect.y(), self._gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_gutter_width(0)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._gutter.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def _paint_line_numbers(self, event) -> None:
        painter = QPainter(self._gutter)
        painter.fillRect(event.rect(), self._GUTTER_BG)
        painter.setPen(self._GUTTER_FG)
        painter.setFont(self.font())

        fh    = self.fontMetrics().height()
        block = self.firstVisibleBlock()
        num   = block.blockNumber()
        top   = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bot = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bot >= event.rect().top():
                painter.drawText(
                    0,
                    top,
                    self._gutter.width() - 6,
                    fh,
                    Qt.AlignmentFlag.AlignRight,
                    str(num + 1),
                )
            block = block.next()
            top   = bot
            bot   = top + round(self.blockBoundingRect(block).height())
            num  += 1

    # ── Current line highlight ────────────────────────────────────────────────

    def _update_extra_selections(self) -> None:
        if self.isReadOnly():
            return
        sels = []
        # 1. current-line full-width highlight (renders first / underneath)
        sel = QTextEdit.ExtraSelection()
        fmt = QTextCharFormat()
        fmt.setBackground(self._LINE_HL)
        fmt.setProperty(QTextFormat.Property.FullWidthSelection, True)
        sel.format = fmt
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        sels.append(sel)
        # 2. search match highlights (render on top)
        sels.extend(self._search_selections)
        self.setExtraSelections(sels)

    def _highlight_current_line(self) -> None:
        self._update_extra_selections()
