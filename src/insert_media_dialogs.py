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
    ok.setText("Einfügen")
    btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
    btns.accepted.connect(dialog.accept)
    btns.rejected.connect(dialog.reject)
    return btns, ok


def _preview_group(preview_widget: QPlainTextEdit) -> QGroupBox:
    grp    = QGroupBox("Vorschau (Markdown)")
    layout = QVBoxLayout(grp)
    layout.addWidget(preview_widget)
    return grp


# ── Link dialog ───────────────────────────────────────────────────────────────

class InsertLinkDialog(QDialog):
    """Dialog for inserting a Markdown link."""

    def __init__(self, selected_text: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Link einfügen")
        self.setMinimumWidth(480)
        self._build_ui(selected_text)
        self._refresh()

    def _build_ui(self, selected_text: str) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        # ── Felder ────────────────────────────────────────────────────────
        grp  = QGroupBox("Link-Eigenschaften")
        form = QFormLayout(grp)

        self._text_edit = QLineEdit(selected_text)
        self._text_edit.setPlaceholderText("z. B.  Hier klicken")
        form.addRow("Anzeigetext:", self._text_edit)

        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("https://beispiel.de")
        form.addRow("URL:", self._url_edit)

        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("Optionaler Tooltip (erscheint beim Hover)")
        form.addRow("Titel (optional):", self._title_edit)

        root.addWidget(grp)

        # ── Vorschau ──────────────────────────────────────────────────────
        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(_mono_font())
        self._preview.setMaximumHeight(56)
        root.addWidget(_preview_group(self._preview))

        # ── Buttons ───────────────────────────────────────────────────────
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

    _IMG_FILTER = (
        "Bilder (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico)"
        ";;Alle Dateien (*)"
    )

    def __init__(self, selected_text: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Bild einfügen")
        self.setMinimumWidth(520)
        self._build_ui(selected_text)
        self._refresh()

    def _build_ui(self, selected_text: str) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        # ── Felder ────────────────────────────────────────────────────────
        grp  = QGroupBox("Bild-Eigenschaften")
        form = QFormLayout(grp)

        self._alt_edit = QLineEdit(selected_text)
        self._alt_edit.setPlaceholderText("Kurze Bildbeschreibung (für Screenreader)")
        form.addRow("Alt-Text:", self._alt_edit)

        # URL-Zeile mit Datei-Browser-Button
        url_row = QHBoxLayout()
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText(
            "https://beispiel.de/bild.png  oder  lokaler Pfad"
        )
        url_row.addWidget(self._url_edit)
        browse_btn = QPushButton("…")
        browse_btn.setFixedWidth(32)
        browse_btn.setToolTip("Lokale Bilddatei auswählen")
        browse_btn.clicked.connect(self._browse)
        url_row.addWidget(browse_btn)
        form.addRow("URL / Pfad:", url_row)

        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("Optionaler Tooltip (erscheint beim Hover)")
        form.addRow("Titel (optional):", self._title_edit)

        root.addWidget(grp)

        # ── Vorschau ──────────────────────────────────────────────────────
        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(_mono_font())
        self._preview.setMaximumHeight(56)
        root.addWidget(_preview_group(self._preview))

        # ── Buttons ───────────────────────────────────────────────────────
        btns, self._ok_btn = _make_buttons(self)
        root.addWidget(btns)

        self._alt_edit.textChanged.connect(self._refresh)
        self._url_edit.textChanged.connect(self._refresh)
        self._title_edit.textChanged.connect(self._refresh)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Bilddatei auswählen", "", self._IMG_FILTER
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
