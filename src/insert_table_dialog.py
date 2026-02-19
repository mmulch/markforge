"""Dialog zum Konfigurieren und Einfügen einer Markdown-Tabelle."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QPlainTextEdit,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

# Ausrichtungs-Optionen und ihre Markdown-Trennzeichen
_ALIGNMENTS: list[tuple[str, str]] = [
    ("Links",    ":---"),
    ("Zentriert", ":---:"),
    ("Rechts",   "---:"),
]
_ALIGN_LABELS  = [label for label, _ in _ALIGNMENTS]
_ALIGN_MARKERS = {label: marker for label, marker in _ALIGNMENTS}


def _make_mono_font(size: int = 10) -> QFont:
    f = QFont("Monospace", size)
    f.setStyleHint(QFont.StyleHint.Monospace)
    return f


class InsertTableDialog(QDialog):
    """Dialog zur Konfiguration einer einzufügenden Markdown-Tabelle."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tabelle einfügen")
        self.setMinimumWidth(520)
        self._build_ui()
        self._sync_column_table()
        self._refresh_preview()

    # ── UI-Aufbau ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        root.addWidget(self._build_structure_group())
        root.addWidget(self._build_columns_group())
        root.addWidget(self._build_preview_group())

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Einfügen")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _build_structure_group(self) -> QGroupBox:
        grp  = QGroupBox("Tabellenstruktur")
        form = QFormLayout(grp)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)

        self._rows_spin = QSpinBox()
        self._rows_spin.setRange(1, 100)
        self._rows_spin.setValue(3)
        self._rows_spin.setToolTip("Anzahl der Datenzeilen (ohne Kopfzeile)")
        form.addRow("Datenzeilen:", self._rows_spin)

        self._cols_spin = QSpinBox()
        self._cols_spin.setRange(1, 15)
        self._cols_spin.setValue(3)
        self._cols_spin.setToolTip("Anzahl der Spalten")
        form.addRow("Spalten:", self._cols_spin)

        self._header_check = QCheckBox("Kopfzeile mit Spaltentiteln")
        self._header_check.setChecked(True)
        form.addRow("", self._header_check)

        self._rows_spin.valueChanged.connect(self._refresh_preview)
        self._cols_spin.valueChanged.connect(self._on_cols_changed)
        self._header_check.toggled.connect(self._refresh_preview)

        return grp

    def _build_columns_group(self) -> QGroupBox:
        grp    = QGroupBox("Spaltenkonfiguration")
        layout = QVBoxLayout(grp)

        self._col_table = QTableWidget()
        self._col_table.setColumnCount(2)
        self._col_table.setHorizontalHeaderLabels(["Spaltenname", "Ausrichtung"])
        hh = self._col_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._col_table.verticalHeader().setDefaultSectionSize(28)
        self._col_table.verticalHeader().setVisible(False)
        self._col_table.setAlternatingRowColors(True)
        self._col_table.setMinimumHeight(140)
        self._col_table.setMaximumHeight(220)
        self._col_table.itemChanged.connect(self._refresh_preview)
        layout.addWidget(self._col_table)

        return grp

    def _build_preview_group(self) -> QGroupBox:
        grp    = QGroupBox("Vorschau (Markdown)")
        layout = QVBoxLayout(grp)

        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(_make_mono_font(10))
        self._preview.setMaximumHeight(130)
        layout.addWidget(self._preview)

        return grp

    # ── Logik ─────────────────────────────────────────────────────────────────

    def _on_cols_changed(self) -> None:
        self._sync_column_table()
        self._refresh_preview()

    def _sync_column_table(self) -> None:
        """Passt die Anzahl der Zeilen in der Spaltentabelle an."""
        n    = self._cols_spin.value()
        prev = self._col_table.rowCount()

        self._col_table.blockSignals(True)
        self._col_table.setRowCount(n)

        for i in range(prev, n):          # nur neue Zeilen befüllen
            item = QTableWidgetItem(f"Spalte {i + 1}")
            self._col_table.setItem(i, 0, item)

            combo = QComboBox()
            combo.addItems(_ALIGN_LABELS)
            combo.currentIndexChanged.connect(self._refresh_preview)
            self._col_table.setCellWidget(i, 1, combo)

        self._col_table.blockSignals(False)

    def _column_config(self) -> list[tuple[str, str]]:
        """Gibt eine Liste von (Name, Ausrichtungslabel) zurück."""
        result = []
        for i in range(self._col_table.rowCount()):
            item  = self._col_table.item(i, 0)
            name  = item.text().strip() if item and item.text().strip() else f"Spalte {i + 1}"
            combo = self._col_table.cellWidget(i, 1)
            align = combo.currentText() if combo else "Links"
            result.append((name, align))
        return result

    def _build_markdown(self) -> str:
        cols       = self._column_config()
        data_rows  = self._rows_spin.value()
        has_header = self._header_check.isChecked()

        # Kopfzeile
        if has_header:
            header = "| " + " | ".join(name for name, _ in cols) + " |"
        else:
            header = "| " + " | ".join(" " * max(len(name), 3) for name, _ in cols) + " |"

        # Trennzeile mit Ausrichtungsmarkierungen
        sep = "| " + " | ".join(_ALIGN_MARKERS[align] for _, align in cols) + " |"

        # Datenzeilen (leere Zellen, Breite = Spaltenname)
        empty_cells = [" " * max(len(name), 3) for name, _ in cols]
        data_row    = "| " + " | ".join(empty_cells) + " |"

        lines = [header, sep] + [data_row] * data_rows
        return "\n".join(lines)

    def _refresh_preview(self) -> None:
        self._preview.setPlainText(self._build_markdown())

    # ── Öffentliche API ───────────────────────────────────────────────────────

    def get_markdown(self) -> str:
        """Gibt den fertigen Markdown-Tabellentext zurück."""
        return self._build_markdown()
