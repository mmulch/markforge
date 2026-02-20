"""Dialogs for inserting links and images."""

from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from i18n import tr


def _mono_font(size: int = 10) -> QFont:
    f = QFont("Monospace", size)
    f.setStyleHint(QFont.StyleHint.Monospace)
    return f


def _make_buttons(dialog: QDialog) -> tuple[QDialogButtonBox, QPushButton]:
    btns = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok
        | QDialogButtonBox.StandardButton.Cancel
    )
    ok = btns.button(QDialogButtonBox.StandardButton.Ok)
    ok.setText(tr("Insert"))
    btns.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
    btns.accepted.connect(dialog.accept)
    btns.rejected.connect(dialog.reject)
    return btns, ok


def _preview_group(preview_widget: QPlainTextEdit) -> QGroupBox:
    grp    = QGroupBox(tr("Preview (Markdown)"))
    layout = QVBoxLayout(grp)
    layout.addWidget(preview_widget)
    return grp


# ── Link dialog ───────────────────────────────────────────────────────────────

class InsertLinkDialog(QDialog):
    """Dialog for inserting a Markdown link."""

    def __init__(self, selected_text: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Insert Link"))
        self.setMinimumWidth(480)
        self._build_ui(selected_text)
        self._refresh()

    def _build_ui(self, selected_text: str) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        grp  = QGroupBox(tr("Link Properties"))
        form = QFormLayout(grp)

        self._text_edit = QLineEdit(selected_text)
        self._text_edit.setPlaceholderText(tr("e.g.  Click here"))
        form.addRow(tr("Display text:"), self._text_edit)

        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText(tr("https://example.com"))
        form.addRow(tr("URL:"), self._url_edit)

        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText(tr("Optional tooltip (shown on hover)"))
        form.addRow(tr("Title (optional):"), self._title_edit)

        root.addWidget(grp)

        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(_mono_font())
        self._preview.setMaximumHeight(56)
        root.addWidget(_preview_group(self._preview))

        btns, self._ok_btn = _make_buttons(self)
        root.addWidget(btns)

        self._text_edit.textChanged.connect(self._refresh)
        self._url_edit.textChanged.connect(self._refresh)
        self._title_edit.textChanged.connect(self._refresh)

    def _refresh(self) -> None:
        md = self.get_markdown()
        self._preview.setPlainText(md)
        self._ok_btn.setEnabled(bool(self._url_edit.text().strip()))

    def get_markdown(self) -> str:
        url   = self._url_edit.text().strip()
        text  = self._text_edit.text().strip() or url
        title = self._title_edit.text().strip()
        if not url:
            return ""
        return f'[{text}]({url} "{title}")' if title else f"[{text}]({url})"


# ── Image dialog ──────────────────────────────────────────────────────────────

class InsertImageDialog(QDialog):
    """Dialog for inserting a Markdown image."""

    def __init__(self, selected_text: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Insert Image"))
        self.setMinimumWidth(520)
        self._build_ui(selected_text)
        self._refresh()

    def _build_ui(self, selected_text: str) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        grp  = QGroupBox(tr("Image Properties"))
        form = QFormLayout(grp)

        self._alt_edit = QLineEdit(selected_text)
        self._alt_edit.setPlaceholderText(tr("Short image description (for screen readers)"))
        form.addRow(tr("Alt Text:"), self._alt_edit)

        url_row = QHBoxLayout()
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText(
            tr("https://example.com/image.png  or  local path")
        )
        url_row.addWidget(self._url_edit)
        browse_btn = QPushButton("…")
        browse_btn.setFixedWidth(32)
        browse_btn.setToolTip(tr("Select local image file"))
        browse_btn.clicked.connect(self._browse)
        url_row.addWidget(browse_btn)
        form.addRow(tr("URL / Path:"), url_row)

        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText(tr("Optional tooltip (shown on hover)"))
        form.addRow(tr("Title (optional):"), self._title_edit)

        root.addWidget(grp)

        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(_mono_font())
        self._preview.setMaximumHeight(56)
        root.addWidget(_preview_group(self._preview))

        btns, self._ok_btn = _make_buttons(self)
        root.addWidget(btns)

        self._alt_edit.textChanged.connect(self._refresh)
        self._url_edit.textChanged.connect(self._refresh)
        self._title_edit.textChanged.connect(self._refresh)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Select Image File"),
            "",
            tr("Images (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;All files (*)"),
        )
        if path:
            self._url_edit.setText(path)

    def _refresh(self) -> None:
        md = self.get_markdown()
        self._preview.setPlainText(md)
        self._ok_btn.setEnabled(bool(self._url_edit.text().strip()))

    def get_markdown(self) -> str:
        url   = self._url_edit.text().strip()
        alt   = self._alt_edit.text().strip()
        title = self._title_edit.text().strip()
        if not url:
            return ""
        return f'![{alt}]({url} "{title}")' if title else f"![{alt}]({url})"
