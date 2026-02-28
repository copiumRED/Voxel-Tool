# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()
if not (project_root / "src" / "app" / "main.py").exists():
    project_root = project_root.parent
assets_dir = project_root / "assets"
datas = []
if assets_dir.exists():
    datas.append((str(assets_dir), "assets"))

block_cipher = None

a = Analysis(
    [str(project_root / "src" / "app" / "main.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtOpenGL",
        "PySide6.QtOpenGLWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VoxelTool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="VoxelTool",
)
