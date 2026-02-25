"""Minimal i18n module – supports DE / EN / AR / VI / SV / UK / KN / HI."""

from __future__ import annotations

_lang: str = "en"

# Language registry: code → display name (shown in Settings combo)
LANGUAGES: dict[str, str] = {
    "en": "English",
    "de": "Deutsch",
    "ar": "عربي (مصري)",
    "vi": "Tiếng Việt",
    "sv": "Svenska",
    "uk": "Українська",
    "kn": "ಕನ್ನಡ",
    "hi": "हिंदी",
}

# Right-to-left languages
RTL_LANGUAGES: frozenset[str] = frozenset({"ar"})

# ── German ────────────────────────────────────────────────────────────────────
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
    "File name:\nFolder: {path}": "Dateiname:\nOrdner: {path}",
    "Open &Folder …": "&Ordner öffnen …",
    "Open Folder": "Ordner öffnen",
    "Open or create a Markdown file to start editing.":
        "Öffnen oder erstellen Sie eine Markdown-Datei, um mit der Bearbeitung zu beginnen.",
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
    # ── Help menu ─────────────────────────────────────────────────────────────
    "&User Manual …": "&Benutzerhandbuch …",
    # ── Git integration ───────────────────────────────────────────────────────
    "Open from &Git …": "Aus &Git öffnen …",
    "Open File from Git": "Datei aus Git öffnen",
    "GitHub / Bitbucket file URL:": "GitHub-/Bitbucket-Datei-URL:",
    "Ref (branch/tag/commit):": "Ref (Branch/Tag/Commit):",
    "Cloning repository …": "Repository wird geklont …",
    "Open from Git": "Aus Git öffnen",
    "Git Push": "Git Push",
    "Pushing to remote …": "Zum Remote wird gepusht …",
    "Pushed to remote.": "Zum Remote gepusht.",
    "Git push failed:\n{exc}": "Git-Push fehlgeschlagen:\n{exc}",
    "Clone failed:\n{exc}": "Klonen fehlgeschlagen:\n{exc}",
    "File not found in repository:\n{path}": "Datei nicht im Repository gefunden:\n{path}",
    "Delete Git Temp Directory?": "Git-Temp-Verzeichnis löschen?",
    "A temporary Git clone is open:\n{path}\n\nDelete it now?":
        "Ein temporärer Git-Klon ist geöffnet:\n{path}\n\nJetzt löschen?",
    "Push to": "Pushen nach",
    "Current branch ({branch})": "Aktueller Branch ({branch})",
    "New branch:": "Neuer Branch:",
    "Create Pull Request": "Pull Request erstellen",
    "PR title:": "PR-Titel:",
    "Target branch:": "Zielbranch:",
    "Git Commit & Push": "Git Commit & Push",
    "Git Authentication": "Git-Authentifizierung",
    "Auth method:": "Auth-Methode:",
    "HTTPS (embedded)": "HTTPS (eingebettet)",
    "HTTPS (git binary)":       "HTTPS (git-Programm)",
    "SSH (key file)": "SSH (Schlüsseldatei)",
    "Token:": "Token:",
    "SSH key:": "SSH-Schlüssel:",
    "Passphrase:": "Passphrase:",
    "Select SSH Key File": "SSH-Schlüsseldatei auswählen",
    "No credentials configured. Public repositories will still work.\n"
    "Configure credentials in View → Settings.":
        "Keine Anmeldedaten konfiguriert. Öffentliche Repos funktionieren weiterhin.\n"
        "Anmeldedaten unter Ansicht → Einstellungen konfigurieren.",
    "Push rejected (non-fast-forward).\nTry saving again using 'New branch'.":
        "Push abgelehnt (non-fast-forward).\n"
        "Versuche erneut zu speichern und 'Neuer Branch' zu wählen.",
    "Commit message:": "Commit-Nachricht:",
    "Amend previous commit":    "Vorherigen Commit überschreiben",
    "Git &Squash …":            "Git &Squash …",
    "Git Squash Commits":       "Git-Commits zusammenführen",
    "Select all new commits":   "Alle neuen Commits auswählen",
    "SHA":                      "SHA",
    "Message":                  "Nachricht",
    "Author":                   "Autor",
    "Date":                     "Datum",
    "Squash commit message:":   "Zusammengeführte Commit-Nachricht:",
    "Enter the combined commit message …":
        "Kombinierte Commit-Nachricht eingeben …",
    "Squash && Push":           "Zusammenführen && Pushen",
    "Select at least 2 commits to squash.":
        "Bitte mindestens 2 Commits zum Zusammenführen auswählen.",
    "The selected commits must form a contiguous range starting from the most recent commit (HEAD).":
        "Die gewählten Commits müssen eine zusammenhängende Reihe ab dem neuesten Commit (HEAD) bilden.",
    "cannot be empty.":         "darf nicht leer sein.",
    "Squashing commits …":      "Commits werden zusammengeführt …",
    "Squash complete.":         "Zusammenführung abgeschlossen.",
    "Git squash failed:\n{exc}": "Git-Squash fehlgeschlagen:\n{exc}",
    "Could not read commit history:\n{exc}":
        "Commit-Verlauf konnte nicht gelesen werden:\n{exc}",
    "No new commits found on this branch.":
        "Keine neuen Commits auf diesem Branch gefunden.",
    "No new commits found compared to '{base}'.":
        "Keine neuen Commits im Vergleich zu '{base}' gefunden.",
    "Loading …": "Wird geladen …",
    "Reload":    "Neu laden",
    "Git squash is only available with SSH or git-binary authentication.":
        "Git-Squash ist nur mit SSH- oder git-Binary-Authentifizierung verfügbar.",
    "Username:": "Benutzername:",
    "Name:":     "Name:",
    "Email:":    "E-Mail:",
    # ── Mermaid ───────────────────────────────────────────────────────────────
    "Insert Mermaid Diagram": "Mermaid-Diagramm einfügen",
    "Mermaid code:":          "Mermaid-Code:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (mermaid.js is loaded from CDN on first use).":
        "Tipp: Die Vorschau des Diagramms erscheint nach dem Einfügen automatisch"
        " im Hauptfenster (mermaid.js wird beim ersten Einsatz vom CDN geladen).",
    "&Mermaid …": "&Mermaid …",
    "Mermaid …":  "Mermaid …",
    # Mermaid template names
    "Flowchart":   "Flussdiagramm",
    "Pie chart":   "Tortendiagramm",
    "ER diagram":  "ER-Diagramm",
    "Git graph":   "Git-Graph",
    "Gantt":       "Gantt",
    # ── Proxy ─────────────────────────────────────────────────────────────────
    "HTTP Proxy": "HTTP-Proxy",
    "Proxy URL:": "Proxy-URL:",
    "Proxy username:": "Proxy-Benutzername:",
    "Proxy password:": "Proxy-Passwort:",
    "Leave empty to use system proxy settings.":
        "Leer lassen, um die Systemproxy-Einstellungen zu verwenden.",
    # ── Find & Replace ────────────────────────────────────────────────────────
    "&Find …":             "&Suchen …",
    "Find && &Replace …":  "Suchen && &Ersetzen …",
    "Find…":               "Suchen…",
    "Replace…":            "Ersetzen…",
    "Replace":             "Ersetzen",
    "Replace All":         "Alle ersetzen",
    "Match case":          "Groß-/Kleinschreibung",
    "Whole words":         "Ganze Wörter",
    "No results":          "Keine Treffer",
    "{cur} / {total}":     "{cur} / {total}",
    "{n} replaced":        "{n} ersetzt",
    "Find previous (Shift+Enter)": "Vorheriges suchen (Umschalt+Eingabe)",
    "Find next (Enter)":           "Nächstes suchen (Eingabe)",
    "Close (Escape)":              "Schließen (Escape)",
    # ── Outline ───────────────────────────────────────────────────────────────
    "Outline":       "Gliederung",
    "Show outline":  "Gliederung anzeigen",
}

