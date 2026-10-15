"""Path helpers for dev, frozen EXE, and bundled resources."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def project_root() -> Path:
    """Directory containing main.py (or the EXE in onedir builds)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource_path(relative: str) -> Path:
    """Resolve a bundled resource path (PyInstaller _MEIPASS or project root)."""
    rel = Path(relative)
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", project_root()))
        candidate = base / rel
        if candidate.exists():
            return candidate
        # onedir: resources may sit next to the exe
        alt = project_root() / rel
        if alt.exists():
            return alt
        return candidate
    return project_root() / rel


def app_data_dir() -> Path:
    """Persistent config/history directory."""
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        path = base / "VideoDownloader"
    else:
        path = project_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    """Runtime log directory."""
    if getattr(sys, "frozen", False):
        path = app_data_dir() / "logs"
    else:
        path = project_root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def tools_ffmpeg_dir() -> Path:
    return project_root() / "tools" / "ffmpeg"


def optional_resource(relative: str) -> Path | None:
    """Return path if the resource exists, else None."""
    path = resource_path(relative)
    return path if path.is_file() else None


def sanitize_filename_component(name: str, max_len: int = 200) -> str:
    """Remove characters unsafe on Windows filenames."""
    forbidden = '<>:"/\\|?*'
    cleaned = "".join(c if c not in forbidden and ord(c) >= 32 else "_" for c in name)
    cleaned = cleaned.strip(" .")
    if not cleaned:
        cleaned = "download"
    return cleaned[:max_len]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
