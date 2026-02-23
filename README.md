# MarkForge

A modern, feature-rich Markdown editor built with Python and PyQt6. Includes a live side-by-side preview, syntax highlighting, PlantUML diagram support, math formulas, PDF export, and full Git integration — in a clean, dual-pane interface.

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
- **Git integration** — open Markdown files directly from GitHub, GitHub Enterprise, Bitbucket Cloud, or Bitbucket Server; edit and push back without leaving the editor; amend the previous commit or squash multiple commits in one step (see [Git Integration](#git-integration))
- **Word count & cursor position** — always visible in the status bar
- **Multilingual** — English and German (Deutsch) UI
- **Persistent settings** — window geometry, splitter positions, and theme preferences are saved across sessions

### Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| New | `Ctrl+N` |
| Open | `Ctrl+O` |
| Open from Git | `Ctrl+Shift+G` |
| Git Squash | `Ctrl+Shift+Q` |
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
- **No git installation required** for HTTPS (API) and SSH modes — git operations use [dulwich](https://www.dulwich.io/), a pure-Python git implementation
- **`git` binary required** only for the optional *HTTPS (git binary)* auth mode (e.g. [Git for Windows](https://git-scm.com/))

Python dependencies (installed automatically by CMake):

| Package | Version | Purpose |
|---|---|---|
| PyQt6 | ≥ 6.4.0 | UI framework |
| PyQt6-WebEngine | ≥ 6.4.0 | Live preview |
| markdown | ≥ 3.4.0 | Markdown rendering |
| Pygments | ≥ 2.14.0 | Code syntax highlighting |
| PyMuPDF | ≥ 1.23.0 | PDF import |
| pymupdf4llm | ≥ 0.3.4 | PDF-to-Markdown conversion |
| dulwich | ≥ 0.20.50 | Pure-Python git client |

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

## Git Integration

MarkForge can open Markdown files directly from any hosted git platform, let you edit them, and push changes back — without leaving the editor. Advanced operations like **amend** and **squash** are supported for SSH and git-binary authentication.

### Supported platforms

| Platform | Example URL pattern |
|---|---|
| GitHub | `https://github.com/owner/repo/blob/main/README.md` |
| GitHub Enterprise | `https://github.mycompany.com/owner/repo/blob/main/docs/guide.md` |
| Bitbucket Cloud | `https://bitbucket.org/owner/repo/src/main/README.md` |
| Bitbucket Server / Data Center | `https://bitbucket.mycompany.com/projects/PROJ/repos/myrepo/browse/README.md?at=main` |

The platform is auto-detected from the URL structure, not the hostname — so any self-hosted instance works out of the box.

### Opening a file

1. **File → Open from Git…** (`Ctrl+Shift+G`)
2. Paste the URL of any file from one of the supported platforms
3. MarkForge validates the URL and shows a preview (`platform · owner/repo · path/to/file.md`)
4. Optionally override the branch in the **Ref** field
5. Click **OK** — the repository is cloned in the background and the file opens in the editor

The file tree header shows `[GIT] reponame` (in green) while a git-managed file is open.

### Saving (commit & push)

Press `Ctrl+S` while a git-managed file is open. A dialog appears with:

- **Commit message** — required
- **Amend previous commit** *(SSH & git binary, from the 2nd save onwards)* — replaces the previous commit instead of creating a new one; the previous commit message is pre-filled; uses force-push (`--force-with-lease`) automatically. Only commits created by MarkForge in the current session can be amended.
- **Push to:**
  - *Current branch* — pushes directly to the branch you cloned from
  - *New branch* — creates a new branch; optionally tick **Create Pull Request** to open a PR automatically
- **PR title / target branch** — shown when "Create Pull Request" is ticked

### Squashing commits

**File → Git Squash…** (`Ctrl+Shift+Q`) *(SSH & git binary only)*

Opens a dialog showing all commits on the current branch that are not yet in a chosen base branch (default: `main`). Select a contiguous range from the most recent commit, enter a combined message, and click **Squash & Push** — MarkForge rewrites the branch history and force-pushes.

- **Base branch** field: change the reference branch (e.g. `main`, `master`, `develop`) and click **Reload** to refresh the list
- **Select all new commits**: checks all commits in the list at once

### Closing

When you close the application while a git-managed file is open, MarkForge asks whether to delete the temporary clone directory.

### Authentication

Configure credentials in **View → Settings → Git Authentication**.

#### HTTPS (username + token)

Works on all platforms without any additional software. Uses the platform REST API — no local git history is maintained, so **amend and squash are not available** in this mode.

#### HTTPS (git binary)

Uses the system `git` executable for all operations (full local clone, commit, push). Requires [Git for Windows](https://git-scm.com/) (or any `git` binary on PATH). Supports **amend** and **squash** just like SSH. Token authentication is configured via the same Username + Token fields.

| Platform | Token type |
|---|---|
| GitHub | Personal access token (`ghp_…`) — needs `repo` scope |
| GitHub Enterprise | Personal access token — same as GitHub |
| Bitbucket Cloud | App password (Account → App passwords) |
| Bitbucket Server | Personal access token or HTTP access token |

> **Public repositories** work without any credentials configured.

#### SSH (key file)

Select **SSH (key file)** in settings and provide the path to your private key and an optional passphrase.

SSH uses [paramiko](https://www.paramiko.org/) for a fully pure-Python connection (no system ssh required):

```bash
pip install paramiko
```

Without paramiko, MarkForge falls back to the system `ssh` client if one is available.

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
│   ├── git_manager.py      # Pure-Python git logic (dulwich)
│   ├── git_dialogs.py      # Git open / commit & push dialogs
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
