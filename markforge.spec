# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# ── Qt DLL stems NOT used by MarkForge ────────────────────────────────────────
# Filtered AFTER Analysis so PyInstaller's DLL-dependency tracker can't re-add
# them via indirect dependencies.
_UNUSED_QT = {
    'qt63danimation', 'qt63dcore', 'qt63dextras', 'qt63dinput',
    'qt63dlogic', 'qt63drender', 'qt63dquick', 'qt63dquickscene2d',
    'qt6bluetooth',
    'qt6charts',
    'qt6datavisualization',
    'qt6location',
    'qt6multimedia', 'qt6multimediaquick', 'qt6multimediawidgets',
    'qt6nfc',
    'qt6positioning', 'qt6positioningquick',
    'qt6quick', 'qt6quickcontrols2', 'qt6quickdialogs2',
    'qt6quicklayouts', 'qt6quickparticles', 'qt6quickshapes',
    'qt6quicktemplates2', 'qt6quicktimeline', 'qt6quickwidgets',
    'qt6remoteobjects',
    'qt6sensors',
    'qt6serialport',
    'qt6sql',
    'qt6test',
    'qt6texttospeech',
    'qt6virtualkeyboard',
    'qt6webview',
}

def _needed(name):
    """Return False for Qt DLLs / .pyd files we don't need."""
    # name is the dest path, e.g. 'PyQt6/Qt6/bin/Qt63DCore.dll'
    stem = name.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]  # basename
    stem = stem.rsplit('.', 1)[0].lower()               # strip extension
    return stem not in _UNUSED_QT

datas, binaries, hiddenimports = collect_all('PyQt6')

_dulwich_datas, _dulwich_binaries, _dulwich_hidden = collect_all('dulwich')
datas     += _dulwich_datas
binaries  += _dulwich_binaries
hiddenimports += _dulwich_hidden

hiddenimports += [
    'markdown',
    'markdown.extensions',
    'markdown.extensions.extra',
    'markdown.extensions.codehilite',
    'markdown.extensions.fenced_code',
    'markdown.extensions.tables',
    'markdown.extensions.toc',
    'markdown.extensions.sane_lists',
    'pygments',
    'pygments.lexers',
    'pygments.formatters',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebChannel',
    'PyQt6.QtPrintSupport',
    # PDF import — lazy imports not visible to PyInstaller's static analysis
    'fitz',
    'pymupdf',
    'pymupdf4llm',
]

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# ── Post-analysis DLL filter ───────────────────────────────────────────────────
# PyInstaller's dependency tracker re-adds Qt DLLs via DLL-import analysis.
# Filter a.binaries HERE (after Analysis) to actually remove them.
a.binaries = TOC([
    (name, src, typ)
    for name, src, typ in a.binaries
    if _needed(name)
])

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MarkForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/markforge.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MarkForge',
)
