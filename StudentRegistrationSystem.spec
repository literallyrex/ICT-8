# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

PYTHON_BASE = Path(sys.base_prefix)
TCL_DATA_DIR = PYTHON_BASE / "tcl" / "tcl8.6"
TK_DATA_DIR = PYTHON_BASE / "tcl" / "tk8.6"

for env_name, env_path in (("TCL_LIBRARY", TCL_DATA_DIR), ("TK_LIBRARY", TK_DATA_DIR)):
    if not env_path.is_dir():
        raise SystemExit(f"{env_name} source folder not found: {env_path}")
    os.environ[env_name] = str(env_path)

datas = [('logo.png', '.'), (str(TCL_DATA_DIR), '_tcl_data'), (str(TK_DATA_DIR), '_tk_data')]
binaries = []
hiddenimports = ['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.font', 'tkinter.simpledialog', 'tkinter.constants', '_tkinter']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tkintermapview')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('matplotlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('mysql')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('geopy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='StudentRegistrationSystem',
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
