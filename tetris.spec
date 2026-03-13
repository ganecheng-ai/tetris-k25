# -*- mode: python ; coding: utf-8 -*-
import os

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')

a = Analysis(
    ['src/main.py'],
    pathex=[src_path],
    binaries=[],
    datas=[],
    hiddenimports=[
        'game',
        'tetromino',
        'board',
        'renderer',
        'input_handler',
        'logger',
        'config',
        'pygame',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='tetris',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
