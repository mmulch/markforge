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
    excludes=[
        # Unused Python stdlib
        'tkinter', '_tkinter',
        'unittest', 'doctest', 'pdb', 'pydoc',
        'turtle', 'curses',
        'multiprocessing', 'concurrent',
        'xmlrpc', 'ftplib', 'smtplib', 'telnetlib',
        # Unused PyQt6 Python bindings (prevents .pyd files being loaded)
        'PyQt6.Qt3DAnimation', 'PyQt6.Qt3DCore', 'PyQt6.Qt3DExtras',
        'PyQt6.Qt3DInput', 'PyQt6.Qt3DLogic', 'PyQt6.Qt3DRender',
        'PyQt6.QtBluetooth', 'PyQt6.QtCharts',
        'PyQt6.QtDataVisualization', 'PyQt6.QtLocation',
        'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets',
        'PyQt6.QtNfc', 'PyQt6.QtPositioning',
        'PyQt6.QtQuick', 'PyQt6.QtQuickControls2', 'PyQt6.QtQuickWidgets',
        'PyQt6.QtRemoteObjects', 'PyQt6.QtSensors', 'PyQt6.QtSerialPort',
        'PyQt6.QtSql', 'PyQt6.QtTest', 'PyQt6.QtTextToSpeech',
    ],
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
    name='Markforge',
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
    name='Markforge',
)
