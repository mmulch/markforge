# MarkForge

A modern, feature-rich Markdown editor built with Python and PyQt6. Includes a live side-by-side preview, syntax highlighting, PlantUML diagram support, math formulas, and PDF export — in a clean, dual-pane interface.

![License](https://img.shields.io/badge/license-GPL--3.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4%2B-green)

---

## Features

- **Live preview** — rendered side-by-side with GitHub-styled CSS (dark & light themes)
- **Editor themes** — switch the editor between dark and light independently of the preview
- **Syntax highlighting** — Markdown-aware highlighting with matching dark/light colour schemes
- **Line numbers** — gutter with current-line highlight
- **File tree** — browse Markdown files and images in the project directory
- **Insert dialogs** — guided dialogs for links, images, tables, and PlantUML diagrams
- **PlantUML support** — embed diagrams rendered via the PlantUML online service
- **Math formulas** — LaTeX notation rendered with MathJax
- **PDF import** — import any PDF and convert it to Markdown automatically (headings, paragraphs, tables preserved)
- **PDF export** — export the current document as a PDF
- **Word count & cursor position** — always visible in the status bar
- **Multilingual** — English and German (Deutsch) UI
- **Persistent settings** — window geometry, splitter positions, and theme preferences are saved across sessions

### Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| New | `Ctrl+N` |
| Open | `Ctrl+O` |
| Save | `Ctrl+S` |
| Save As | `Ctrl+Shift+S` |
| Export as PDF | `Ctrl+Shift+E` |
| Import PDF | `Ctrl+Shift+I` |
| Toggle file tree | `Ctrl+B` |
| Toggle preview | `Ctrl+Shift+P` |
| Insert link | `Ctrl+K` |
| Insert image | `Ctrl+Shift+K` |
| Insert PlantUML | `Ctrl+Shift+U` |
| Insert table | `Ctrl+Shift+T` |

---

## Requirements

- Python 3.8+
- CMake 3.16+

Python dependencies (installed automatically by CMake):

| Package | Version |
|---|---|
| PyQt6 | ≥ 6.4.0 |
| PyQt6-WebEngine | ≥ 6.4.0 |
| markdown | ≥ 3.4.0 |
| Pygments | ≥ 2.14.0 |
| PyMuPDF | ≥ 1.23.0 |
| pymupdf4llm | ≥ 0.3.4 |

---

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/mmulch/markforge.git
cd markforge

# 2. Configure the build
cmake -B build

# 3. Install Python dependencies into the local virtual environment
cmake --build build --target install_deps

# 4. Run the application
cmake --build build --target run
```

Or run directly without CMake:

```bash
pip install -r requirements.txt
python src/main.py
```

---

## Packages & Installers

Pre-built packages are published on the [Releases](../../releases) page and built automatically via GitHub Actions whenever a version tag (`v*.*.*`) is pushed.

### Debian / Ubuntu

```bash
sudo apt install ./markforge_*.deb
```

The package declares system-level dependencies (`python3-pyqt6`, `python3-pyqt6.qtwebengine`, `python3-markdown`, `python3-pygments`) — no virtual environment required.

### Windows

Download and run `Markforge-Setup.exe` from the Releases page.

To build the Windows installer yourself you need:
- [PyInstaller](https://pyinstaller.org/) (`pip install pyinstaller`)
- [Inno Setup 6](https://jrsoftware.org/isinfo.php)
- [ImageMagick](https://imagemagick.org/) (for icon generation)

---

## Supported Markdown Extensions

- Tables, footnotes, abbreviations (`extra`)
- Syntax-highlighted code blocks (`codehilite` + Pygments)
- Table of contents (`toc`)
- Strikethrough (`~~text~~`)
- Task lists
- PlantUML diagram blocks
- LaTeX math via MathJax

---

## Project Structure

```
markforge/
├── src/                    # Python source files
│   ├── main.py             # Entry point
│   ├── mainwindow.py       # Main window and application logic
│   ├── editor_widget.py    # Text editor with line numbers
│   ├── preview_widget.py   # Live HTML preview (WebEngine)
│   ├── highlighter.py      # Markdown syntax highlighter
│   ├── file_tree_widget.py # Project file browser
│   ├── i18n.py             # Translations (EN/DE)
│   └── ...                 # Insert dialogs, settings, help dialogs
├── assets/
│   └── markforge.svg       # Application logo
├── .github/workflows/
│   ├── release-windows.yml # CI/CD: build & release Windows installer
│   └── release-debian.yml  # CI/CD: build & release Debian package
├── CMakeLists.txt
├── requirements.txt
├── markforge.spec          # PyInstaller configuration
└── LICENSE
```

---

## License

Copyright © Marcel Mulch

Released under the [GNU General Public License v3.0](LICENSE).

Developed with help of Claude Code