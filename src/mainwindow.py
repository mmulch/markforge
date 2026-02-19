"""Hauptfenster des Markdown-Editors."""

from __future__ import annotations

import os

from PyQt6.QtCore import QSettings, QTimer, Qt, QUrl
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QToolBar,
)

from editor_widget import EditorWidget
from file_tree_widget import FileTreeWidget
from insert_media_dialogs import InsertImageDialog, InsertLinkDialog
from insert_plantuml_dialog import InsertPlantUMLDialog
from insert_table_dialog import InsertTableDialog
from preview_widget import PreviewWidget

_FILTER_OPEN = "Markdown-Dateien (*.md *.markdown);;Textdateien (*.txt);;Alle Dateien (*)"
_FILTER_SAVE = "Markdown-Dateien (*.md);;Textdateien (*.txt);;Alle Dateien (*)"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._file: str | None = None
        self._modified = False
        self._settings = QSettings("MarkdownEditor", "MarkdownEditor")

        self._build_ui()
        self._build_menu()
        self._build_toolbar()
        self._build_statusbar()
        self._connect_signals()
        self._restore_settings()

        self.resize(1280, 800)
        self._update_title()

    # ── UI-Aufbau ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Innerer Splitter: Editor | Vorschau
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._editor   = EditorWidget()
        self._preview  = PreviewWidget()
        self._splitter.addWidget(self._editor)
        self._splitter.addWidget(self._preview)
        self._splitter.setSizes([640, 640])

        # Äußerer Splitter: Dateibaum | (Editor + Vorschau)
        self._outer_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._file_tree = FileTreeWidget()
        self._file_tree.set_root(os.getcwd())
        self._outer_splitter.addWidget(self._file_tree)
        self._outer_splitter.addWidget(self._splitter)
        self._outer_splitter.setSizes([200, 1080])
        self._outer_splitter.setStretchFactor(0, 0)
        self._outer_splitter.setStretchFactor(1, 1)

        self.setCentralWidget(self._outer_splitter)

    def _build_menu(self) -> None:
        mb = self.menuBar()

        # ── Datei ──────────────────────────────────────────────────────────
        m = mb.addMenu("&Datei")
        self._act_new     = self._mk_action("&Neu",              QKeySequence.StandardKey.New,    m)
        self._act_open    = self._mk_action("&Öffnen …",         QKeySequence.StandardKey.Open,   m)
        m.addSeparator()
        self._act_save    = self._mk_action("&Speichern",         QKeySequence.StandardKey.Save,   m)
        self._act_save_as = self._mk_action("Speichern &unter …", QKeySequence.StandardKey.SaveAs, m)
        m.addSeparator()
        quit_act = self._mk_action("&Beenden", QKeySequence.StandardKey.Quit, m)
        quit_act.triggered.connect(self.close)

        # ── Bearbeiten ─────────────────────────────────────────────────────
        m = mb.addMenu("&Bearbeiten")
        undo  = self._mk_action("&Rückgängig",    QKeySequence.StandardKey.Undo,  m)
        redo  = self._mk_action("&Wiederholen",   QKeySequence.StandardKey.Redo,  m)
        m.addSeparator()
        cut   = self._mk_action("&Ausschneiden",  QKeySequence.StandardKey.Cut,   m)
        copy  = self._mk_action("&Kopieren",      QKeySequence.StandardKey.Copy,  m)
        paste = self._mk_action("&Einfügen",      QKeySequence.StandardKey.Paste, m)
        undo.triggered.connect(self._editor.undo)
        redo.triggered.connect(self._editor.redo)
        cut.triggered.connect(self._editor.cut)
        copy.triggered.connect(self._editor.copy)
        paste.triggered.connect(self._editor.paste)

        # ── Einfügen ───────────────────────────────────────────────────────
        m = mb.addMenu("&Einfügen")
        self._act_insert_link    = self._mk_action("&Link …",      "Ctrl+K",       m)
        self._act_insert_image   = self._mk_action("&Bild …",      "Ctrl+Shift+K", m)
        self._act_insert_plantuml = self._mk_action("&PlantUML …", "Ctrl+Shift+U", m)
        m.addSeparator()
        self._act_insert_table   = self._mk_action("&Tabelle …",   "Ctrl+Shift+T", m)

        # ── Ansicht ────────────────────────────────────────────────────────
        m = mb.addMenu("&Ansicht")
        self._act_filetree = self._mk_action(
            "Dateibaum anzeigen", "Ctrl+B", m, checkable=True
        )
        self._act_filetree.setChecked(True)
        self._act_preview = self._mk_action(
            "Vorschau anzeigen", "Ctrl+Shift+P", m, checkable=True
        )
        self._act_preview.setChecked(True)
        m.addSeparator()
        self._act_wrap = self._mk_action("Zeilenumbruch", None, m, checkable=True)
        self._act_wrap.setChecked(True)

        # ── Hilfe ──────────────────────────────────────────────────────────
        m = mb.addMenu("&Hilfe")
        about = self._mk_action("&Über …", None, m)
        about.triggered.connect(self._about)

    def _build_toolbar(self) -> None:
        tb = QToolBar("Werkzeugleiste")
        tb.setMovable(False)
        self.addToolBar(tb)
        tb.addAction(self._act_new)
        tb.addAction(self._act_open)
        tb.addAction(self._act_save)
        tb.addSeparator()
        tb.addAction(self._act_preview)

    def _build_statusbar(self) -> None:
        self._lbl_words = QLabel("0 Wörter")
        self._lbl_pos   = QLabel("Zeile 1, Spalte 1")
        sb = self.statusBar()
        sb.addPermanentWidget(self._lbl_words)
        sb.addPermanentWidget(self._lbl_pos)

    # ── Hilfsmethoden ─────────────────────────────────────────────────────────

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

    # ── Signalverbindungen ────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._act_new.triggered.connect(self._new)
        self._act_open.triggered.connect(self._open)
        self._act_save.triggered.connect(self._save)
        self._act_save_as.triggered.connect(self._save_as)
        self._act_insert_link.triggered.connect(self._insert_link)
        self._act_insert_image.triggered.connect(self._insert_image)
        self._act_insert_plantuml.triggered.connect(self._insert_plantuml)
        self._act_insert_table.triggered.connect(self._insert_table)
        self._act_filetree.toggled.connect(self._file_tree.setVisible)
        self._act_preview.toggled.connect(self._preview.setVisible)
        self._act_wrap.toggled.connect(self._editor.set_word_wrap)
        self._file_tree.file_activated.connect(self._load)
        self._preview.open_file.connect(self._load)

        self._editor.textChanged.connect(self._on_change)
        self._editor.cursorPositionChanged.connect(self._update_pos)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(300)  # 300 ms Entprellung
        self._timer.timeout.connect(self._refresh_preview)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_change(self) -> None:
        self._modified = True
        self._update_title()
        self._update_words()
        self._timer.start()

    def _refresh_preview(self) -> None:
        self._preview.set_markdown(self._editor.toPlainText(), self._doc_base_url())

    def _doc_base_url(self) -> QUrl:
        """Basis-URL für die Vorschau: Verzeichnis der geöffneten Datei."""
        if self._file:
            directory = os.path.dirname(os.path.abspath(self._file))
        else:
            directory = os.path.abspath(os.getcwd())
        return QUrl.fromLocalFile(directory + "/")

    def _update_pos(self) -> None:
        cur = self._editor.textCursor()
        self._lbl_pos.setText(
            f"Zeile {cur.blockNumber() + 1}, Spalte {cur.columnNumber() + 1}"
        )

    def _update_words(self) -> None:
        txt = self._editor.toPlainText().strip()
        n   = len(txt.split()) if txt else 0
        self._lbl_words.setText(f"{n} Wörter")

    def _update_title(self) -> None:
        name = os.path.basename(self._file) if self._file else "Unbenannt"
        mod  = "*" if self._modified else ""
        self.setWindowTitle(f"{mod}{name} — Markdown-Editor")

    # ── Datei-Operationen ─────────────────────────────────────────────────────

    def _new(self) -> None:
        if not self._maybe_save():
            return
        self._editor.clear()
        self._file     = None
        self._modified = False
        self._update_title()
        self._refresh_preview()

    def _open(self) -> None:
        if not self._maybe_save():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Datei öffnen", "", _FILTER_OPEN
        )
        if path:
            self._load(path)

    def _load(self, path: str) -> None:
        try:
            with open(path, encoding="utf-8") as fh:
                self._editor.setPlainText(fh.read())
        except OSError as exc:
            QMessageBox.critical(self, "Fehler", f"Datei konnte nicht geöffnet werden:\n{exc}")
            return
        self._file     = path
        self._modified = False
        self._update_title()
        self._file_tree.set_root(os.path.dirname(os.path.abspath(path)))
        self._refresh_preview()

    def _save(self) -> None:
        if self._file:
            self._write(self._file)
        else:
            self._save_as()

    def _save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Speichern unter", "", _FILTER_SAVE
        )
        if path:
            self._write(path)

    def _write(self, path: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._editor.toPlainText())
        except OSError as exc:
            QMessageBox.critical(self, "Fehler", f"Datei konnte nicht gespeichert werden:\n{exc}")
            return
        self._file     = path
        self._modified = False
        self._update_title()
        self.statusBar().showMessage("Gespeichert.", 3000)

    def _maybe_save(self) -> bool:
        """Gibt True zurück, wenn der aktuelle Inhalt verworfen werden darf."""
        if not self._modified:
            return True
        reply = QMessageBox.question(
            self,
            "Ungespeicherte Änderungen",
            "Möchten Sie die Änderungen speichern?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Save:
            self._save()
            return True
        return reply == QMessageBox.StandardButton.Discard

    # ── Einstellungen ─────────────────────────────────────────────────────────

    def _restore_settings(self) -> None:
        if geo := self._settings.value("geometry"):
            self.restoreGeometry(geo)
        if sizes := self._settings.value("splitter"):
            self._splitter.setSizes([int(s) for s in sizes])
        if sizes := self._settings.value("outer_splitter"):
            self._outer_splitter.setSizes([int(s) for s in sizes])

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if not self._maybe_save():
            event.ignore()
            return
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("splitter", self._splitter.sizes())
        self._settings.setValue("outer_splitter", self._outer_splitter.sizes())
        event.accept()

    # ── Einfügen ──────────────────────────────────────────────────────────────

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

    def _insert_table(self) -> None:
        dlg = InsertTableDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        table_md = dlg.get_markdown()
        cursor   = self._editor.textCursor()

        # Tabelle soll immer auf einer eigenen Zeile beginnen und enden
        prefix = "\n" if cursor.columnNumber() > 0 else ""
        cursor.insertText(f"{prefix}{table_md}\n")
        self._editor.setTextCursor(cursor)
        self._editor.setFocus()

    # ── Über ──────────────────────────────────────────────────────────────────

    def _about(self) -> None:
        QMessageBox.about(
            self,
            "Über Markdown-Editor",
            "<h3>Markdown-Editor 1.0</h3>"
            "<p>Erstellt mit <b>Python 3</b> und <b>PyQt6</b>.</p>"
            "<p>Unterstützte Erweiterungen:<br>"
            "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>",
        )
