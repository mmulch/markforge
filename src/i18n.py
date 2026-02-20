"""Minimal i18n module – supports DE / EN."""

from __future__ import annotations

_lang: str = "en"

_DE: dict[str, str] = {
    # ── Menus ─────────────────────────────────────────────────────────────────
    "&File": "&Datei",
    "&New": "&Neu",
    "&Open …": "&Öffnen …",
    "&Save": "&Speichern",
    "Save &As …": "Speichern &unter …",
    "Export as PDF …": "Als PDF exportieren …",
    # ── Splash screen ─────────────────────────────────────────────────────────
    "Loading …": "Laden …",
    "Initializing interface …": "Oberfläche wird geladen …",
    "Ready": "Bereit",
    # ── PDF import ────────────────────────────────────────────────────────────
    "Importing PDF …": "PDF wird importiert …",
    "&Import PDF …": "&PDF importieren …",
    "Import PDF": "PDF importieren",
    "New File": "Neue Datei",
    "File name:": "Dateiname:",
    "pymupdf4llm is not installed.\nInstall it with: pip install pymupdf4llm":
        "pymupdf4llm ist nicht installiert.\nInstallieren mit: pip install pymupdf4llm",
    "Could not import PDF:\n{exc}": "PDF konnte nicht importiert werden:\n{exc}",
    "&Quit": "&Beenden",
    "&Edit": "&Bearbeiten",
    "&Undo": "&Rückgängig",
    "&Redo": "&Wiederholen",
    "Cu&t": "&Ausschneiden",
    "&Copy": "&Kopieren",
    "&Paste": "&Einfügen",
    "&Insert": "&Einfügen",
    "&Link …": "&Link …",
    "&Image …": "&Bild …",
    "&PlantUML …": "&PlantUML …",
    "&Table …": "&Tabelle …",
    "&View": "&Ansicht",
    "Show file tree": "Dateibaum anzeigen",
    "Show preview": "Vorschau anzeigen",
    "Word wrap": "Zeilenumbruch",
    "Light preview": "Helle Vorschau",
    "Light editor": "Heller Editor",
    "Settings …": "Einstellungen …",
    "&Help": "&Hilfe",
    "&Markdown …": "&Markdown …",
    "&About …": "&Über …",
    # ── Toolbar ───────────────────────────────────────────────────────────────
    "Toolbar": "Werkzeugleiste",
    # ── Status bar ────────────────────────────────────────────────────────────
    "{n} words": "{n} Wörter",
    "Line {line}, Col {col}": "Zeile {line}, Spalte {col}",
    # ── Window title ──────────────────────────────────────────────────────────
    "Untitled": "Unbenannt",
    # ── File dialogs ──────────────────────────────────────────────────────────
    "Open File": "Datei öffnen",
    "Save As": "Speichern unter",
    "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*)":
        "Markdown-Dateien (*.md *.markdown);;Textdateien (*.txt);;Alle Dateien (*)",
    "Markdown files (*.md);;Text files (*.txt);;All files (*)":
        "Markdown-Dateien (*.md);;Textdateien (*.txt);;Alle Dateien (*)",
    # ── Status / messages ─────────────────────────────────────────────────────
    "Export as PDF": "Als PDF exportieren",
    "PDF files (*.pdf);;All files (*)": "PDF-Dateien (*.pdf);;Alle Dateien (*)",
    "PDF saved: {path}": "PDF gespeichert: {path}",
    "Could not save PDF:\n{path}": "PDF konnte nicht gespeichert werden:\n{path}",
    "Saved.": "Gespeichert.",
    "Unsaved Changes": "Ungespeicherte Änderungen",
    "Do you want to save the changes?": "Möchten Sie die Änderungen speichern?",
    "Error": "Fehler",
    "Could not open file:\n{exc}": "Datei konnte nicht geöffnet werden:\n{exc}",
    "Could not save file:\n{exc}": "Datei konnte nicht gespeichert werden:\n{exc}",
    # ── About ─────────────────────────────────────────────────────────────────
    "About MarkForge": "Über MarkForge",
    "<h3>MarkForge 1.0</h3>"
    "<p>Created with <b>Python 3</b> and <b>PyQt6</b>.</p>"
    "<p>Supported extensions:<br>"
    "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
    "<hr>"
    "<p>Copyright &copy; Marcel Mulch</p>"
    "<p>License: GNU General Public License 3.0</p>":
        "<h3>Markdown-Editor 1.0</h3>"
        "<p>Erstellt mit <b>Python 3</b> und <b>PyQt6</b>.</p>"
        "<p>Unterstützte Erweiterungen:<br>"
        "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
        "<hr>"
        "<p>Copyright &copy; Marcel Mulch</p>"
        "<p>Lizenz: GNU General Public License 3.0</p>",
    # ── Table dialog ──────────────────────────────────────────────────────────
    "Insert Table": "Tabelle einfügen",
    "Table Structure": "Tabellenstruktur",
    "Number of data rows (excluding header)": "Anzahl der Datenzeilen (ohne Kopfzeile)",
    "Data rows:": "Datenzeilen:",
    "Number of columns": "Anzahl der Spalten",
    "Columns:": "Spalten:",
    "Header row with column titles": "Kopfzeile mit Spaltentiteln",
    "Column Configuration": "Spaltenkonfiguration",
    "Column Name": "Spaltenname",
    "Alignment": "Ausrichtung",
    "Preview (Markdown)": "Vorschau (Markdown)",
    "Insert": "Einfügen",
    "Cancel": "Abbrechen",
    "Column {n}": "Spalte {n}",
    "Left": "Links",
    "Center": "Zentriert",
    "Right": "Rechts",
    # ── Link dialog ───────────────────────────────────────────────────────────
    "Insert Link": "Link einfügen",
    "Link Properties": "Link-Eigenschaften",
    "e.g.  Click here": "z. B.  Hier klicken",
    "Display text:": "Anzeigetext:",
    "https://example.com": "https://beispiel.de",
    "URL:": "URL:",
    "Optional tooltip (shown on hover)": "Optionaler Tooltip (erscheint beim Hover)",
    "Title (optional):": "Titel (optional):",
    # ── Image dialog ──────────────────────────────────────────────────────────
    "Insert Image": "Bild einfügen",
    "Image Properties": "Bild-Eigenschaften",
    "Short image description (for screen readers)": "Kurze Bildbeschreibung (für Screenreader)",
    "Alt Text:": "Alt-Text:",
    "https://example.com/image.png  or  local path":
        "https://beispiel.de/bild.png  oder  lokaler Pfad",
    "Select local image file": "Lokale Bilddatei auswählen",
    "URL / Path:": "URL / Pfad:",
    "Images (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;All files (*)":
        "Bilder (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;Alle Dateien (*)",
    "Select Image File": "Bilddatei auswählen",
    # ── PlantUML dialog ───────────────────────────────────────────────────────
    "Insert PlantUML Diagram": "PlantUML-Diagramm einfügen",
    "Diagram type:": "Diagrammtyp:",
    "PlantUML code:": "PlantUML-Code:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (internet connection required).":
        "Tipp: Die Vorschau des Diagramms erscheint nach dem Einfügen automatisch"
        " im Hauptfenster (Internetverbindung erforderlich).",
    # PlantUML template names
    "Sequence diagram": "Sequenzdiagramm",
    "Class diagram": "Klassendiagramm",
    "Activity diagram": "Aktivitätsdiagramm",
    "State diagram": "Zustandsdiagramm",
    "Component diagram": "Komponentendiagramm",
    "Use case diagram": "Anwendungsfalldiagramm",
    "Gantt diagram": "Gantt-Diagramm",
    "Mind map": "MindMap",
    "WBS (Work breakdown)": "WBS (Arbeitsstruktur)",
    "Timing diagram": "Timing-Diagramm",
    "Deployment diagram": "Deployment-Diagramm",
    "JSON": "JSON",
    # ── File tree ─────────────────────────────────────────────────────────────
    "Current root directory": "Aktuelles Stammverzeichnis",
    "Choose Directory": "Verzeichnis wählen",
    # ── Settings dialog ───────────────────────────────────────────────────────
    "Settings": "Einstellungen",
    "Language:": "Sprache:",
    "Restart required to apply language changes.":
        "Neustart erforderlich, um Sprachänderungen anzuwenden.",
    "Editor theme:": "Editor-Theme:",
    "Preview theme:": "Vorschau-Theme:",
    "App theme:": "App-Theme:",
    "App theme requires restart.": "App-Theme erfordert einen Neustart.",
}


def setup(lang: str) -> None:
    """Call once before any UI is built to select the active language."""
    global _lang
    _lang = lang if lang in ("de", "en") else "en"


def current() -> str:
    """Return the active language code ('de' or 'en')."""
    return _lang


def tr(text: str, **kwargs: object) -> str:
    """Translate *text* and optionally format with named placeholders."""
    result = _DE.get(text, text) if _lang == "de" else text
    return result.format(**kwargs) if kwargs else result