# ── Arabic (Egyptian / MSA) ───────────────────────────────────────────────────
_AR: dict[str, str] = {
    # ── Menus ─────────────────────────────────────────────────────────────────
    "&File": "&ملف",
    "&New": "&جديد",
    "&Open …": "&فتح …",
    "&Save": "&حفظ",
    "Save &As …": "حفظ &باسم …",
    "Export as PDF …": "تصدير كـ PDF …",
    # ── Splash screen ─────────────────────────────────────────────────────────
    "Loading …": "جاري التحميل …",
    "Initializing interface …": "جاري تهيئة الواجهة …",
    "Ready": "جاهز",
    # ── PDF import ────────────────────────────────────────────────────────────
    "Importing PDF …": "جاري استيراد PDF …",
    "&Import PDF …": "&استيراد PDF …",
    "Import PDF": "استيراد PDF",
    "New File": "ملف جديد",
    "File name:\nFolder: {path}": "اسم الملف:\nالمجلد: {path}",
    "Open &Folder …": "فتح &مجلد …",
    "Open Folder": "فتح مجلد",
    "Open or create a Markdown file to start editing.":
        "افتح أو أنشئ ملف Markdown للبدء في التحرير.",
    "pymupdf4llm is not installed.\nInstall it with: pip install pymupdf4llm":
        "pymupdf4llm غير مثبت.\nثبّته بـ: pip install pymupdf4llm",
    "Could not import PDF:\n{exc}": "تعذّر استيراد PDF:\n{exc}",
    "&Quit": "&خروج",
    "&Edit": "&تعديل",
    "&Undo": "&تراجع",
    "&Redo": "&إعادة",
    "Cu&t": "&قص",
    "&Copy": "&نسخ",
    "&Paste": "&لصق",
    "&Insert": "&إدراج",
    "&Link …": "&رابط …",
    "&Image …": "&صورة …",
    "&PlantUML …": "&PlantUML …",
    "&Table …": "&جدول …",
    "&View": "&عرض",
    "Show file tree": "عرض شجرة الملفات",
    "Show preview": "عرض المعاينة",
    "Word wrap": "التفاف الأسطر",
    "Light preview": "معاينة فاتحة",
    "Light editor": "محرر فاتح",
    "Settings …": "إعدادات …",
    "&Help": "&مساعدة",
    "&Markdown …": "&Markdown …",
    "&About …": "&حول …",
    # ── Toolbar ───────────────────────────────────────────────────────────────
    "Toolbar": "شريط الأدوات",
    # ── Status bar ────────────────────────────────────────────────────────────
    "{n} words": "{n} كلمات",
    "Line {line}, Col {col}": "سطر {line}، عمود {col}",
    # ── Window title ──────────────────────────────────────────────────────────
    "Untitled": "بدون عنوان",
    # ── File dialogs ──────────────────────────────────────────────────────────
    "Open File": "فتح ملف",
    "Save As": "حفظ باسم",
    "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*)":
        "ملفات Markdown (*.md *.markdown);;ملفات نصية (*.txt);;جميع الملفات (*)",
    "Markdown files (*.md);;Text files (*.txt);;All files (*)":
        "ملفات Markdown (*.md);;ملفات نصية (*.txt);;جميع الملفات (*)",
    # ── Status / messages ─────────────────────────────────────────────────────
    "Export as PDF": "تصدير كـ PDF",
    "PDF files (*.pdf);;All files (*)": "ملفات PDF (*.pdf);;جميع الملفات (*)",
    "PDF saved: {path}": "تم حفظ PDF: {path}",
    "Could not save PDF:\n{path}": "تعذّر حفظ PDF:\n{path}",
    "Saved.": "تم الحفظ.",
    "Unsaved Changes": "تغييرات غير محفوظة",
    "Do you want to save the changes?": "هل تريد حفظ التغييرات؟",
    "Error": "خطأ",
    "Could not open file:\n{exc}": "تعذّر فتح الملف:\n{exc}",
    "Could not save file:\n{exc}": "تعذّر حفظ الملف:\n{exc}",
    # ── About ─────────────────────────────────────────────────────────────────
    "About MarkForge": "حول MarkForge",
    "<h3>MarkForge 1.0</h3>"
    "<p>Created with <b>Python 3</b> and <b>PyQt6</b>.</p>"
    "<p>Supported extensions:<br>"
    "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
    "<hr>"
    "<p>Copyright &copy; Marcel Mulch</p>"
    "<p>License: GNU General Public License 3.0</p>":
        "<h3>MarkForge 1.0</h3>"
        "<p>أُنشئ بـ <b>Python 3</b> و<b>PyQt6</b>.</p>"
        "<p>الامتدادات المدعومة:<br>"
        "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
        "<hr>"
        "<p>حقوق النشر &copy; Marcel Mulch</p>"
        "<p>الرخصة: GNU General Public License 3.0</p>",
    # ── Table dialog ──────────────────────────────────────────────────────────
    "Insert Table": "إدراج جدول",
    "Table Structure": "بنية الجدول",
    "Number of data rows (excluding header)": "عدد صفوف البيانات (باستثناء الرأس)",
    "Data rows:": "صفوف البيانات:",
    "Number of columns": "عدد الأعمدة",
    "Columns:": "الأعمدة:",
    "Header row with column titles": "صف الرأس مع عناوين الأعمدة",
    "Column Configuration": "تكوين الأعمدة",
    "Column Name": "اسم العمود",
    "Alignment": "المحاذاة",
    "Preview (Markdown)": "معاينة (Markdown)",
    "Insert": "إدراج",
    "Cancel": "إلغاء",
    "Column {n}": "عمود {n}",
    "Left": "يسار",
    "Center": "وسط",
    "Right": "يمين",
    # ── Link dialog ───────────────────────────────────────────────────────────
    "Insert Link": "إدراج رابط",
    "Link Properties": "خصائص الرابط",
    "e.g.  Click here": "مثال:  انقر هنا",
    "Display text:": "نص العرض:",
    "https://example.com": "https://example.com",
    "URL:": "الرابط:",
    "Optional tooltip (shown on hover)": "تلميح اختياري (يظهر عند التمرير)",
    "Title (optional):": "العنوان (اختياري):",
    # ── Image dialog ──────────────────────────────────────────────────────────
    "Insert Image": "إدراج صورة",
    "Image Properties": "خصائص الصورة",
    "Short image description (for screen readers)": "وصف مختصر للصورة (لقارئات الشاشة)",
    "Alt Text:": "النص البديل:",
    "https://example.com/image.png  or  local path":
        "https://example.com/image.png  أو  مسار محلي",
    "Select local image file": "اختر ملف صورة محلي",
    "URL / Path:": "الرابط / المسار:",
    "Images (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;All files (*)":
        "صور (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;جميع الملفات (*)",
    "Select Image File": "اختر ملف صورة",
    # ── PlantUML dialog ───────────────────────────────────────────────────────
    "Insert PlantUML Diagram": "إدراج مخطط PlantUML",
    "Diagram type:": "نوع المخطط:",
    "PlantUML code:": "كود PlantUML:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (internet connection required).":
        "نصيحة: تظهر معاينة المخطط تلقائياً في النافذة الرئيسية بعد الإدراج"
        " (مطلوب اتصال بالإنترنت).",
    # PlantUML template names
    "Sequence diagram": "مخطط تسلسلي",
    "Class diagram": "مخطط الفئات",
    "Activity diagram": "مخطط النشاط",
    "State diagram": "مخطط الحالة",
    "Component diagram": "مخطط المكونات",
    "Use case diagram": "مخطط حالات الاستخدام",
    "Gantt diagram": "مخطط غانت",
    "Mind map": "خريطة ذهنية",
    "WBS (Work breakdown)": "WBS (هيكل تفصيل العمل)",
    "Timing diagram": "مخطط التوقيت",
    "Deployment diagram": "مخطط النشر",
    "JSON": "JSON",
    # ── File tree ─────────────────────────────────────────────────────────────
    "Current root directory": "المجلد الجذري الحالي",
    "Choose Directory": "اختر مجلداً",
    # ── Settings dialog ───────────────────────────────────────────────────────
    "Settings": "الإعدادات",
    "Language:": "اللغة:",
    "Restart required to apply language changes.":
        "يلزم إعادة التشغيل لتطبيق تغييرات اللغة.",
    "Editor theme:": "ثيم المحرر:",
    "Preview theme:": "ثيم المعاينة:",
    "App theme:": "ثيم التطبيق:",
    "App theme requires restart.": "ثيم التطبيق يتطلب إعادة التشغيل.",
    # ── Help menu ─────────────────────────────────────────────────────────────
    "&User Manual …": "&دليل المستخدم …",
    # ── Git integration ───────────────────────────────────────────────────────
    "Open from &Git …": "فتح من &Git …",
    "Open File from Git": "فتح ملف من Git",
    "GitHub / Bitbucket file URL:": "رابط ملف GitHub / Bitbucket:",
    "Ref (branch/tag/commit):": "المرجع (فرع/وسم/commit):",
    "Cloning repository …": "جاري نسخ المستودع …",
    "Open from Git": "فتح من Git",
    "Git Push": "Git Push",
    "Pushing to remote …": "جاري الرفع إلى الخادم …",
    "Pushed to remote.": "تم الرفع إلى الخادم.",
    "Git push failed:\n{exc}": "فشل Git push:\n{exc}",
    "Clone failed:\n{exc}": "فشل النسخ:\n{exc}",
    "File not found in repository:\n{path}": "الملف غير موجود في المستودع:\n{path}",
    "Delete Git Temp Directory?": "حذف مجلد Git المؤقت؟",
    "A temporary Git clone is open:\n{path}\n\nDelete it now?":
        "نسخة Git مؤقتة مفتوحة:\n{path}\n\nهل تحذفها الآن؟",
    "Push to": "الرفع إلى",
    "Current branch ({branch})": "الفرع الحالي ({branch})",
    "New branch:": "فرع جديد:",
    "Create Pull Request": "إنشاء Pull Request",
    "PR title:": "عنوان PR:",
    "Target branch:": "الفرع المستهدف:",
    "Git Commit & Push": "Git Commit & Push",
    "Git Authentication": "مصادقة Git",
    "Auth method:": "طريقة المصادقة:",
    "HTTPS (embedded)": "HTTPS (مدمج)",
    "HTTPS (git binary)": "HTTPS (git ثنائي)",
    "SSH (key file)": "SSH (ملف المفتاح)",
    "Token:": "الرمز:",
    "SSH key:": "مفتاح SSH:",
    "Passphrase:": "عبارة المرور:",
    "Select SSH Key File": "اختر ملف مفتاح SSH",
    "No credentials configured. Public repositories will still work.\n"
    "Configure credentials in View → Settings.":
        "لا توجد بيانات اعتماد مكوّنة. المستودعات العامة ستعمل.\n"
        "كوّن البيانات في عرض → إعدادات.",
    "Push rejected (non-fast-forward).\nTry saving again using 'New branch'.":
        "رُفض Push (non-fast-forward).\nجرّب الحفظ مجدداً بـ 'فرع جديد'.",
    "Commit message:": "رسالة commit:",
    "Amend previous commit": "تعديل الـ commit السابق",
    "Git &Squash …": "Git &Squash …",
    "Git Squash Commits": "دمج commits في Git",
    "Select all new commits": "اختر جميع الـ commits الجديدة",
    "SHA": "SHA",
    "Message": "الرسالة",
    "Author": "المؤلف",
    "Date": "التاريخ",
    "Squash commit message:": "رسالة commit المدمجة:",
    "Enter the combined commit message …": "أدخل رسالة commit المجمّعة …",
    "Squash && Push": "دمج && رفع",
    "Select at least 2 commits to squash.": "اختر commit-ين على الأقل للدمج.",
    "The selected commits must form a contiguous range starting from the most recent commit (HEAD).":
        "يجب أن تشكّل الـ commits المختارة نطاقاً متصلاً من أحدث commit (HEAD).",
    "cannot be empty.": "لا يمكن أن تكون فارغة.",
    "Squashing commits …": "جاري دمج الـ commits …",
    "Squash complete.": "اكتمل الدمج.",
    "Git squash failed:\n{exc}": "فشل Git squash:\n{exc}",
    "Could not read commit history:\n{exc}": "تعذّر قراءة سجل الـ commits:\n{exc}",
    "No new commits found on this branch.": "لا توجد commits جديدة على هذا الفرع.",
    "No new commits found compared to '{base}'.":
        "لا توجد commits جديدة مقارنة بـ '{base}'.",
    "Reload": "إعادة تحميل",
    "Git squash is only available with SSH or git-binary authentication.":
        "Git squash متاح فقط مع مصادقة SSH أو git-binary.",
    "Username:": "اسم المستخدم:",
    "Name:": "الاسم:",
    "Email:": "البريد الإلكتروني:",
    # ── Mermaid ───────────────────────────────────────────────────────────────
    "Insert Mermaid Diagram": "إدراج مخطط Mermaid",
    "Mermaid code:": "كود Mermaid:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (mermaid.js is loaded from CDN on first use).":
        "نصيحة: تظهر معاينة المخطط تلقائياً في النافذة الرئيسية بعد الإدراج"
        " (يُحمَّل mermaid.js من CDN عند أول استخدام).",
    "&Mermaid …": "&Mermaid …",
    "Mermaid …": "Mermaid …",
    # Mermaid template names
    "Flowchart": "مخطط تدفق",
    "Pie chart": "مخطط دائري",
    "ER diagram": "مخطط ER",
    "Git graph": "رسم بياني Git",
    "Gantt": "غانت",
    # ── Proxy ─────────────────────────────────────────────────────────────────
    "HTTP Proxy": "بروكسي HTTP",
    "Proxy URL:": "رابط البروكسي:",
    "Proxy username:": "اسم مستخدم البروكسي:",
    "Proxy password:": "كلمة مرور البروكسي:",
    "Leave empty to use system proxy settings.":
        "اتركه فارغاً لاستخدام إعدادات البروكسي للنظام.",
}

