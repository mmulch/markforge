# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
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
]

pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')
datas   += pyqt6_datas
binaries += pyqt6_binaries
hiddenimports += pyqt6_hiddenimports

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
