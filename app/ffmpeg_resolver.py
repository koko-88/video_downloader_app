"""Locate FFmpeg for yt-dlp — automatic, no user picker."""

from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.paths import project_root, tools_ffmpeg_dir

logger = logging.getLogger("videodownloader")

_UNSET = object()
_cached: FFmpegInfo | object = _UNSET

_COMMON_FFMPEG_DIRS = (
    Path(r"C:\ffmpeg\bin"),
    Path(r"C:\Program Files\ffmpeg\bin"),
    Path(r"C:\Program Files (x86)\ffmpeg\bin"),
)


@dataclass
class FFmpegInfo:
    found: bool
    ffmpeg_path: Optional[Path] = None
    ffprobe_path: Optional[Path] = None
    ffmpeg_dir: Optional[Path] = None
    source: str = "not_found"


def _dir_has_ffmpeg(directory: Path) -> Optional[Path]:
    for name in ("ffmpeg.exe", "ffmpeg"):
        candidate = directory / name
        if candidate.is_file():
            return candidate.resolve()
    return None


def _find_ffprobe(ffmpeg_exe: Path) -> Optional[Path]:
    directory = ffmpeg_exe.parent
    for name in ("ffprobe.exe", "ffprobe"):
        candidate = directory / name
        if candidate.is_file():
            return candidate.resolve()
    return None


def _search_dirs() -> list[tuple[str, Path]]:
    """Ordered search locations: (label, directory to check)."""
    items: list[tuple[str, Path]] = []
    root = project_root()

    items.append(("bundled:tools/ffmpeg", root / "tools" / "ffmpeg"))
    items.append(("bundled:project tools", tools_ffmpeg_dir()))
    items.append(("next to executable", root))
    items.append(("internal bundle", root / "_internal" / "tools" / "ffmpeg"))

    for common in _COMMON_FFMPEG_DIRS:
        items.append((f"common:{common.name}", common))

    path_env = os.environ.get("PATH", "")
    for part in path_env.split(os.pathsep):
        part = part.strip().strip('"')
        if part:
            items.append(("PATH", Path(part)))

    seen: set[str] = set()
    unique: list[tuple[str, Path]] = []
    for label, d in items:
        try:
            key = str(d.resolve()).lower()
        except OSError:
            key = str(d).lower()
        if key not in seen:
            seen.add(key)
            unique.append((label, d))
    return unique


def _build_info_from_exe(ffmpeg_exe: Path, source: str) -> FFmpegInfo:
    ffmpeg_dir = ffmpeg_exe.parent.resolve()
    return FFmpegInfo(
        found=True,
        ffmpeg_path=ffmpeg_exe,
        ffprobe_path=_find_ffprobe(ffmpeg_exe),
        ffmpeg_dir=ffmpeg_dir,
        source=source,
    )


def resolve_ffmpeg() -> FFmpegInfo:
    """Return FFmpeg discovery result. Never returns object() or non-Path values."""
    global _cached
    if _cached is not _UNSET:
        assert isinstance(_cached, FFmpegInfo)
        return _cached

    for label, directory in _search_dirs():
        ffmpeg_exe = _dir_has_ffmpeg(directory)
        if ffmpeg_exe:
            info = _build_info_from_exe(ffmpeg_exe, source=label)
            _cached = info
            logger.info(
                "FFmpeg found (%s): %s",
                label,
                info.ffmpeg_path,
            )
            return info

    found = shutil.which("ffmpeg")
    if found:
        info = _build_info_from_exe(
            Path(found).resolve(),
            source="PATH:which",
        )
        _cached = info
        logger.info("FFmpeg found (which): %s", info.ffmpeg_path)
        return info

    info = FFmpegInfo(found=False)
    _cached = info
    logger.warning("FFmpeg not found")
    return info


def ffmpeg_status_message() -> str:
    info = resolve_ffmpeg()
    if info.found and info.ffmpeg_dir:
        return f"FFmpeg: OK ({info.ffmpeg_dir})"
    return (
        "FFmpeg: not found (MP3/MP4 need FFmpeg in tools/ffmpeg, next to the app, or PATH)"
    )


def needs_ffmpeg(fmt: str) -> bool:
    from app.formats import normalize_format_label

    label = normalize_format_label(fmt)
    return label in (
        "MP4 Video",
        "MP3 Audio",
        "M4A Audio",
        "WEBM Video",
    )


def clear_cache() -> None:
    global _cached
    _cached = _UNSET