# ── Vietnamese ────────────────────────────────────────────────────────────────
_VI: dict[str, str] = {
    # ── Menus ─────────────────────────────────────────────────────────────────
    "&File": "&Tệp",
    "&New": "&Mới",
    "&Open …": "&Mở …",
    "&Save": "&Lưu",
    "Save &As …": "Lưu &thành …",
    "Export as PDF …": "Xuất sang PDF …",
    # ── Splash screen ─────────────────────────────────────────────────────────
    "Loading …": "Đang tải …",
    "Initializing interface …": "Đang khởi tạo giao diện …",
    "Ready": "Sẵn sàng",
    # ── PDF import ────────────────────────────────────────────────────────────
    "Importing PDF …": "Đang nhập PDF …",
    "&Import PDF …": "&Nhập PDF …",
    "Import PDF": "Nhập PDF",
    "New File": "Tệp mới",
    "File name:\nFolder: {path}": "Tên tệp:\nThư mục: {path}",
    "Open &Folder …": "Mở &thư mục …",
    "Open Folder": "Mở thư mục",
    "Open or create a Markdown file to start editing.":
        "Mở hoặc tạo tệp Markdown để bắt đầu chỉnh sửa.",
    "pymupdf4llm is not installed.\nInstall it with: pip install pymupdf4llm":
        "pymupdf4llm chưa được cài đặt.\nCài đặt bằng: pip install pymupdf4llm",
    "Could not import PDF:\n{exc}": "Không thể nhập PDF:\n{exc}",
    "&Quit": "&Thoát",
    "&Edit": "&Chỉnh sửa",
    "&Undo": "&Hoàn tác",
    "&Redo": "&Làm lại",
    "Cu&t": "C&ắt",
    "&Copy": "&Sao chép",
    "&Paste": "&Dán",
    "&Insert": "&Chèn",
    "&Link …": "&Liên kết …",
    "&Image …": "&Hình ảnh …",
    "&PlantUML …": "&PlantUML …",
    "&Table …": "&Bảng …",
    "&View": "&Xem",
    "Show file tree": "Hiển thị cây tệp",
    "Show preview": "Hiển thị xem trước",
    "Word wrap": "Ngắt dòng tự động",
    "Light preview": "Xem trước sáng",
    "Light editor": "Trình soạn sáng",
    "Settings …": "Cài đặt …",
    "&Help": "&Trợ giúp",
    "&Markdown …": "&Markdown …",
    "&About …": "&Giới thiệu …",
    # ── Toolbar ───────────────────────────────────────────────────────────────
    "Toolbar": "Thanh công cụ",
    # ── Status bar ────────────────────────────────────────────────────────────
    "{n} words": "{n} từ",
    "Line {line}, Col {col}": "Dòng {line}, Cột {col}",
    # ── Window title ──────────────────────────────────────────────────────────
    "Untitled": "Chưa đặt tên",
    # ── File dialogs ──────────────────────────────────────────────────────────
    "Open File": "Mở tệp",
    "Save As": "Lưu thành",
    "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*)":
        "Tệp Markdown (*.md *.markdown);;Tệp văn bản (*.txt);;Tất cả tệp (*)",
    "Markdown files (*.md);;Text files (*.txt);;All files (*)":
        "Tệp Markdown (*.md);;Tệp văn bản (*.txt);;Tất cả tệp (*)",
    # ── Status / messages ─────────────────────────────────────────────────────
    "Export as PDF": "Xuất sang PDF",
    "PDF files (*.pdf);;All files (*)": "Tệp PDF (*.pdf);;Tất cả tệp (*)",
    "PDF saved: {path}": "Đã lưu PDF: {path}",
    "Could not save PDF:\n{path}": "Không thể lưu PDF:\n{path}",
    "Saved.": "Đã lưu.",
    "Unsaved Changes": "Thay đổi chưa lưu",
    "Do you want to save the changes?": "Bạn có muốn lưu các thay đổi không?",
    "Error": "Lỗi",
    "Could not open file:\n{exc}": "Không thể mở tệp:\n{exc}",
    "Could not save file:\n{exc}": "Không thể lưu tệp:\n{exc}",
    # ── About ─────────────────────────────────────────────────────────────────
    "About MarkForge": "Giới thiệu MarkForge",
    "<h3>MarkForge 1.0</h3>"
    "<p>Created with <b>Python 3</b> and <b>PyQt6</b>.</p>"
    "<p>Supported extensions:<br>"
    "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
    "<hr>"
    "<p>Copyright &copy; Marcel Mulch</p>"
    "<p>License: GNU General Public License 3.0</p>":
        "<h3>MarkForge 1.0</h3>"
        "<p>Được tạo bằng <b>Python 3</b> và <b>PyQt6</b>.</p>"
        "<p>Các tiện ích mở rộng được hỗ trợ:<br>"
        "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
        "<hr>"
        "<p>Bản quyền &copy; Marcel Mulch</p>"
        "<p>Giấy phép: GNU General Public License 3.0</p>",
    # ── Table dialog ──────────────────────────────────────────────────────────
    "Insert Table": "Chèn bảng",
    "Table Structure": "Cấu trúc bảng",
    "Number of data rows (excluding header)": "Số hàng dữ liệu (không tính tiêu đề)",
    "Data rows:": "Hàng dữ liệu:",
    "Number of columns": "Số cột",
    "Columns:": "Số cột:",
    "Header row with column titles": "Hàng tiêu đề với tên cột",
    "Column Configuration": "Cấu hình cột",
    "Column Name": "Tên cột",
    "Alignment": "Căn chỉnh",
    "Preview (Markdown)": "Xem trước (Markdown)",
    "Insert": "Chèn",
    "Cancel": "Hủy",
    "Column {n}": "Cột {n}",
    "Left": "Trái",
    "Center": "Giữa",
    "Right": "Phải",
    # ── Link dialog ───────────────────────────────────────────────────────────
    "Insert Link": "Chèn liên kết",
    "Link Properties": "Thuộc tính liên kết",
    "e.g.  Click here": "vd:  Nhấn vào đây",
    "Display text:": "Văn bản hiển thị:",
    "https://example.com": "https://example.com",
    "URL:": "URL:",
    "Optional tooltip (shown on hover)": "Chú giải (hiển thị khi di chuột)",
    "Title (optional):": "Tiêu đề (tùy chọn):",
    # ── Image dialog ──────────────────────────────────────────────────────────
    "Insert Image": "Chèn hình ảnh",
    "Image Properties": "Thuộc tính hình ảnh",
    "Short image description (for screen readers)":
        "Mô tả ngắn cho hình ảnh (trình đọc màn hình)",
    "Alt Text:": "Văn bản thay thế:",
    "https://example.com/image.png  or  local path":
        "https://example.com/image.png  hoặc  đường dẫn cục bộ",
    "Select local image file": "Chọn tệp hình ảnh cục bộ",
    "URL / Path:": "URL / Đường dẫn:",
    "Images (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;All files (*)":
        "Hình ảnh (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;Tất cả tệp (*)",
    "Select Image File": "Chọn tệp hình ảnh",
    # ── PlantUML dialog ───────────────────────────────────────────────────────
    "Insert PlantUML Diagram": "Chèn sơ đồ PlantUML",
    "Diagram type:": "Loại sơ đồ:",
    "PlantUML code:": "Mã PlantUML:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (internet connection required).":
        "Mẹo: Xem trước sơ đồ tự động xuất hiện trong cửa sổ chính sau khi chèn"
        " (cần kết nối internet).",
    # PlantUML template names
    "Sequence diagram": "Sơ đồ tuần tự",
    "Class diagram": "Sơ đồ lớp",
    "Activity diagram": "Sơ đồ hoạt động",
    "State diagram": "Sơ đồ trạng thái",
    "Component diagram": "Sơ đồ thành phần",
    "Use case diagram": "Sơ đồ ca sử dụng",
    "Gantt diagram": "Sơ đồ Gantt",
    "Mind map": "Bản đồ tư duy",
    "WBS (Work breakdown)": "WBS (Phân tích công việc)",
    "Timing diagram": "Sơ đồ thời gian",
    "Deployment diagram": "Sơ đồ triển khai",
    "JSON": "JSON",
    # ── File tree ─────────────────────────────────────────────────────────────
    "Current root directory": "Thư mục gốc hiện tại",
    "Choose Directory": "Chọn thư mục",
    # ── Settings dialog ───────────────────────────────────────────────────────
    "Settings": "Cài đặt",
    "Language:": "Ngôn ngữ:",
    "Restart required to apply language changes.":
        "Cần khởi động lại để áp dụng thay đổi ngôn ngữ.",
    "Editor theme:": "Giao diện trình soạn:",
    "Preview theme:": "Giao diện xem trước:",
    "App theme:": "Giao diện ứng dụng:",
    "App theme requires restart.": "Giao diện ứng dụng cần khởi động lại.",
    # ── Help menu ─────────────────────────────────────────────────────────────
    "&User Manual …": "&Hướng dẫn sử dụng …",
    # ── Git integration ───────────────────────────────────────────────────────
    "Open from &Git …": "Mở từ &Git …",
    "Open File from Git": "Mở tệp từ Git",
    "GitHub / Bitbucket file URL:": "URL tệp GitHub / Bitbucket:",
    "Ref (branch/tag/commit):": "Ref (nhánh/thẻ/commit):",
    "Cloning repository …": "Đang sao chép kho lưu trữ …",
    "Open from Git": "Mở từ Git",
    "Git Push": "Git Push",
    "Pushing to remote …": "Đang đẩy lên máy chủ …",
    "Pushed to remote.": "Đã đẩy lên máy chủ.",
    "Git push failed:\n{exc}": "Git push thất bại:\n{exc}",
    "Clone failed:\n{exc}": "Sao chép thất bại:\n{exc}",
    "File not found in repository:\n{path}": "Không tìm thấy tệp trong kho:\n{path}",
    "Delete Git Temp Directory?": "Xóa thư mục tạm Git?",
    "A temporary Git clone is open:\n{path}\n\nDelete it now?":
        "Đang mở bản sao Git tạm:\n{path}\n\nXóa ngay bây giờ?",
    "Push to": "Đẩy lên",
    "Current branch ({branch})": "Nhánh hiện tại ({branch})",
    "New branch:": "Nhánh mới:",
    "Create Pull Request": "Tạo Pull Request",
    "PR title:": "Tiêu đề PR:",
    "Target branch:": "Nhánh đích:",
    "Git Commit & Push": "Git Commit & Push",
    "Git Authentication": "Xác thực Git",
    "Auth method:": "Phương thức xác thực:",
    "HTTPS (embedded)": "HTTPS (tích hợp)",
    "HTTPS (git binary)": "HTTPS (git nhị phân)",
    "SSH (key file)": "SSH (tệp khóa)",
    "Token:": "Token:",
    "SSH key:": "Khóa SSH:",
    "Passphrase:": "Cụm mật khẩu:",
    "Select SSH Key File": "Chọn tệp khóa SSH",
    "No credentials configured. Public repositories will still work.\n"
    "Configure credentials in View → Settings.":
        "Chưa cấu hình thông tin đăng nhập. Kho công khai vẫn hoạt động.\n"
        "Cấu hình trong Xem → Cài đặt.",
    "Push rejected (non-fast-forward).\nTry saving again using 'New branch'.":
        "Push bị từ chối (non-fast-forward).\nThử lưu lại bằng 'Nhánh mới'.",
    "Commit message:": "Nội dung commit:",
    "Amend previous commit": "Sửa commit trước",
    "Git &Squash …": "Git &Squash …",
    "Git Squash Commits": "Gộp commits Git",
    "Select all new commits": "Chọn tất cả commit mới",
    "SHA": "SHA",
    "Message": "Nội dung",
    "Author": "Tác giả",
    "Date": "Ngày",
    "Squash commit message:": "Nội dung commit gộp:",
    "Enter the combined commit message …": "Nhập nội dung commit kết hợp …",
    "Squash && Push": "Gộp && Đẩy",
    "Select at least 2 commits to squash.": "Chọn ít nhất 2 commit để gộp.",
    "The selected commits must form a contiguous range starting from the most recent commit (HEAD).":
        "Các commit đã chọn phải tạo thành dải liên tiếp từ commit gần nhất (HEAD).",
    "cannot be empty.": "không được để trống.",
    "Squashing commits …": "Đang gộp commits …",
    "Squash complete.": "Gộp hoàn tất.",
    "Git squash failed:\n{exc}": "Git squash thất bại:\n{exc}",
    "Could not read commit history:\n{exc}": "Không thể đọc lịch sử commit:\n{exc}",
    "No new commits found on this branch.": "Không có commit mới trên nhánh này.",
    "No new commits found compared to '{base}'.":
        "Không có commit mới so với '{base}'.",
    "Reload": "Tải lại",
    "Git squash is only available with SSH or git-binary authentication.":
        "Git squash chỉ khả dụng với xác thực SSH hoặc git-binary.",
    "Username:": "Tên người dùng:",
    "Name:": "Tên:",
    "Email:": "Email:",
    # ── Mermaid ───────────────────────────────────────────────────────────────
    "Insert Mermaid Diagram": "Chèn sơ đồ Mermaid",
    "Mermaid code:": "Mã Mermaid:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (mermaid.js is loaded from CDN on first use).":
        "Mẹo: Xem trước sơ đồ tự động xuất hiện trong cửa sổ chính sau khi chèn"
        " (mermaid.js được tải từ CDN lần đầu sử dụng).",
    "&Mermaid …": "&Mermaid …",
    "Mermaid …": "Mermaid …",
    # Mermaid template names
    "Flowchart": "Sơ đồ luồng",
    "Pie chart": "Biểu đồ tròn",
    "ER diagram": "Sơ đồ ER",
    "Git graph": "Đồ thị Git",
    "Gantt": "Gantt",
    # ── Proxy ─────────────────────────────────────────────────────────────────
    "HTTP Proxy": "HTTP Proxy",
    "Proxy URL:": "URL Proxy:",
    "Proxy username:": "Tên người dùng Proxy:",
    "Proxy password:": "Mật khẩu Proxy:",
    "Leave empty to use system proxy settings.":
        "Để trống để dùng cài đặt proxy hệ thống.",
}

