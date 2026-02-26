"""Editor widget with line numbers and Markdown syntax highlighting."""

from __future__ import annotations

import os
from typing import Callable

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QImage,
    QKeySequence,
    QPainter,
    QPalette,
    QTextCharFormat,
    QTextFormat,
    QTextOption,
)
from PyQt6.QtWidgets import QApplication, QMessageBox, QPlainTextEdit, QTextEdit, QWidget

from highlighter import MarkdownHighlighter
from themes import EDITOR_THEMES

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico"}


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

    # Diff marker types
    _DIFF_ADDED    = QColor(80,  200, 100)
    _DIFF_MODIFIED = QColor(220, 150,  30)
    _DIFF_REMOVED  = QColor(210,  70,  70)

    def __init__(self) -> None:
        super().__init__()
        self._theme_name = "VS Code Dark"
        self._gutter = _LineNumberArea(self)
        self._highlighter = MarkdownHighlighter(self.document())
        self._search_selections: list = []
        self._get_assets_dir: Callable[[], str | None] = lambda: None
        self._diff_markers: dict[int, str] = {}  # 1-based line → "added"|"modified"|"removed_above"

        self.setAcceptDrops(True)
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

    def set_assets_dir_provider(self, fn: Callable[[], str | None]) -> None:
        self._get_assets_dir = fn

    def set_diff_markers(self, markers: dict[int, str]) -> None:
        """Update gutter diff markers. Keys are 1-based line numbers."""
        self._diff_markers = markers
        self._update_gutter_width(0)
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

    _DIFF_BAR_W = 4  # px width of the diff colour bar in the gutter

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        extra = self._DIFF_BAR_W if self._diff_markers else 0
        return 16 + extra + self.fontMetrics().horizontalAdvance("9") * digits

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

        has_diff = bool(self._diff_markers)
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bot >= event.rect().top():
                # ── diff colour bar ─────────────────────────────────────────
                if has_diff:
                    marker = self._diff_markers.get(num + 1)
                    if marker == "added":
                        painter.fillRect(0, top, self._DIFF_BAR_W, bot - top,
                                         self._DIFF_ADDED)
                    elif marker == "modified":
                        painter.fillRect(0, top, self._DIFF_BAR_W, bot - top,
                                         self._DIFF_MODIFIED)
                    elif marker == "removed_above":
                        # Small triangle pointing right at the top of this row
                        h = min(8, bot - top)
                        painter.fillRect(0, top, self._DIFF_BAR_W, h,
                                         self._DIFF_REMOVED)
                # ── line number ─────────────────────────────────────────────
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

    # ── Clipboard paste / drag-and-drop ───────────────────────────────────────

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.matches(QKeySequence.StandardKey.Paste):
            if self._try_paste_image():
                return
        super().keyPressEvent(event)

    def dragEnterEvent(self, event) -> None:  # type: ignore[override]
        if self._has_image_or_file(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._has_image_or_file(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:  # type: ignore[override]
        if self._has_image_or_file(event.mimeData()):
            self._handle_drop(event.mimeData())
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def _has_image_or_file(self, mime) -> bool:
        if mime.hasImage():
            return True
        if mime.hasUrls():
            return any(
                u.isLocalFile() for u in mime.urls()
            )
        return False

    def _try_paste_image(self) -> bool:
        """Check clipboard for image data; save and insert if found. Returns True if handled."""
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if not mime or not mime.hasImage():
            return False
        assets_dir = self._get_assets_dir()
        if not assets_dir:
            self._show_no_file_message()
            return True
        image = clipboard.image()
        if image.isNull():
            return False
        rel_path = self._save_image_to_assets(image, "image")
        if rel_path:
            self._insert_md_image(rel_path)
        return True

    def _handle_drop(self, mime) -> None:
        """Handle dropped files or raw image data."""
        if mime.hasUrls():
            for url in mime.urls():
                if not url.isLocalFile():
                    continue
                dropped_path = url.toLocalFile()
                ext = os.path.splitext(dropped_path)[1].lower()
                if ext in _IMAGE_EXTENSIONS:
                    self._handle_dropped_image_file(dropped_path)
                elif ext in {".md", ".markdown"}:
                    self._handle_dropped_md_file(dropped_path)
                elif ext == ".pdf":
                    self._handle_dropped_pdf_file(dropped_path)
                else:
                    assets_dir = self._get_assets_dir()
                    if not assets_dir:
                        self._show_no_file_message()
                        return
                    doc_dir = os.path.dirname(assets_dir)
                    rel_path = os.path.relpath(dropped_path, start=doc_dir)
                    self._insert_md_link(rel_path)
        elif mime.hasImage():
            image = mime.imageData()
            if image is None:
                return
            if not isinstance(image, QImage):
                image = QImage(image)
            assets_dir = self._get_assets_dir()
            if not assets_dir:
                self._show_no_file_message()
                return
            rel_path = self._save_image_to_assets(image, "image")
            if rel_path:
                self._insert_md_image(rel_path)

    def _handle_dropped_image_file(self, dropped_path: str) -> None:
        """Show a dialog asking whether to use the original path or copy to assets."""
        from i18n import tr
        fname = os.path.basename(dropped_path)
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("Add Image"))
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(tr("How would you like to add <b>{name}</b>?", name=fname))
        btn_orig  = msg.addButton(tr("Original path"),  QMessageBox.ButtonRole.AcceptRole)
        btn_asset = msg.addButton(tr("Copy to assets"), QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(btn_orig)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked == btn_orig:
            assets_dir = self._get_assets_dir()
            if assets_dir:
                doc_dir = os.path.dirname(assets_dir)
                path = os.path.relpath(dropped_path, start=doc_dir)
            else:
                path = dropped_path
            self._insert_md_image(path)
        elif clicked == btn_asset:
            assets_dir = self._get_assets_dir()
            if not assets_dir:
                self._show_no_file_message()
                return
            rel_path = self._copy_file_to_assets(dropped_path)
            if rel_path:
                self._insert_md_image(rel_path)

    def _handle_dropped_md_file(self, dropped_path: str) -> None:
        """Dialog: open MD from original path, or copy to current working folder first."""
        from i18n import tr
        fname = os.path.basename(dropped_path)
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("Open Markdown File"))
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(tr("What would you like to do with <b>{name}</b>?", name=fname))
        btn_open = msg.addButton(tr("Open"),           QMessageBox.ButtonRole.AcceptRole)
        btn_copy = msg.addButton(tr("Copy to folder"), QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(btn_open)
        msg.exec()
        clicked = msg.clickedButton()
        win = self.window()
        if clicked == btn_open:
            if hasattr(win, "_load"):
                win._load(dropped_path)
        elif clicked == btn_copy:
            assets_dir = self._get_assets_dir()
            if not assets_dir:
                self._show_no_file_message()
                return
            doc_dir = os.path.dirname(assets_dir)
            dest = self._copy_to_dir(dropped_path, doc_dir)
            if dest and hasattr(win, "_load"):
                win._load(dest)

    def _handle_dropped_pdf_file(self, dropped_path: str) -> None:
        """Delegate PDF drop handling to MainWindow."""
        win = self.window()
        if hasattr(win, "_import_pdf_drop"):
            win._import_pdf_drop(dropped_path)

    def _copy_to_dir(self, src_path: str, dest_dir: str) -> str | None:
        """Copy src_path into dest_dir, preserving filename (adds suffix on collision)."""
        import shutil
        name, ext = os.path.splitext(os.path.basename(src_path))
        dest = os.path.join(dest_dir, f"{name}{ext}")
        n = 1
        while os.path.exists(dest):
            if os.path.abspath(dest) == os.path.abspath(src_path):
                return dest   # already in place — nothing to copy
            dest = os.path.join(dest_dir, f"{name}_{n:03d}{ext}")
            n += 1
        shutil.copy2(src_path, dest)
        return dest

    def _save_image_to_assets(self, image: QImage, hint: str) -> str | None:
        """Save QImage to the assets directory. Returns a relative path like assets/image_001.png."""
        assets_dir = self._get_assets_dir()
        if not assets_dir:
            return None
        os.makedirs(assets_dir, exist_ok=True)
        # Find next available filename
        n = 1
        while True:
            filename = f"{hint}_{n:03d}.png"
            full_path = os.path.join(assets_dir, filename)
            if not os.path.exists(full_path):
                break
            n += 1
        if not image.save(full_path, "PNG"):
            return None
        doc_dir = os.path.dirname(assets_dir)
        return os.path.relpath(full_path, start=doc_dir)

    def _copy_file_to_assets(self, src_path: str) -> str | None:
        """Copy a file to the assets directory, preserving its name/extension. Returns relative path."""
        import shutil
        assets_dir = self._get_assets_dir()
        if not assets_dir:
            return None
        os.makedirs(assets_dir, exist_ok=True)
        name, ext = os.path.splitext(os.path.basename(src_path))
        dest = os.path.join(assets_dir, f"{name}{ext}")
        n = 1
        while os.path.exists(dest):
            dest = os.path.join(assets_dir, f"{name}_{n:03d}{ext}")
            n += 1
        shutil.copy2(src_path, dest)
        doc_dir = os.path.dirname(assets_dir)
        return os.path.relpath(dest, start=doc_dir)

    def _insert_md_image(self, rel_path: str) -> None:
        cursor = self.textCursor()
        cursor.insertText(f"![]({rel_path})")

    def _insert_md_link(self, rel_path: str) -> None:
        filename = os.path.basename(rel_path)
        cursor = self.textCursor()
        cursor.insertText(f"[{filename}]({rel_path})")

    def _show_no_file_message(self) -> None:
        from i18n import tr
        win = self.window()
        if hasattr(win, "statusBar"):
            win.statusBar().showMessage(tr("Save the file first to paste images."), 4000)
