# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — bundles only files that exist (no missing icon/ffmpeg errors)."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

spec_dir = Path(SPEC).resolve().parent
datas = []
binaries = []
hiddenimports = [
    "app",
    "app.main_window",
    "app.download_queue",
    "app.downloader_worker",
    "app.ydl_options",
    "app.cookie_fallback",
    "app.ffmpeg_resolver",
    "app.config",
    "app.history",
    "app.logger_setup",
    "app.errors",
    "app.paths",
    "app.formats",
    "app.runtime_status",
    "yt_dlp",
    "yt_dlp.extractor",
    "yt_dlp.extractor.youtube",
    "yt_dlp_ejs",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]

for pkg in ("yt_dlp", "yt_dlp_ejs"):
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception:
        pass

try:
    hiddenimports += collect_submodules("yt_dlp")
except Exception:
    pass

resources_dir = spec_dir / "resources"
if resources_dir.is_dir():
    for item in sorted(resources_dir.iterdir()):
        if item.is_file() and item.name not in (".gitkeep",):
            datas.append((str(item), "resources"))

ffmpeg_dir = spec_dir / "tools" / "ffmpeg"
if ffmpeg_dir.is_dir():
    for f in sorted(ffmpeg_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in (".exe", ".dll"):
            datas.append((str(f), "tools/ffmpeg"))

icon_path = resources_dir / "icon.ico"
icon_arg = str(icon_path) if icon_path.is_file() else None

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[str(spec_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VideoDownloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_arg,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="VideoDownloader",
)