# ── Swedish ───────────────────────────────────────────────────────────────────
_SV: dict[str, str] = {
    # ── Menus ─────────────────────────────────────────────────────────────────
    "&File": "&Arkiv",
    "&New": "&Ny",
    "&Open …": "&Öppna …",
    "&Save": "&Spara",
    "Save &As …": "Spara &som …",
    "Export as PDF …": "Exportera som PDF …",
    # ── Splash screen ─────────────────────────────────────────────────────────
    "Loading …": "Laddar …",
    "Initializing interface …": "Startar gränssnittet …",
    "Ready": "Redo",
    # ── PDF import ────────────────────────────────────────────────────────────
    "Importing PDF …": "Importerar PDF …",
    "&Import PDF …": "&Importera PDF …",
    "Import PDF": "Importera PDF",
    "New File": "Ny fil",
    "File name:\nFolder: {path}": "Filnamn:\nMapp: {path}",
    "Open &Folder …": "Öppna &mapp …",
    "Open Folder": "Öppna mapp",
    "Open or create a Markdown file to start editing.":
        "Öppna eller skapa en Markdown-fil för att börja redigera.",
    "pymupdf4llm is not installed.\nInstall it with: pip install pymupdf4llm":
        "pymupdf4llm är inte installerat.\nInstallera med: pip install pymupdf4llm",
    "Could not import PDF:\n{exc}": "Kunde inte importera PDF:\n{exc}",
    "&Quit": "&Avsluta",
    "&Edit": "&Redigera",
    "&Undo": "&Ångra",
    "&Redo": "&Gör om",
    "Cu&t": "K&lipp ut",
    "&Copy": "&Kopiera",
    "&Paste": "&Klistra in",
    "&Insert": "&Infoga",
    "&Link …": "&Länk …",
    "&Image …": "&Bild …",
    "&PlantUML …": "&PlantUML …",
    "&Table …": "&Tabell …",
    "&View": "&Visa",
    "Show file tree": "Visa filträd",
    "Show preview": "Visa förhandsvisning",
    "Word wrap": "Radbrytning",
    "Light preview": "Ljus förhandsvisning",
    "Light editor": "Ljus editor",
    "Settings …": "Inställningar …",
    "&Help": "&Hjälp",
    "&Markdown …": "&Markdown …",
    "&About …": "&Om …",
    # ── Toolbar ───────────────────────────────────────────────────────────────
    "Toolbar": "Verktygsfält",
    # ── Status bar ────────────────────────────────────────────────────────────
    "{n} words": "{n} ord",
    "Line {line}, Col {col}": "Rad {line}, Kol {col}",
    # ── Window title ──────────────────────────────────────────────────────────
    "Untitled": "Namnlös",
    # ── File dialogs ──────────────────────────────────────────────────────────
    "Open File": "Öppna fil",
    "Save As": "Spara som",
    "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*)":
        "Markdown-filer (*.md *.markdown);;Textfiler (*.txt);;Alla filer (*)",
    "Markdown files (*.md);;Text files (*.txt);;All files (*)":
        "Markdown-filer (*.md);;Textfiler (*.txt);;Alla filer (*)",
    # ── Status / messages ─────────────────────────────────────────────────────
    "Export as PDF": "Exportera som PDF",
    "PDF files (*.pdf);;All files (*)": "PDF-filer (*.pdf);;Alla filer (*)",
    "PDF saved: {path}": "PDF sparad: {path}",
    "Could not save PDF:\n{path}": "Kunde inte spara PDF:\n{path}",
    "Saved.": "Sparad.",
    "Unsaved Changes": "Osparade ändringar",
    "Do you want to save the changes?": "Vill du spara ändringarna?",
    "Error": "Fel",
    "Could not open file:\n{exc}": "Kunde inte öppna filen:\n{exc}",
    "Could not save file:\n{exc}": "Kunde inte spara filen:\n{exc}",
    # ── About ─────────────────────────────────────────────────────────────────
    "About MarkForge": "Om MarkForge",
    "<h3>MarkForge 1.0</h3>"
    "<p>Created with <b>Python 3</b> and <b>PyQt6</b>.</p>"
    "<p>Supported extensions:<br>"
    "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
    "<hr>"
    "<p>Copyright &copy; Marcel Mulch</p>"
    "<p>License: GNU General Public License 3.0</p>":
        "<h3>MarkForge 1.0</h3>"
        "<p>Skapad med <b>Python 3</b> och <b>PyQt6</b>.</p>"
        "<p>Stödda tillägg:<br>"
        "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
        "<hr>"
        "<p>Copyright &copy; Marcel Mulch</p>"
        "<p>Licens: GNU General Public License 3.0</p>",
    # ── Table dialog ──────────────────────────────────────────────────────────
    "Insert Table": "Infoga tabell",
    "Table Structure": "Tabellstruktur",
    "Number of data rows (excluding header)": "Antal datarader (exkl. rubrik)",
    "Data rows:": "Datarader:",
    "Number of columns": "Antal kolumner",
    "Columns:": "Kolumner:",
    "Header row with column titles": "Rubrikrad med kolumntitlar",
    "Column Configuration": "Kolumnkonfiguration",
    "Column Name": "Kolumnnamn",
    "Alignment": "Justering",
    "Preview (Markdown)": "Förhandsvisning (Markdown)",
    "Insert": "Infoga",
    "Cancel": "Avbryt",
    "Column {n}": "Kolumn {n}",
    "Left": "Vänster",
    "Center": "Mitten",
    "Right": "Höger",
    # ── Link dialog ───────────────────────────────────────────────────────────
    "Insert Link": "Infoga länk",
    "Link Properties": "Länkegenskaper",
    "e.g.  Click here": "t.ex.  Klicka här",
    "Display text:": "Visningstext:",
    "https://example.com": "https://example.com",
    "URL:": "URL:",
    "Optional tooltip (shown on hover)": "Valfri verktygstips (visas vid hovring)",
    "Title (optional):": "Titel (valfri):",
    # ── Image dialog ──────────────────────────────────────────────────────────
    "Insert Image": "Infoga bild",
    "Image Properties": "Bildegenskaper",
    "Short image description (for screen readers)":
        "Kort bildbeskrivning (för skärmläsare)",
    "Alt Text:": "Alternativtext:",
    "https://example.com/image.png  or  local path":
        "https://example.com/image.png  eller  lokal sökväg",
    "Select local image file": "Välj lokal bildfil",
    "URL / Path:": "URL / Sökväg:",
    "Images (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;All files (*)":
        "Bilder (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;Alla filer (*)",
    "Select Image File": "Välj bildfil",
    # ── PlantUML dialog ───────────────────────────────────────────────────────
    "Insert PlantUML Diagram": "Infoga PlantUML-diagram",
    "Diagram type:": "Diagramtyp:",
    "PlantUML code:": "PlantUML-kod:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (internet connection required).":
        "Tips: Förhandsvisningen visas automatiskt i huvudfönstret efter infogning"
        " (internetanslutning krävs).",
    # PlantUML template names
    "Sequence diagram": "Sekvensdiagram",
    "Class diagram": "Klassdiagram",
    "Activity diagram": "Aktivitetsdiagram",
    "State diagram": "Tillståndsdiagram",
    "Component diagram": "Komponentdiagram",
    "Use case diagram": "Användningsfallsdiagram",
    "Gantt diagram": "Gantt-diagram",
    "Mind map": "Tankekarta",
    "WBS (Work breakdown)": "WBS (Arbetsstruktur)",
    "Timing diagram": "Tidsdiagram",
    "Deployment diagram": "Driftsättningsdiagram",
    "JSON": "JSON",
    # ── File tree ─────────────────────────────────────────────────────────────
    "Current root directory": "Aktuell rotkatalog",
    "Choose Directory": "Välj katalog",
    # ── Settings dialog ───────────────────────────────────────────────────────
    "Settings": "Inställningar",
    "Language:": "Språk:",
    "Restart required to apply language changes.":
        "Omstart krävs för att tillämpa språkändringar.",
    "Editor theme:": "Editortema:",
    "Preview theme:": "Förhandsvisningstema:",
    "App theme:": "Apptema:",
    "App theme requires restart.": "Apptema kräver omstart.",
    # ── Help menu ─────────────────────────────────────────────────────────────
    "&User Manual …": "&Användarmanual …",
    # ── Git integration ───────────────────────────────────────────────────────
    "Open from &Git …": "Öppna från &Git …",
    "Open File from Git": "Öppna fil från Git",
    "GitHub / Bitbucket file URL:": "GitHub / Bitbucket fil-URL:",
    "Ref (branch/tag/commit):": "Ref (gren/tagg/commit):",
    "Cloning repository …": "Klonar arkiv …",
    "Open from Git": "Öppna från Git",
    "Git Push": "Git Push",
    "Pushing to remote …": "Pushar till fjärrserver …",
    "Pushed to remote.": "Pushad till fjärrserver.",
    "Git push failed:\n{exc}": "Git push misslyckades:\n{exc}",
    "Clone failed:\n{exc}": "Kloning misslyckades:\n{exc}",
    "File not found in repository:\n{path}": "Filen hittades inte i arkivet:\n{path}",
    "Delete Git Temp Directory?": "Radera Git-temp-katalog?",
    "A temporary Git clone is open:\n{path}\n\nDelete it now?":
        "En temporär Git-klon är öppen:\n{path}\n\nRadera nu?",
    "Push to": "Pusha till",
    "Current branch ({branch})": "Aktuell gren ({branch})",
    "New branch:": "Ny gren:",
    "Create Pull Request": "Skapa Pull Request",
    "PR title:": "PR-titel:",
    "Target branch:": "Målgren:",
    "Git Commit & Push": "Git Commit & Push",
    "Git Authentication": "Git-autentisering",
    "Auth method:": "Autentiseringsmetod:",
    "HTTPS (embedded)": "HTTPS (inbyggd)",
    "HTTPS (git binary)": "HTTPS (git-program)",
    "SSH (key file)": "SSH (nyckelfil)",
    "Token:": "Token:",
    "SSH key:": "SSH-nyckel:",
    "Passphrase:": "Lösenfras:",
    "Select SSH Key File": "Välj SSH-nyckelfil",
    "No credentials configured. Public repositories will still work.\n"
    "Configure credentials in View → Settings.":
        "Inga autentiseringsuppgifter konfigurerade. Publika arkiv fungerar ändå.\n"
        "Konfigurera i Visa → Inställningar.",
    "Push rejected (non-fast-forward).\nTry saving again using 'New branch'.":
        "Push avvisad (non-fast-forward).\nFörsök spara igen med 'Ny gren'.",
    "Commit message:": "Commit-meddelande:",
    "Amend previous commit": "Ändra föregående commit",
    "Git &Squash …": "Git &Squash …",
    "Git Squash Commits": "Sammanfoga Git-commits",
    "Select all new commits": "Markera alla nya commits",
    "SHA": "SHA",
    "Message": "Meddelande",
    "Author": "Författare",
    "Date": "Datum",
    "Squash commit message:": "Sammanfogat commit-meddelande:",
    "Enter the combined commit message …": "Ange det kombinerade commit-meddelandet …",
    "Squash && Push": "Sammanfoga && Pusha",
    "Select at least 2 commits to squash.": "Välj minst 2 commits att sammanfoga.",
    "The selected commits must form a contiguous range starting from the most recent commit (HEAD).":
        "De valda commits måste bilda ett sammanhängande intervall från senaste commit (HEAD).",
    "cannot be empty.": "får inte vara tomt.",
    "Squashing commits …": "Sammanfogar commits …",
    "Squash complete.": "Sammanfogning klar.",
    "Git squash failed:\n{exc}": "Git squash misslyckades:\n{exc}",
    "Could not read commit history:\n{exc}": "Kunde inte läsa commit-historik:\n{exc}",
    "No new commits found on this branch.": "Inga nya commits hittades på den här grenen.",
    "No new commits found compared to '{base}'.":
        "Inga nya commits jämfört med '{base}'.",
    "Reload": "Ladda om",
    "Git squash is only available with SSH or git-binary authentication.":
        "Git squash är bara tillgängligt med SSH- eller git-binary-autentisering.",
    "Username:": "Användarnamn:",
    "Name:": "Namn:",
    "Email:": "E-post:",
    # ── Mermaid ───────────────────────────────────────────────────────────────
    "Insert Mermaid Diagram": "Infoga Mermaid-diagram",
    "Mermaid code:": "Mermaid-kod:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (mermaid.js is loaded from CDN on first use).":
        "Tips: Förhandsvisningen visas automatiskt i huvudfönstret efter infogning"
        " (mermaid.js laddas från CDN vid första användning).",
    "&Mermaid …": "&Mermaid …",
    "Mermaid …": "Mermaid …",
    # Mermaid template names
    "Flowchart": "Flödesschema",
    "Pie chart": "Cirkeldiagram",
    "ER diagram": "ER-diagram",
    "Git graph": "Git-graf",
    "Gantt": "Gantt",
    # ── Proxy ─────────────────────────────────────────────────────────────────
    "HTTP Proxy": "HTTP-proxy",
    "Proxy URL:": "Proxy-URL:",
    "Proxy username:": "Proxy-användarnamn:",
    "Proxy password:": "Proxy-lösenord:",
    "Leave empty to use system proxy settings.":
        "Lämna tomt för att använda systemets proxyinställningar.",
}

