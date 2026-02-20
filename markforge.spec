# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# ── Qt DLL stems NOT used by MarkForge ────────────────────────────────────────
# Removing these saves 60-100 MB from the final package.
_UNUSED_QT = {
    'Qt63DAnimation', 'Qt63DCore', 'Qt63DExtras', 'Qt63DInput',
    'Qt63DLogic', 'Qt63DRender', 'Qt63DQuick', 'Qt63DQuickScene2D',
    'Qt6Bluetooth',
    'Qt6Charts',
    'Qt6DataVisualization',
    'Qt6Location',
    'Qt6Multimedia', 'Qt6MultimediaQuick', 'Qt6MultimediaWidgets',
    'Qt6Nfc',
    'Qt6Positioning', 'Qt6PositioningQuick',
    'Qt6Quick', 'Qt6QuickControls2', 'Qt6QuickDialogs2',
    'Qt6QuickLayouts', 'Qt6QuickParticles', 'Qt6QuickShapes',
    'Qt6QuickTemplates2', 'Qt6QuickTimeline', 'Qt6QuickWidgets',
    'Qt6RemoteObjects',
    'Qt6Sensors',
    'Qt6SerialPort',
    'Qt6Sql',
    'Qt6Test',
    'Qt6TextToSpeech',
    'Qt6VirtualKeyboard',
    'Qt6WebView',
}

datas, binaries, hiddenimports = collect_all('PyQt6')

# Drop unused Qt DLLs and their associated data files
binaries = [
    (src, dst) for src, dst in binaries
    if not any(name in src for name in _UNUSED_QT)
]
datas = [
    (src, dst) for src, dst in datas
    if not any(name in src for name in _UNUSED_QT)
]

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
    # PDF import (lazy imports — PyInstaller can't detect these automatically)
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
        'difflib', 'turtle', 'curses',
        'multiprocessing', 'concurrent',
        'xmlrpc', 'ftplib', 'smtplib', 'telnetlib',
        # Unused PyQt6 Python bindings
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
