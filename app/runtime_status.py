"""Lightweight runtime dependency status for logs and diagnostics."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from app.ffmpeg_resolver import resolve_ffmpeg
from app.js_runtime import resolve_js_runtimes


@dataclass
class RuntimeStatus:
    ytdlp_version: str
    ytdlp_path: str
    ytdlp_runtime: str
    python_executable: str
    ytdlp_ejs: str
    ffmpeg: str
    ffprobe: str
    js_runtime: str


def collect_runtime_status() -> RuntimeStatus:
    ytdlp_version = "unavailable"
    ytdlp_path = "unavailable"
    ytdlp_runtime = "PyInstaller-bundled Python package" if getattr(
        sys, "frozen", False
    ) else "Python package"
    ytdlp_ejs = "not found"
    js_runtime = "not detected"
    try:
        import yt_dlp

        ytdlp_version = getattr(yt_dlp.version, "__version__", "unknown")
        ytdlp_path = str(getattr(yt_dlp, "__file__", "unknown"))
    except Exception as e:
        ytdlp_version = f"error: {e}"
        ytdlp_path = f"error: {e}"

    try:
        import yt_dlp_ejs

        ytdlp_ejs = getattr(yt_dlp_ejs, "__version__", "present")
    except Exception:
        ytdlp_ejs = "not found"

    for name, configuration in resolve_js_runtimes().items():
        js_runtime = f"{name} ({configuration['path']})"

    info = resolve_ffmpeg()
    ffmpeg = str(info.ffmpeg_path) if info.found and info.ffmpeg_path else "not found"
    ffprobe = str(info.ffprobe_path) if info.ffprobe_path else "not found"
    return RuntimeStatus(
        ytdlp_version=ytdlp_version,
        ytdlp_path=ytdlp_path,
        ytdlp_runtime=ytdlp_runtime,
        python_executable=sys.executable,
        ytdlp_ejs=ytdlp_ejs,
        ffmpeg=ffmpeg,
        ffprobe=ffprobe,
        js_runtime=js_runtime,
    )