# ── Ukrainian ────────────────────────────────────────────────────────────────
_UK: dict[str, str] = {
    # ── Menus ─────────────────────────────────────────────────────────────────
    "&File": "&Файл",
    "&New": "&Новий",
    "&Open …": "&Відкрити …",
    "&Save": "&Зберегти",
    "Save &As …": "Зберегти &як …",
    "Export as PDF …": "Експортувати як PDF …",
    # ── Splash screen ─────────────────────────────────────────────────────────
    "Loading …": "Завантаження …",
    "Initializing interface …": "Ініціалізація інтерфейсу …",
    "Ready": "Готово",
    # ── PDF import ────────────────────────────────────────────────────────────
    "Importing PDF …": "Імпорт PDF …",
    "&Import PDF …": "&Імпортувати PDF …",
    "Import PDF": "Імпортувати PDF",
    "New File": "Новий файл",
    "File name:\nFolder: {path}": "Ім'я файлу:\nПапка: {path}",
    "Open &Folder …": "Відкрити &папку …",
    "Open Folder": "Відкрити папку",
    "Open or create a Markdown file to start editing.":
        "Відкрийте або створіть файл Markdown, щоб почати редагування.",
    "pymupdf4llm is not installed.\nInstall it with: pip install pymupdf4llm":
        "pymupdf4llm не встановлено.\nВстановіть: pip install pymupdf4llm",
    "Could not import PDF:\n{exc}": "Не вдалося імпортувати PDF:\n{exc}",
    "&Quit": "&Вихід",
    "&Edit": "&Редагування",
    "&Undo": "&Скасувати",
    "&Redo": "&Повторити",
    "Cu&t": "В&ирізати",
    "&Copy": "&Копіювати",
    "&Paste": "&Вставити",
    "&Insert": "&Вставити",
    "&Link …": "&Посилання …",
    "&Image …": "&Зображення …",
    "&PlantUML …": "&PlantUML …",
    "&Table …": "&Таблиця …",
    "&View": "&Вигляд",
    "Show file tree": "Показати дерево файлів",
    "Show preview": "Показати попередній перегляд",
    "Word wrap": "Перенесення рядків",
    "Light preview": "Світлий попередній перегляд",
    "Light editor": "Світлий редактор",
    "Settings …": "Налаштування …",
    "&Help": "&Довідка",
    "&Markdown …": "&Markdown …",
    "&About …": "&Про програму …",
    # ── Toolbar ───────────────────────────────────────────────────────────────
    "Toolbar": "Панель інструментів",
    # ── Status bar ────────────────────────────────────────────────────────────
    "{n} words": "{n} слів",
    "Line {line}, Col {col}": "Рядок {line}, Стовпець {col}",
    # ── Window title ──────────────────────────────────────────────────────────
    "Untitled": "Без назви",
    # ── File dialogs ──────────────────────────────────────────────────────────
    "Open File": "Відкрити файл",
    "Save As": "Зберегти як",
    "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*)":
        "Файли Markdown (*.md *.markdown);;Текстові файли (*.txt);;Усі файли (*)",
    "Markdown files (*.md);;Text files (*.txt);;All files (*)":
        "Файли Markdown (*.md);;Текстові файли (*.txt);;Усі файли (*)",
    # ── Status / messages ─────────────────────────────────────────────────────
    "Export as PDF": "Експортувати як PDF",
    "PDF files (*.pdf);;All files (*)": "Файли PDF (*.pdf);;Усі файли (*)",
    "PDF saved: {path}": "PDF збережено: {path}",
    "Could not save PDF:\n{path}": "Не вдалося зберегти PDF:\n{path}",
    "Saved.": "Збережено.",
    "Unsaved Changes": "Незбережені зміни",
    "Do you want to save the changes?": "Зберегти зміни?",
    "Error": "Помилка",
    "Could not open file:\n{exc}": "Не вдалося відкрити файл:\n{exc}",
    "Could not save file:\n{exc}": "Не вдалося зберегти файл:\n{exc}",
    # ── About ─────────────────────────────────────────────────────────────────
    "About MarkForge": "Про MarkForge",
    "<h3>MarkForge 1.0</h3>"
    "<p>Created with <b>Python 3</b> and <b>PyQt6</b>.</p>"
    "<p>Supported extensions:<br>"
    "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
    "<hr>"
    "<p>Copyright &copy; Marcel Mulch</p>"
    "<p>License: GNU General Public License 3.0</p>":
        "<h3>MarkForge 1.0</h3>"
        "<p>Створено за допомогою <b>Python 3</b> та <b>PyQt6</b>.</p>"
        "<p>Підтримувані розширення:<br>"
        "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
        "<hr>"
        "<p>Авторське право &copy; Marcel Mulch</p>"
        "<p>Ліцензія: GNU General Public License 3.0</p>",
    # ── Table dialog ──────────────────────────────────────────────────────────
    "Insert Table": "Вставити таблицю",
    "Table Structure": "Структура таблиці",
    "Number of data rows (excluding header)": "Кількість рядків даних (без заголовка)",
    "Data rows:": "Рядки даних:",
    "Number of columns": "Кількість стовпців",
    "Columns:": "Стовпці:",
    "Header row with column titles": "Рядок заголовка з назвами стовпців",
    "Column Configuration": "Конфігурація стовпців",
    "Column Name": "Назва стовпця",
    "Alignment": "Вирівнювання",
    "Preview (Markdown)": "Попередній перегляд (Markdown)",
    "Insert": "Вставити",
    "Cancel": "Скасувати",
    "Column {n}": "Стовпець {n}",
    "Left": "Ліворуч",
    "Center": "По центру",
    "Right": "Праворуч",
    # ── Link dialog ───────────────────────────────────────────────────────────
    "Insert Link": "Вставити посилання",
    "Link Properties": "Властивості посилання",
    "e.g.  Click here": "напр.  Натисніть тут",
    "Display text:": "Текст посилання:",
    "https://example.com": "https://example.com",
    "URL:": "URL:",
    "Optional tooltip (shown on hover)": "Підказка (відображається при наведенні)",
    "Title (optional):": "Заголовок (необов'язково):",
    # ── Image dialog ──────────────────────────────────────────────────────────
    "Insert Image": "Вставити зображення",
    "Image Properties": "Властивості зображення",
    "Short image description (for screen readers)":
        "Короткий опис зображення (для читачів екрана)",
    "Alt Text:": "Альтернативний текст:",
    "https://example.com/image.png  or  local path":
        "https://example.com/image.png  або  локальний шлях",
    "Select local image file": "Вибрати локальний файл зображення",
    "URL / Path:": "URL / Шлях:",
    "Images (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;All files (*)":
        "Зображення (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;Усі файли (*)",
    "Select Image File": "Вибрати файл зображення",
    # ── PlantUML dialog ───────────────────────────────────────────────────────
    "Insert PlantUML Diagram": "Вставити діаграму PlantUML",
    "Diagram type:": "Тип діаграми:",
    "PlantUML code:": "Код PlantUML:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (internet connection required).":
        "Порада: попередній перегляд діаграми з'явиться автоматично після вставки"
        " (потрібне підключення до інтернету).",
    # PlantUML template names
    "Sequence diagram": "Діаграма послідовності",
    "Class diagram": "Діаграма класів",
    "Activity diagram": "Діаграма діяльності",
    "State diagram": "Діаграма станів",
    "Component diagram": "Діаграма компонентів",
    "Use case diagram": "Діаграма варіантів використання",
    "Gantt diagram": "Діаграма Ганта",
    "Mind map": "Карта думок",
    "WBS (Work breakdown)": "WBS (Декомпозиція робіт)",
    "Timing diagram": "Часова діаграма",
    "Deployment diagram": "Діаграма розгортання",
    "JSON": "JSON",
    # ── File tree ─────────────────────────────────────────────────────────────
    "Current root directory": "Поточний кореневий каталог",
    "Choose Directory": "Вибрати каталог",
    # ── Settings dialog ───────────────────────────────────────────────────────
    "Settings": "Налаштування",
    "Language:": "Мова:",
    "Restart required to apply language changes.":
        "Для застосування змін мови потрібен перезапуск.",
    "Editor theme:": "Тема редактора:",
    "Preview theme:": "Тема попереднього перегляду:",
    "App theme:": "Тема програми:",
    "App theme requires restart.": "Тема програми потребує перезапуску.",
    # ── Help menu ─────────────────────────────────────────────────────────────
    "&User Manual …": "&Посібник користувача …",
    # ── Git integration ───────────────────────────────────────────────────────
    "Open from &Git …": "Відкрити з &Git …",
    "Open File from Git": "Відкрити файл з Git",
    "GitHub / Bitbucket file URL:": "URL файлу GitHub / Bitbucket:",
    "Ref (branch/tag/commit):": "Ref (гілка/тег/commit):",
    "Cloning repository …": "Клонування репозиторію …",
    "Open from Git": "Відкрити з Git",
    "Git Push": "Git Push",
    "Pushing to remote …": "Надсилання на сервер …",
    "Pushed to remote.": "Надіслано на сервер.",
    "Git push failed:\n{exc}": "Git push не вдався:\n{exc}",
    "Clone failed:\n{exc}": "Клонування не вдалося:\n{exc}",
    "File not found in repository:\n{path}": "Файл не знайдено в репозиторії:\n{path}",
    "Delete Git Temp Directory?": "Видалити тимчасову директорію Git?",
    "A temporary Git clone is open:\n{path}\n\nDelete it now?":
        "Відкрито тимчасовий клон Git:\n{path}\n\nВидалити зараз?",
    "Push to": "Надіслати до",
    "Current branch ({branch})": "Поточна гілка ({branch})",
    "New branch:": "Нова гілка:",
    "Create Pull Request": "Створити Pull Request",
    "PR title:": "Заголовок PR:",
    "Target branch:": "Цільова гілка:",
    "Git Commit & Push": "Git Commit & Push",
    "Git Authentication": "Автентифікація Git",
    "Auth method:": "Метод автентифікації:",
    "HTTPS (embedded)": "HTTPS (вбудований)",
    "HTTPS (git binary)": "HTTPS (git-програма)",
    "SSH (key file)": "SSH (файл ключа)",
    "Token:": "Токен:",
    "SSH key:": "SSH-ключ:",
    "Passphrase:": "Парольна фраза:",
    "Select SSH Key File": "Вибрати файл SSH-ключа",
    "No credentials configured. Public repositories will still work.\n"
    "Configure credentials in View → Settings.":
        "Облікові дані не налаштовані. Публічні репозиторії працюватимуть.\n"
        "Налаштуйте в Вигляд → Налаштування.",
    "Push rejected (non-fast-forward).\nTry saving again using 'New branch'.":
        "Push відхилено (non-fast-forward).\nСпробуйте зберегти з 'Нова гілка'.",
    "Commit message:": "Повідомлення commit:",
    "Amend previous commit": "Змінити попередній commit",
    "Git &Squash …": "Git &Squash …",
    "Git Squash Commits": "Об'єднати commits Git",
    "Select all new commits": "Вибрати всі нові commits",
    "SHA": "SHA",
    "Message": "Повідомлення",
    "Author": "Автор",
    "Date": "Дата",
    "Squash commit message:": "Повідомлення об'єднаного commit:",
    "Enter the combined commit message …": "Введіть об'єднане повідомлення commit …",
    "Squash && Push": "Об'єднати && Надіслати",
    "Select at least 2 commits to squash.": "Виберіть щонайменше 2 commits для об'єднання.",
    "The selected commits must form a contiguous range starting from the most recent commit (HEAD).":
        "Вибрані commits мають утворювати неперервний діапазон від найновішого commit (HEAD).",
    "cannot be empty.": "не може бути порожнім.",
    "Squashing commits …": "Об'єднання commits …",
    "Squash complete.": "Об'єднання завершено.",
    "Git squash failed:\n{exc}": "Git squash не вдався:\n{exc}",
    "Could not read commit history:\n{exc}": "Не вдалося прочитати історію commit:\n{exc}",
    "No new commits found on this branch.": "Нових commits на цій гілці не знайдено.",
    "No new commits found compared to '{base}'.":
        "Нових commits порівняно з '{base}' не знайдено.",
    "Reload": "Оновити",
    "Git squash is only available with SSH or git-binary authentication.":
        "Git squash доступний лише з SSH- або git-binary-автентифікацією.",
    "Username:": "Ім'я користувача:",
    "Name:": "Ім'я:",
    "Email:": "Електронна пошта:",
    # ── Mermaid ───────────────────────────────────────────────────────────────
    "Insert Mermaid Diagram": "Вставити діаграму Mermaid",
    "Mermaid code:": "Код Mermaid:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (mermaid.js is loaded from CDN on first use).":
        "Порада: попередній перегляд з'явиться автоматично після вставки"
        " (mermaid.js завантажується з CDN при першому використанні).",
    "&Mermaid …": "&Mermaid …",
    "Mermaid …": "Mermaid …",
    # Mermaid template names
    "Flowchart": "Блок-схема",
    "Pie chart": "Кругова діаграма",
    "ER diagram": "ER-діаграма",
    "Git graph": "Граф Git",
    "Gantt": "Ганта",
    # ── Proxy ─────────────────────────────────────────────────────────────────
    "HTTP Proxy": "HTTP-проксі",
    "Proxy URL:": "URL проксі:",
    "Proxy username:": "Ім'я користувача проксі:",
    "Proxy password:": "Пароль проксі:",
    "Leave empty to use system proxy settings.":
        "Залиште порожнім для використання системних налаштувань проксі.",
}

