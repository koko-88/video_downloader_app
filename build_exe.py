#!/usr/bin/env python3
"""Build the VideoDownloader Windows executable (PyInstaller onedir)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, help="New isolated build destination; existing build/dist are never removed")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    spec = root / "video_downloader.spec"

    if not spec.is_file():
        print(f"ERROR: Missing spec file: {spec}")
        return 1

    resources = root / "resources"
    icon = resources / "icon.ico"
    loader = resources / "loader.gif"
    ffmpeg = root / "tools" / "ffmpeg" / "ffmpeg.exe"

    print("=== PyInstaller build ===")
    print(f"  Project:  {root}")
    print(f"  icon.ico:     {'yes' if icon.is_file() else 'no (optional)'}")
    print(f"  loader.gif:   {'yes' if loader.is_file() else 'no (optional)'}")
    if ffmpeg.is_file():
        print(f"  ffmpeg.exe:   yes (will bundle)")
    else:
        print("  ffmpeg.exe:   no (optional - app can use PATH FFmpeg at runtime)")
        print("                Put ffmpeg.exe in tools/ffmpeg/ before build to bundle it.")

    destination = args.output_root.resolve() if args.output_root else root
    try:
        destination.relative_to(root)
    except ValueError:
        print("ERROR: Build destination must be inside this workspace.")
        return 1
    if any((destination / folder).exists() for folder in ("build", "dist")):
        print("ERROR: Existing build/dist preserved. Choose a new --output-root inside the workspace.")
        return 1
    destination.mkdir(parents=True, exist_ok=True)


    # Ensure PyInstaller is available
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("ERROR: PyInstaller not installed. Run: pip install -r requirements.txt")
        return 1

    try:
        import yt_dlp
    except ImportError:
        print("ERROR: yt-dlp is not installed in the build Python environment.")
        return 1

    print(f"  Python executable: {sys.executable}")
    print(f"  yt-dlp version:    {yt_dlp.version.__version__}")
    print(f"  yt-dlp package:    {yt_dlp.__file__}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec),
        "--noconfirm",
        "--clean",
        "--distpath", str(destination / "dist"),
        "--workpath", str(destination / "build"),
    ]
    print("Running:", " ".join(cmd))
    build_env = os.environ.copy()
    build_env["PYINSTALLER_CONFIG_DIR"] = str(destination / "cache")
    path_entries = build_env.get("PATH", "").split(os.pathsep)
    clean_path_entries = [
        entry for entry in path_entries if "codex-runtimes" not in entry.lower()
    ]
    if clean_path_entries != path_entries:
        print("Removed Codex workspace runtime paths from the PyInstaller build PATH")
        build_env["PATH"] = os.pathsep.join(clean_path_entries)

    result = subprocess.run(cmd, cwd=root, env=build_env)
    if result.returncode != 0:
        print(f"ERROR: PyInstaller failed (exit {result.returncode})")
        return result.returncode

    exe = destination / "dist" / "VideoDownloader" / "VideoDownloader.exe"
    if not exe.is_file():
        print("ERROR: Build finished but EXE not found:")
        print(f"  {exe}")
        return 1

    print(f"\nBuild OK: {exe}")
    bundled_ffmpeg = destination / "dist" / "VideoDownloader" / "tools" / "ffmpeg" / "ffmpeg.exe"
    if bundled_ffmpeg.is_file():
        print(f"Bundled FFmpeg: {bundled_ffmpeg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
