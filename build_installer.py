#!/usr/bin/env python3
"""Build Windows setup EXE (Inno Setup) from PyInstaller dist output."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

INNO_DOWNLOAD_URL = "https://jrsoftware.org/isdl.php"
INSTALLER_NAME = "VideoDownloader_Setup_1.0.0.exe"
BUILD_LOG = Path(__file__).resolve().parent / "build_logs" / "installer_build.log"


def _append_build_log(text: str) -> None:
    BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with BUILD_LOG.open("a", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")
    except OSError:
        pass  # bat may hold the log; stdout still shows the message


def iter_iscc_candidates() -> list[tuple[str, Path]]:
    """
    Ordered Inno Setup ISCC.exe search locations.
    Returns (label, path) for logging.
    """
    items: list[tuple[str, Path]] = []

    # 1. INNO_SETUP_DIR / INNO_SETUP_PATH
    for env_name in ("INNO_SETUP_DIR", "INNO_SETUP_PATH"):
        val = os.environ.get(env_name)
        if val:
            items.append((f"environment:{env_name}", Path(val) / "ISCC.exe"))

    # 2. PATH (placeholder — resolved separately)
    items.append(("PATH:ISCC", Path("PATH")))

    # 3–4. Per-user LocalAppData\Programs
    localappdata = os.environ.get("LOCALAPPDATA", "")
    if localappdata:
        for version in ("Inno Setup 6", "Inno Setup 7"):
            items.append(
                (
                    f"LOCALAPPDATA\\Programs\\{version}",
                    Path(localappdata) / "Programs" / version / "ISCC.exe",
                )
            )

    # Explicit Users\USERNAME paths (same tree, explicit for logging)
    username = os.environ.get("USERNAME", "")
    if username:
        for version in ("Inno Setup 6", "Inno Setup 7"):
            items.append(
                (
                    f"Users\\{username}\\AppData\\Local\\Programs\\{version}",
                    Path("C:/Users")
                    / username
                    / "AppData"
                    / "Local"
                    / "Programs"
                    / version
                    / "ISCC.exe",
                )
            )

    # 5–6. Program Files
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    pf64 = os.environ.get("ProgramFiles", r"C:\Program Files")
    for label, base in (("ProgramFiles(x86)", Path(pf86)), ("ProgramFiles", Path(pf64))):
        for version in ("Inno Setup 6", "Inno Setup 7"):
            items.append((f"{label}\\{version}", base / version / "ISCC.exe"))

    return items


def find_iscc() -> Path | None:
    """Locate Inno Setup compiler (ISCC.exe) using ordered search."""
    checked_lines: list[str] = ["Inno Setup ISCC.exe search:"]

    for label, path in iter_iscc_candidates():
        if label == "PATH:ISCC":
            found = shutil.which("ISCC") or shutil.which("iscc")
            line = f"  [PATH] ISCC -> {found if found else 'not found'}"
            checked_lines.append(line)
            if found:
                _append_build_log("\n".join(checked_lines))
                return Path(found).resolve()
            continue

        exists = path.is_file()
        status = "FOUND" if exists else "not found"
        checked_lines.append(f"  [{status}] {label}: {path}")
        if exists:
            _append_build_log("\n".join(checked_lines))
            return path.resolve()

    checked_lines.append("")
    checked_lines.append(
        "ERROR: Inno Setup was not found. Install Inno Setup 6 (per-user or all users), "
        "then run BUILD_INSTALLER_DOUBLE_CLICK.bat again."
    )
    _append_build_log("\n".join(checked_lines))
    return None


def open_inno_download_page() -> None:
    print(f"Opening download page: {INNO_DOWNLOAD_URL}")
    try:
        webbrowser.open(INNO_DOWNLOAD_URL)
    except Exception as e:
        print(f"(Could not open browser: {e})")


def _print_inno_not_found() -> None:
    print(
        "ERROR: Inno Setup was not found. Install Inno Setup 6, "
        "then run BUILD_INSTALLER_DOUBLE_CLICK.bat again.\n"
        f"Download: {INNO_DOWNLOAD_URL}\n"
    )
    print("All checked paths were written to:")
    print(f"  {BUILD_LOG}")
    print("\nPaths checked (in order):")
    for label, path in iter_iscc_candidates():
        if label == "PATH:ISCC":
            found = shutil.which("ISCC") or shutil.which("iscc")
            print(f"  PATH ISCC -> {found or 'not found'}")
        else:
            mark = "FOUND" if path.is_file() else "missing"
            print(f"  [{mark}] {path}")


def main() -> int:
    root = Path(__file__).resolve().parent
    dist_exe = root / "dist" / "VideoDownloader" / "VideoDownloader.exe"
    iss = root / "installer" / "VideoDownloader.iss"
    out_dir = root / "installer_output"
    installer_exe = out_dir / INSTALLER_NAME

    if not iss.is_file():
        print(f"ERROR: Missing installer script: {iss}")
        return 1

    if not dist_exe.is_file():
        print("PyInstaller output not found. Running build_exe.py first...")
        import build_exe

        if build_exe.main() != 0:
            print("ERROR: build_exe.py failed. Cannot create installer.")
            return 1
        if not dist_exe.is_file():
            print(f"ERROR: Still missing: {dist_exe}")
            return 1

    iscc = find_iscc()
    if iscc is None:
        _print_inno_not_found()
        open_inno_download_page()
        return 1

    print(f"Inno Setup compiler: {iscc}")
    out_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["INNO_SETUP_DIR"] = str(iscc.parent)

    cmd = [str(iscc), str(iss)]
    print("Running:", " ".join(cmd))
    print("Working directory:", root / "installer")
    result = subprocess.run(cmd, cwd=root / "installer", env=env)
    if result.returncode != 0:
        print(f"ERROR: ISCC failed with exit code {result.returncode}")
        return result.returncode

    if installer_exe.is_file():
        size_mb = installer_exe.stat().st_size / (1024 * 1024)
        print(f"\nInstaller OK: {installer_exe}")
        print(f"Size: {size_mb:.1f} MB")
        print("\nDouble-click the setup EXE to install on Windows.")
        return 0

    setups = sorted(
        out_dir.glob("VideoDownloader_Setup_*.exe"),
        key=lambda p: p.stat().st_mtime,
    )
    if setups:
        print(f"\nWARNING: Expected {INSTALLER_NAME}")
        print(f"Found instead: {setups[-1]}")
        return 1

    print(f"\nERROR: Installer was not created in: {out_dir}")
    print(f"Expected: {installer_exe}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