# ── Kannada ───────────────────────────────────────────────────────────────────
_KN: dict[str, str] = {
    # ── Menus ─────────────────────────────────────────────────────────────────
    "&File": "&ಫೈಲ್",
    "&New": "&ಹೊಸದು",
    "&Open …": "&ತೆರೆ …",
    "&Save": "&ಉಳಿಸು",
    "Save &As …": "&ಹೆಸರಿನಲ್ಲಿ ಉಳಿಸು …",
    "Export as PDF …": "PDF ಆಗಿ ರಫ್ತು ಮಾಡಿ …",
    # ── Splash screen ─────────────────────────────────────────────────────────
    "Loading …": "ಲೋಡ್ ಆಗುತ್ತಿದೆ …",
    "Initializing interface …": "ಇಂಟರ್‌ಫೇಸ್ ಪ್ರಾರಂಭಿಸಲಾಗುತ್ತಿದೆ …",
    "Ready": "ಸಿದ್ಧ",
    # ── PDF import ────────────────────────────────────────────────────────────
    "Importing PDF …": "PDF ಆಮದು ಮಾಡಲಾಗುತ್ತಿದೆ …",
    "&Import PDF …": "&PDF ಆಮದು ಮಾಡಿ …",
    "Import PDF": "PDF ಆಮದು ಮಾಡಿ",
    "New File": "ಹೊಸ ಫೈಲ್",
    "File name:\nFolder: {path}": "ಫೈಲ್ ಹೆಸರು:\nಫೋಲ್ಡರ್: {path}",
    "Open &Folder …": "&ಫೋಲ್ಡರ್ ತೆರೆ …",
    "Open Folder": "ಫೋಲ್ಡರ್ ತೆರೆ",
    "Open or create a Markdown file to start editing.":
        "ಸಂಪಾದನೆ ಪ್ರಾರಂಭಿಸಲು Markdown ಫೈಲ್ ತೆರೆಯಿರಿ ಅಥವಾ ರಚಿಸಿರಿ.",
    "pymupdf4llm is not installed.\nInstall it with: pip install pymupdf4llm":
        "pymupdf4llm ಸ್ಥಾಪಿಸಲಾಗಿಲ್ಲ.\nಸ್ಥಾಪಿಸಿ: pip install pymupdf4llm",
    "Could not import PDF:\n{exc}": "PDF ಆಮದು ಮಾಡಲಾಗಲಿಲ್ಲ:\n{exc}",
    "&Quit": "&ನಿರ್ಗಮಿಸು",
    "&Edit": "&ಸಂಪಾದಿಸು",
    "&Undo": "&ರದ್ದು",
    "&Redo": "&ಮರಳಿ ಮಾಡು",
    "Cu&t": "&ಕತ್ತರಿಸು",
    "&Copy": "&ನಕಲಿಸು",
    "&Paste": "&ಅಂಟಿಸು",
    "&Insert": "&ಸೇರಿಸು",
    "&Link …": "&ಲಿಂಕ್ …",
    "&Image …": "&ಚಿತ್ರ …",
    "&PlantUML …": "&PlantUML …",
    "&Table …": "&ಕೋಷ್ಟಕ …",
    "&View": "&ನೋಟ",
    "Show file tree": "ಫೈಲ್ ಮರ ತೋರಿಸಿ",
    "Show preview": "ಮುನ್ನೋಟ ತೋರಿಸಿ",
    "Word wrap": "ಪದ ಮಡಿಕೆ",
    "Light preview": "ತಿಳಿ ಮುನ್ನೋಟ",
    "Light editor": "ತಿಳಿ ಸಂಪಾದಕ",
    "Settings …": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು …",
    "&Help": "&ಸಹಾಯ",
    "&Markdown …": "&Markdown …",
    "&About …": "&ಕುರಿತು …",
    # ── Toolbar ───────────────────────────────────────────────────────────────
    "Toolbar": "ಉಪಕರಣಪಟ್ಟಿ",
    # ── Status bar ────────────────────────────────────────────────────────────
    "{n} words": "{n} ಪದಗಳು",
    "Line {line}, Col {col}": "ಸಾಲು {line}, ಕಾಲಮ್ {col}",
    # ── Window title ──────────────────────────────────────────────────────────
    "Untitled": "ಶೀರ್ಷಿಕೆಯಿಲ್ಲ",
    # ── File dialogs ──────────────────────────────────────────────────────────
    "Open File": "ಫೈಲ್ ತೆರೆ",
    "Save As": "ಹೆಸರಿನಲ್ಲಿ ಉಳಿಸು",
    "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*)":
        "Markdown ಫೈಲ್‌ಗಳು (*.md *.markdown);;ಪಠ್ಯ ಫೈಲ್‌ಗಳು (*.txt);;ಎಲ್ಲಾ ಫೈಲ್‌ಗಳು (*)",
    "Markdown files (*.md);;Text files (*.txt);;All files (*)":
        "Markdown ಫೈಲ್‌ಗಳು (*.md);;ಪಠ್ಯ ಫೈಲ್‌ಗಳು (*.txt);;ಎಲ್ಲಾ ಫೈಲ್‌ಗಳು (*)",
    # ── Status / messages ─────────────────────────────────────────────────────
    "Export as PDF": "PDF ಆಗಿ ರಫ್ತು ಮಾಡಿ",
    "PDF files (*.pdf);;All files (*)": "PDF ಫೈಲ್‌ಗಳು (*.pdf);;ಎಲ್ಲಾ ಫೈಲ್‌ಗಳು (*)",
    "PDF saved: {path}": "PDF ಉಳಿಸಲಾಗಿದೆ: {path}",
    "Could not save PDF:\n{path}": "PDF ಉಳಿಸಲಾಗಲಿಲ್ಲ:\n{path}",
    "Saved.": "ಉಳಿಸಲಾಗಿದೆ.",
    "Unsaved Changes": "ಉಳಿಸದ ಬದಲಾವಣೆಗಳು",
    "Do you want to save the changes?": "ಬದಲಾವಣೆಗಳನ್ನು ಉಳಿಸಬೇಕೇ?",
    "Error": "ದೋಷ",
    "Could not open file:\n{exc}": "ಫೈಲ್ ತೆರೆಯಲಾಗಲಿಲ್ಲ:\n{exc}",
    "Could not save file:\n{exc}": "ಫೈಲ್ ಉಳಿಸಲಾಗಲಿಲ್ಲ:\n{exc}",
    # ── About ─────────────────────────────────────────────────────────────────
    "About MarkForge": "MarkForge ಕುರಿತು",
    "<h3>MarkForge 1.0</h3>"
    "<p>Created with <b>Python 3</b> and <b>PyQt6</b>.</p>"
    "<p>Supported extensions:<br>"
    "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
    "<hr>"
    "<p>Copyright &copy; Marcel Mulch</p>"
    "<p>License: GNU General Public License 3.0</p>":
        "<h3>MarkForge 1.0</h3>"
        "<p><b>Python 3</b> ಮತ್ತು <b>PyQt6</b> ಜೊತೆ ರಚಿಸಲಾಗಿದೆ.</p>"
        "<p>ಬೆಂಬಲಿತ ವಿಸ್ತರಣೆಗಳು:<br>"
        "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
        "<hr>"
        "<p>ಹಕ್ಕುಸ್ವಾಮ್ಯ &copy; Marcel Mulch</p>"
        "<p>ಪರವಾನಗಿ: GNU General Public License 3.0</p>",
    # ── Table dialog ──────────────────────────────────────────────────────────
    "Insert Table": "ಕೋಷ್ಟಕ ಸೇರಿಸಿ",
    "Table Structure": "ಕೋಷ್ಟಕ ರಚನೆ",
    "Number of data rows (excluding header)": "ಡೇಟಾ ಸಾಲುಗಳ ಸಂಖ್ಯೆ (ಶೀರ್ಷಿಕೆ ಹೊರತುಪಡಿಸಿ)",
    "Data rows:": "ಡೇಟಾ ಸಾಲುಗಳು:",
    "Number of columns": "ಕಾಲಮ್‌ಗಳ ಸಂಖ್ಯೆ",
    "Columns:": "ಕಾಲಮ್‌ಗಳು:",
    "Header row with column titles": "ಕಾಲಮ್ ಶೀರ್ಷಿಕೆಗಳ ಶಿರ್ಷಿಕೆ ಸಾಲು",
    "Column Configuration": "ಕಾಲಮ್ ಸಂರಚನೆ",
    "Column Name": "ಕಾಲಮ್ ಹೆಸರು",
    "Alignment": "ಜೋಡಣೆ",
    "Preview (Markdown)": "ಮುನ್ನೋಟ (Markdown)",
    "Insert": "ಸೇರಿಸಿ",
    "Cancel": "ರದ್ದುಮಾಡಿ",
    "Column {n}": "ಕಾಲಮ್ {n}",
    "Left": "ಎಡ",
    "Center": "ಮಧ್ಯ",
    "Right": "ಬಲ",
    # ── Link dialog ───────────────────────────────────────────────────────────
    "Insert Link": "ಲಿಂಕ್ ಸೇರಿಸಿ",
    "Link Properties": "ಲಿಂಕ್ ಗುಣಲಕ್ಷಣಗಳು",
    "e.g.  Click here": "ಉದಾ:  ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ",
    "Display text:": "ಪ್ರದರ್ಶನ ಪಠ್ಯ:",
    "https://example.com": "https://example.com",
    "URL:": "URL:",
    "Optional tooltip (shown on hover)": "ಐಚ್ಛಿಕ ಟೂಲ್‌ಟಿಪ್ (ಹೋವರ್‌ನಲ್ಲಿ ತೋರಿಸಲಾಗುತ್ತದೆ)",
    "Title (optional):": "ಶೀರ್ಷಿಕೆ (ಐಚ್ಛಿಕ):",
    # ── Image dialog ──────────────────────────────────────────────────────────
    "Insert Image": "ಚಿತ್ರ ಸೇರಿಸಿ",
    "Image Properties": "ಚಿತ್ರ ಗುಣಲಕ್ಷಣಗಳು",
    "Short image description (for screen readers)":
        "ಚಿತ್ರದ ಸಂಕ್ಷಿಪ್ತ ವಿವರಣೆ (ಸ್ಕ್ರೀನ್ ರೀಡರ್‌ಗಳಿಗಾಗಿ)",
    "Alt Text:": "ಪರ್ಯಾಯ ಪಠ್ಯ:",
    "https://example.com/image.png  or  local path":
        "https://example.com/image.png  ಅಥವಾ  ಸ್ಥಳೀಯ ಮಾರ್ಗ",
    "Select local image file": "ಸ್ಥಳೀಯ ಚಿತ್ರ ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ",
    "URL / Path:": "URL / ಮಾರ್ಗ:",
    "Images (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;All files (*)":
        "ಚಿತ್ರಗಳು (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;ಎಲ್ಲಾ ಫೈಲ್‌ಗಳು (*)",
    "Select Image File": "ಚಿತ್ರ ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ",
    # ── PlantUML dialog ───────────────────────────────────────────────────────
    "Insert PlantUML Diagram": "PlantUML ರೇಖಾಚಿತ್ರ ಸೇರಿಸಿ",
    "Diagram type:": "ರೇಖಾಚಿತ್ರ ಪ್ರಕಾರ:",
    "PlantUML code:": "PlantUML ಕೋಡ್:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (internet connection required).":
        "ಸಲಹೆ: ಸೇರಿಸಿದ ನಂತರ ರೇಖಾಚಿತ್ರ ಮುನ್ನೋಟ ತಾನಾಗಿ ಮುಖ್ಯ ವಿಂಡೋದಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ"
        " (ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕ ಅಗತ್ಯ).",
    # PlantUML template names
    "Sequence diagram": "ಅನುಕ್ರಮ ರೇಖಾಚಿತ್ರ",
    "Class diagram": "ವರ್ಗ ರೇಖಾಚಿತ್ರ",
    "Activity diagram": "ಚಟುವಟಿಕೆ ರೇಖಾಚಿತ್ರ",
    "State diagram": "ಸ್ಥಿತಿ ರೇಖಾಚಿತ್ರ",
    "Component diagram": "ಘಟಕ ರೇಖಾಚಿತ್ರ",
    "Use case diagram": "ಬಳಕೆ ಪ್ರಕರಣ ರೇಖಾಚಿತ್ರ",
    "Gantt diagram": "ಗ್ಯಾಂಟ್ ರೇಖಾಚಿತ್ರ",
    "Mind map": "ಮನಸ್ಸಿನ ನಕ್ಷೆ",
    "WBS (Work breakdown)": "WBS (ಕಾರ್ಯ ವಿಭಜನೆ)",
    "Timing diagram": "ಸಮಯ ರೇಖಾಚಿತ್ರ",
    "Deployment diagram": "ನಿಯೋಜನೆ ರೇಖಾಚಿತ್ರ",
    "JSON": "JSON",
    # ── File tree ─────────────────────────────────────────────────────────────
    "Current root directory": "ಪ್ರಸ್ತುತ ಮೂಲ ಡೈರೆಕ್ಟರಿ",
    "Choose Directory": "ಡೈರೆಕ್ಟರಿ ಆಯ್ಕೆ ಮಾಡಿ",
    # ── Settings dialog ───────────────────────────────────────────────────────
    "Settings": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
    "Language:": "ಭಾಷೆ:",
    "Restart required to apply language changes.":
        "ಭಾಷಾ ಬದಲಾವಣೆಗಳನ್ನು ಅನ್ವಯಿಸಲು ಮರುಪ್ರಾರಂಭ ಅಗತ್ಯ.",
    "Editor theme:": "ಸಂಪಾದಕ ಥೀಮ್:",
    "Preview theme:": "ಮುನ್ನೋಟ ಥೀಮ್:",
    "App theme:": "ಅಪ್ಲಿಕೇಶನ್ ಥೀಮ್:",
    "App theme requires restart.": "ಅಪ್ಲಿಕೇಶನ್ ಥೀಮ್‌ಗೆ ಮರುಪ್ರಾರಂಭ ಅಗತ್ಯ.",
    # ── Help menu ─────────────────────────────────────────────────────────────
    "&User Manual …": "&ಬಳಕೆದಾರ ಕೈಪಿಡಿ …",
    # ── Git integration ───────────────────────────────────────────────────────
    "Open from &Git …": "&Git ನಿಂದ ತೆರೆ …",
    "Open File from Git": "Git ನಿಂದ ಫೈಲ್ ತೆರೆ",
    "GitHub / Bitbucket file URL:": "GitHub / Bitbucket ಫೈಲ್ URL:",
    "Ref (branch/tag/commit):": "Ref (ಶಾಖೆ/ಟ್ಯಾಗ್/commit):",
    "Cloning repository …": "ರೆಪೊಸಿಟರಿ ಕ್ಲೋನ್ ಮಾಡಲಾಗುತ್ತಿದೆ …",
    "Open from Git": "Git ನಿಂದ ತೆರೆ",
    "Git Push": "Git Push",
    "Pushing to remote …": "ರಿಮೋಟ್‌ಗೆ ತಳ್ಳಲಾಗುತ್ತಿದೆ …",
    "Pushed to remote.": "ರಿಮೋಟ್‌ಗೆ ತಳ್ಳಲಾಗಿದೆ.",
    "Git push failed:\n{exc}": "Git push ವಿಫಲವಾಗಿದೆ:\n{exc}",
    "Clone failed:\n{exc}": "ಕ್ಲೋನ್ ವಿಫಲವಾಗಿದೆ:\n{exc}",
    "File not found in repository:\n{path}": "ರೆಪೊಸಿಟರಿಯಲ್ಲಿ ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ:\n{path}",
    "Delete Git Temp Directory?": "Git ತಾತ್ಕಾಲಿಕ ಡೈರೆಕ್ಟರಿ ಅಳಿಸಬೇಕೇ?",
    "A temporary Git clone is open:\n{path}\n\nDelete it now?":
        "ತಾತ್ಕಾಲಿಕ Git ಕ್ಲೋನ್ ತೆರೆಯಲಾಗಿದೆ:\n{path}\n\nಈಗ ಅಳಿಸಬೇಕೇ?",
    "Push to": "ತಳ್ಳಿ",
    "Current branch ({branch})": "ಪ್ರಸ್ತುತ ಶಾಖೆ ({branch})",
    "New branch:": "ಹೊಸ ಶಾಖೆ:",
    "Create Pull Request": "Pull Request ರಚಿಸಿ",
    "PR title:": "PR ಶೀರ್ಷಿಕೆ:",
    "Target branch:": "ಗುರಿ ಶಾಖೆ:",
    "Git Commit & Push": "Git Commit & Push",
    "Git Authentication": "Git ದೃಢೀಕರಣ",
    "Auth method:": "ದೃಢೀಕರಣ ವಿಧಾನ:",
    "HTTPS (embedded)": "HTTPS (ಅಂತರ್ಗತ)",
    "HTTPS (git binary)": "HTTPS (git ಬೈನರಿ)",
    "SSH (key file)": "SSH (ಕೀ ಫೈಲ್)",
    "Token:": "ಟೋಕನ್:",
    "SSH key:": "SSH ಕೀ:",
    "Passphrase:": "ಪಾಸ್‌ಫ್ರೇಸ್:",
    "Select SSH Key File": "SSH ಕೀ ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ",
    "No credentials configured. Public repositories will still work.\n"
    "Configure credentials in View → Settings.":
        "ಯಾವುದೇ ರುಜುವಾತುಗಳು ಸಂರಚಿಸಲಾಗಿಲ್ಲ. ಸಾರ್ವಜನಿಕ ರೆಪೊಸಿಟರಿಗಳು ಕಾರ್ಯ ನಿರ್ವಹಿಸುತ್ತವೆ.\n"
        "ನೋಟ → ಸೆಟ್ಟಿಂಗ್‌ಗಳಲ್ಲಿ ಸಂರಚಿಸಿ.",
    "Push rejected (non-fast-forward).\nTry saving again using 'New branch'.":
        "Push ತಿರಸ್ಕರಿಸಲಾಗಿದೆ (non-fast-forward).\n'ಹೊಸ ಶಾಖೆ' ಬಳಸಿ ಮತ್ತೆ ಉಳಿಸಿ.",
    "Commit message:": "Commit ಸಂದೇಶ:",
    "Amend previous commit": "ಹಿಂದಿನ commit ತಿದ್ದು",
    "Git &Squash …": "Git &Squash …",
    "Git Squash Commits": "Git commits ಒಗ್ಗೂಡಿಸಿ",
    "Select all new commits": "ಎಲ್ಲಾ ಹೊಸ commits ಆಯ್ಕೆ ಮಾಡಿ",
    "SHA": "SHA",
    "Message": "ಸಂದೇಶ",
    "Author": "ಲೇಖಕ",
    "Date": "ದಿನಾಂಕ",
    "Squash commit message:": "Squash commit ಸಂದೇಶ:",
    "Enter the combined commit message …": "ಸಂಯೋಜಿತ commit ಸಂದೇಶ ನಮೂದಿಸಿ …",
    "Squash && Push": "ಒಗ್ಗೂಡಿಸಿ && ತಳ್ಳಿ",
    "Select at least 2 commits to squash.": "ಒಗ್ಗೂಡಿಸಲು ಕನಿಷ್ಠ 2 commits ಆಯ್ಕೆ ಮಾಡಿ.",
    "The selected commits must form a contiguous range starting from the most recent commit (HEAD).":
        "ಆಯ್ಕೆ ಮಾಡಿದ commits ಇತ್ತೀಚಿನ commit (HEAD) ನಿಂದ ನಿರಂತರ ಶ್ರೇಣಿಯನ್ನು ರೂಪಿಸಬೇಕು.",
    "cannot be empty.": "ಖಾಲಿ ಇರಬಾರದು.",
    "Squashing commits …": "Commits ಒಗ್ಗೂಡಿಸಲಾಗುತ್ತಿದೆ …",
    "Squash complete.": "ಒಗ್ಗೂಡಿಸುವಿಕೆ ಪೂರ್ಣಗೊಂಡಿದೆ.",
    "Git squash failed:\n{exc}": "Git squash ವಿಫಲವಾಗಿದೆ:\n{exc}",
    "Could not read commit history:\n{exc}": "Commit ಇತಿಹಾಸ ಓದಲಾಗಲಿಲ್ಲ:\n{exc}",
    "No new commits found on this branch.": "ಈ ಶಾಖೆಯಲ್ಲಿ ಹೊಸ commits ಕಂಡುಬಂದಿಲ್ಲ.",
    "No new commits found compared to '{base}'.":
        "'{base}' ಗೆ ಹೋಲಿಸಿದರೆ ಹೊಸ commits ಕಂಡುಬಂದಿಲ್ಲ.",
    "Reload": "ಮರುಲೋಡ್",
    "Git squash is only available with SSH or git-binary authentication.":
        "Git squash ಕೇವಲ SSH ಅಥವಾ git-binary ದೃಢೀಕರಣದೊಂದಿಗೆ ಲಭ್ಯ.",
    "Username:": "ಬಳಕೆದಾರ ಹೆಸರು:",
    "Name:": "ಹೆಸರು:",
    "Email:": "ಇಮೇಲ್:",
    # ── Mermaid ───────────────────────────────────────────────────────────────
    "Insert Mermaid Diagram": "Mermaid ರೇಖಾಚಿತ್ರ ಸೇರಿಸಿ",
    "Mermaid code:": "Mermaid ಕೋಡ್:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (mermaid.js is loaded from CDN on first use).":
        "ಸಲಹೆ: ಸೇರಿಸಿದ ನಂತರ ರೇಖಾಚಿತ್ರ ಮುನ್ನೋಟ ತಾನಾಗಿ ಮುಖ್ಯ ವಿಂಡೋದಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ"
        " (ಮೊದಲ ಬಳಕೆಯಲ್ಲಿ CDN ನಿಂದ mermaid.js ಲೋಡ್ ಆಗುತ್ತದೆ).",
    "&Mermaid …": "&Mermaid …",
    "Mermaid …": "Mermaid …",
    # Mermaid template names
    "Flowchart": "ಹರಿವು ಚಾರ್ಟ್",
    "Pie chart": "ಪೈ ಚಾರ್ಟ್",
    "ER diagram": "ER ರೇಖಾಚಿತ್ರ",
    "Git graph": "Git ಗ್ರಾಫ್",
    "Gantt": "ಗ್ಯಾಂಟ್",
    # ── Proxy ─────────────────────────────────────────────────────────────────
    "HTTP Proxy": "HTTP ಪ್ರಾಕ್ಸಿ",
    "Proxy URL:": "ಪ್ರಾಕ್ಸಿ URL:",
    "Proxy username:": "ಪ್ರಾಕ್ಸಿ ಬಳಕೆದಾರ ಹೆಸರು:",
    "Proxy password:": "ಪ್ರಾಕ್ಸಿ ಪಾಸ್‌ವರ್ಡ್:",
    "Leave empty to use system proxy settings.":
        "ಸಿಸ್ಟಂ ಪ್ರಾಕ್ಸಿ ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ಬಳಸಲು ಖಾಲಿ ಬಿಡಿ.",
}

# ── Hindi ────────────────────────────────────────────────────────────────────
_HI: dict[str, str] = {
    # ── Menus ─────────────────────────────────────────────────────────────────
    "&File": "&फ़ाइल",
    "&New": "&नया",
    "&Open …": "&खोलें …",
    "&Save": "&सहेजें",
    "Save &As …": "&इस रूप में सहेजें …",
    "Export as PDF …": "PDF के रूप में निर्यात करें …",
    # ── Splash screen ─────────────────────────────────────────────────────────
    "Loading …": "लोड हो रहा है …",
    "Initializing interface …": "इंटरफ़ेस आरंभ हो रहा है …",
    "Ready": "तैयार",
    # ── PDF import ────────────────────────────────────────────────────────────
    "Importing PDF …": "PDF आयात हो रहा है …",
    "&Import PDF …": "&PDF आयात करें …",
    "Import PDF": "PDF आयात करें",
    "New File": "नई फ़ाइल",
    "File name:\nFolder: {path}": "फ़ाइल का नाम:\nफ़ोल्डर: {path}",
    "Open &Folder …": "&फ़ोल्डर खोलें …",
    "Open Folder": "फ़ोल्डर खोलें",
    "Open or create a Markdown file to start editing.":
        "संपादन शुरू करने के लिए Markdown फ़ाइल खोलें या बनाएँ।",
    "pymupdf4llm is not installed.\nInstall it with: pip install pymupdf4llm":
        "pymupdf4llm इंस्टॉल नहीं है।\nइंस्टॉल करें: pip install pymupdf4llm",
    "Could not import PDF:\n{exc}": "PDF आयात नहीं किया जा सका:\n{exc}",
    "&Quit": "&बाहर निकलें",
    "&Edit": "&संपादन",
    "&Undo": "&पूर्ववत करें",
    "&Redo": "&फिर से करें",
    "Cu&t": "&काटें",
    "&Copy": "&कॉपी करें",
    "&Paste": "&पेस्ट करें",
    "&Insert": "&सम्मिलित करें",
    "&Link …": "&लिंक …",
    "&Image …": "&चित्र …",
    "&PlantUML …": "&PlantUML …",
    "&Table …": "&तालिका …",
    "&View": "&दृश्य",
    "Show file tree": "फ़ाइल ट्री दिखाएँ",
    "Show preview": "पूर्वावलोकन दिखाएँ",
    "Word wrap": "शब्द लपेट",
    "Light preview": "हल्का पूर्वावलोकन",
    "Light editor": "हल्का संपादक",
    "Settings …": "सेटिंग्स …",
    "&Help": "&सहायता",
    "&Markdown …": "&Markdown …",
    "&About …": "&के बारे में …",
    # ── Toolbar ───────────────────────────────────────────────────────────────
    "Toolbar": "टूलबार",
    # ── Status bar ────────────────────────────────────────────────────────────
    "{n} words": "{n} शब्द",
    "Line {line}, Col {col}": "पंक्ति {line}, स्तंभ {col}",
    # ── Window title ──────────────────────────────────────────────────────────
    "Untitled": "शीर्षकहीन",
    # ── File dialogs ──────────────────────────────────────────────────────────
    "Open File": "फ़ाइल खोलें",
    "Save As": "इस रूप में सहेजें",
    "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*)":
        "Markdown फ़ाइलें (*.md *.markdown);;पाठ फ़ाइलें (*.txt);;सभी फ़ाइलें (*)",
    "Markdown files (*.md);;Text files (*.txt);;All files (*)":
        "Markdown फ़ाइलें (*.md);;पाठ फ़ाइलें (*.txt);;सभी फ़ाइलें (*)",
    # ── Status / messages ─────────────────────────────────────────────────────
    "Export as PDF": "PDF के रूप में निर्यात करें",
    "PDF files (*.pdf);;All files (*)": "PDF फ़ाइलें (*.pdf);;सभी फ़ाइलें (*)",
    "PDF saved: {path}": "PDF सहेजी गई: {path}",
    "Could not save PDF:\n{path}": "PDF सहेजी नहीं जा सकी:\n{path}",
    "Saved.": "सहेजा गया।",
    "Unsaved Changes": "असहेजे परिवर्तन",
    "Do you want to save the changes?": "क्या आप परिवर्तन सहेजना चाहते हैं?",
    "Error": "त्रुटि",
    "Could not open file:\n{exc}": "फ़ाइल खोली नहीं जा सकी:\n{exc}",
    "Could not save file:\n{exc}": "फ़ाइल सहेजी नहीं जा सकी:\n{exc}",
    # ── About ─────────────────────────────────────────────────────────────────
    "About MarkForge": "MarkForge के बारे में",
    "<h3>MarkForge 1.0</h3>"
    "<p>Created with <b>Python 3</b> and <b>PyQt6</b>.</p>"
    "<p>Supported extensions:<br>"
    "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
    "<hr>"
    "<p>Copyright &copy; Marcel Mulch</p>"
    "<p>License: GNU General Public License 3.0</p>":
        "<h3>MarkForge 1.0</h3>"
        "<p><b>Python 3</b> और <b>PyQt6</b> से बनाया गया।</p>"
        "<p>समर्थित विस्तार:<br>"
        "Tables · Fenced Code Blocks · Footnotes · Abbreviations · ToC</p>"
        "<hr>"
        "<p>कॉपीराइट &copy; Marcel Mulch</p>"
        "<p>लाइसेंस: GNU General Public License 3.0</p>",
    # ── Table dialog ──────────────────────────────────────────────────────────
    "Insert Table": "तालिका सम्मिलित करें",
    "Table Structure": "तालिका संरचना",
    "Number of data rows (excluding header)": "डेटा पंक्तियों की संख्या (शीर्षलेख के बिना)",
    "Data rows:": "डेटा पंक्तियाँ:",
    "Number of columns": "स्तंभों की संख्या",
    "Columns:": "स्तंभ:",
    "Header row with column titles": "स्तंभ शीर्षकों के साथ शीर्षलेख पंक्ति",
    "Column Configuration": "स्तंभ कॉन्फ़िगरेशन",
    "Column Name": "स्तंभ का नाम",
    "Alignment": "संरेखण",
    "Preview (Markdown)": "पूर्वावलोकन (Markdown)",
    "Insert": "सम्मिलित करें",
    "Cancel": "रद्द करें",
    "Column {n}": "स्तंभ {n}",
    "Left": "बाएँ",
    "Center": "केंद्र",
    "Right": "दाएँ",
    # ── Link dialog ───────────────────────────────────────────────────────────
    "Insert Link": "लिंक सम्मिलित करें",
    "Link Properties": "लिंक गुण",
    "e.g.  Click here": "उदा:  यहाँ क्लिक करें",
    "Display text:": "प्रदर्शन पाठ:",
    "https://example.com": "https://example.com",
    "URL:": "URL:",
    "Optional tooltip (shown on hover)": "वैकल्पिक टूलटिप (होवर पर दिखाई देती है)",
    "Title (optional):": "शीर्षक (वैकल्पिक):",
    # ── Image dialog ──────────────────────────────────────────────────────────
    "Insert Image": "चित्र सम्मिलित करें",
    "Image Properties": "चित्र गुण",
    "Short image description (for screen readers)":
        "चित्र का संक्षिप्त विवरण (स्क्रीन रीडर के लिए)",
    "Alt Text:": "वैकल्पिक पाठ:",
    "https://example.com/image.png  or  local path":
        "https://example.com/image.png  या  स्थानीय पथ",
    "Select local image file": "स्थानीय चित्र फ़ाइल चुनें",
    "URL / Path:": "URL / पथ:",
    "Images (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;All files (*)":
        "चित्र (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp *.ico);;सभी फ़ाइलें (*)",
    "Select Image File": "चित्र फ़ाइल चुनें",
    # ── PlantUML dialog ───────────────────────────────────────────────────────
    "Insert PlantUML Diagram": "PlantUML आरेख सम्मिलित करें",
    "Diagram type:": "आरेख प्रकार:",
    "PlantUML code:": "PlantUML कोड:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (internet connection required).":
        "सुझाव: सम्मिलित करने के बाद आरेख पूर्वावलोकन मुख्य विंडो में स्वतः दिखाई देगा"
        " (इंटरनेट कनेक्शन आवश्यक)।",
    # PlantUML template names
    "Sequence diagram": "अनुक्रम आरेख",
    "Class diagram": "वर्ग आरेख",
    "Activity diagram": "गतिविधि आरेख",
    "State diagram": "स्थिति आरेख",
    "Component diagram": "घटक आरेख",
    "Use case diagram": "उपयोग मामला आरेख",
    "Gantt diagram": "गैंट आरेख",
    "Mind map": "माइंड मैप",
    "WBS (Work breakdown)": "WBS (कार्य विघटन)",
    "Timing diagram": "समय आरेख",
    "Deployment diagram": "परिनियोजन आरेख",
    "JSON": "JSON",
    # ── File tree ─────────────────────────────────────────────────────────────
    "Current root directory": "वर्तमान मूल निर्देशिका",
    "Choose Directory": "निर्देशिका चुनें",
    # ── Settings dialog ───────────────────────────────────────────────────────
    "Settings": "सेटिंग्स",
    "Language:": "भाषा:",
    "Restart required to apply language changes.":
        "भाषा परिवर्तन लागू करने के लिए पुनरारंभ आवश्यक है।",
    "Editor theme:": "संपादक थीम:",
    "Preview theme:": "पूर्वावलोकन थीम:",
    "App theme:": "ऐप थीम:",
    "App theme requires restart.": "ऐप थीम के लिए पुनरारंभ आवश्यक है।",
    # ── Help menu ─────────────────────────────────────────────────────────────
    "&User Manual …": "&उपयोगकर्ता मैनुअल …",
    # ── Git integration ───────────────────────────────────────────────────────
    "Open from &Git …": "&Git से खोलें …",
    "Open File from Git": "Git से फ़ाइल खोलें",
    "GitHub / Bitbucket file URL:": "GitHub / Bitbucket फ़ाइल URL:",
    "Ref (branch/tag/commit):": "Ref (शाखा/टैग/commit):",
    "Cloning repository …": "रिपॉज़िटरी क्लोन हो रही है …",
    "Open from Git": "Git से खोलें",
    "Git Push": "Git Push",
    "Pushing to remote …": "रिमोट पर भेजा जा रहा है …",
    "Pushed to remote.": "रिमोट पर भेजा गया।",
    "Git push failed:\n{exc}": "Git push विफल हुआ:\n{exc}",
    "Clone failed:\n{exc}": "क्लोन विफल हुआ:\n{exc}",
    "File not found in repository:\n{path}": "रिपॉज़िटरी में फ़ाइल नहीं मिली:\n{path}",
    "Delete Git Temp Directory?": "Git अस्थायी निर्देशिका हटाएँ?",
    "A temporary Git clone is open:\n{path}\n\nDelete it now?":
        "एक अस्थायी Git क्लोन खुला है:\n{path}\n\nअभी हटाएँ?",
    "Push to": "इस पर भेजें",
    "Current branch ({branch})": "वर्तमान शाखा ({branch})",
    "New branch:": "नई शाखा:",
    "Create Pull Request": "Pull Request बनाएँ",
    "PR title:": "PR शीर्षक:",
    "Target branch:": "लक्ष्य शाखा:",
    "Git Commit & Push": "Git Commit & Push",
    "Git Authentication": "Git प्रमाणीकरण",
    "Auth method:": "प्रमाणीकरण विधि:",
    "HTTPS (embedded)": "HTTPS (अंतर्निहित)",
    "HTTPS (git binary)": "HTTPS (git बाइनरी)",
    "SSH (key file)": "SSH (की फ़ाइल)",
    "Token:": "टोकन:",
    "SSH key:": "SSH की:",
    "Passphrase:": "पासफ़्रेज़:",
    "Select SSH Key File": "SSH की फ़ाइल चुनें",
    "No credentials configured. Public repositories will still work.\n"
    "Configure credentials in View → Settings.":
        "कोई क्रेडेंशियल कॉन्फ़िगर नहीं। सार्वजनिक रिपॉज़िटरी काम करेंगी।\n"
        "दृश्य → सेटिंग्स में कॉन्फ़िगर करें।",
    "Push rejected (non-fast-forward).\nTry saving again using 'New branch'.":
        "Push अस्वीकृत (non-fast-forward)।\n'नई शाखा' का उपयोग करके फिर सहेजें।",
    "Commit message:": "Commit संदेश:",
    "Amend previous commit": "पिछले commit को सुधारें",
    "Git &Squash …": "Git &Squash …",
    "Git Squash Commits": "Git commits को मिलाएँ",
    "Select all new commits": "सभी नए commits चुनें",
    "SHA": "SHA",
    "Message": "संदेश",
    "Author": "लेखक",
    "Date": "दिनांक",
    "Squash commit message:": "Squash commit संदेश:",
    "Enter the combined commit message …": "संयुक्त commit संदेश दर्ज करें …",
    "Squash && Push": "मिलाएँ && भेजें",
    "Select at least 2 commits to squash.": "मिलाने के लिए कम से कम 2 commits चुनें।",
    "The selected commits must form a contiguous range starting from the most recent commit (HEAD).":
        "चुने गए commits को सबसे हाल के commit (HEAD) से शुरू होने वाली निरंतर श्रेणी बनानी होगी।",
    "cannot be empty.": "खाली नहीं हो सकता।",
    "Squashing commits …": "Commits मिलाए जा रहे हैं …",
    "Squash complete.": "मिलाना पूर्ण।",
    "Git squash failed:\n{exc}": "Git squash विफल हुआ:\n{exc}",
    "Could not read commit history:\n{exc}": "Commit इतिहास नहीं पढ़ा जा सका:\n{exc}",
    "No new commits found on this branch.": "इस शाखा पर कोई नया commit नहीं मिला।",
    "No new commits found compared to '{base}'.":
        "'{base}' की तुलना में कोई नया commit नहीं मिला।",
    "Reload": "पुनः लोड करें",
    "Git squash is only available with SSH or git-binary authentication.":
        "Git squash केवल SSH या git-binary प्रमाणीकरण के साथ उपलब्ध है।",
    "Username:": "उपयोगकर्ता नाम:",
    "Name:": "नाम:",
    "Email:": "ईमेल:",
    # ── Mermaid ───────────────────────────────────────────────────────────────
    "Insert Mermaid Diagram": "Mermaid आरेख सम्मिलित करें",
    "Mermaid code:": "Mermaid कोड:",
    "Tip: The diagram preview appears automatically in the main window after inserting"
    " (mermaid.js is loaded from CDN on first use).":
        "सुझाव: सम्मिलित करने के बाद आरेख पूर्वावलोकन मुख्य विंडो में स्वतः दिखाई देगा"
        " (पहली बार उपयोग पर CDN से mermaid.js लोड होता है)।",
    "&Mermaid …": "&Mermaid …",
    "Mermaid …": "Mermaid …",
    # Mermaid template names
    "Flowchart": "फ़्लोचार्ट",
    "Pie chart": "पाई चार्ट",
    "ER diagram": "ER आरेख",
    "Git graph": "Git ग्राफ़",
    "Gantt": "गैंट",
    # ── Proxy ─────────────────────────────────────────────────────────────────
    "HTTP Proxy": "HTTP प्रॉक्सी",
    "Proxy URL:": "प्रॉक्सी URL:",
    "Proxy username:": "प्रॉक्सी उपयोगकर्ता नाम:",
    "Proxy password:": "प्रॉक्सी पासवर्ड:",
    "Leave empty to use system proxy settings.":
        "सिस्टम प्रॉक्सी सेटिंग्स उपयोग करने के लिए खाली छोड़ें।",
}

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "de": _DE,
    "ar": _AR,
    "vi": _VI,
    "sv": _SV,
    "uk": _UK,
    "kn": _KN,
    "hi": _HI,
}


def setup(lang: str) -> None:
    """Call once before any UI is built to select the active language."""
    global _lang
    _lang = lang if (lang == "en" or lang in _TRANSLATIONS) else "en"


def current() -> str:
    """Return the active language code ('en', 'de', 'ar', …)."""
    return _lang


def is_rtl() -> bool:
    """Return True if the current language is right-to-left (e.g. Arabic)."""
    return _lang in RTL_LANGUAGES


def tr(text: str, **kwargs: object) -> str:
    """Translate *text* and optionally format with named placeholders."""
    table = _TRANSLATIONS.get(_lang)
    result = table.get(text, text) if table else text
    return result.format(**kwargs) if kwargs else result
