"""Build yt-dlp options from UI choices."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from app.errors import DownloadCancelled
from app.privacy import redact
from app.js_runtime import resolve_js_runtimes
from app.ffmpeg_resolver import FFmpegInfo
from app.formats import (
    FORMAT_M4A,
    FORMAT_MP3,
    FORMAT_WEBM,
    mp3_preferred_quality,
    normalize_format_label,
    video_height_filter,
)

logger = logging.getLogger("videodownloader")

ProgressCallback = Callable[[int], None]
LogCallback = Callable[[str], None]
CancelCheck = Callable[[], bool]

GENERIC_FALLBACK_FORMAT = "bestvideo*+bestaudio/best"
DEFAULT_VIDEO_FORMAT = "bv*+ba/b"

_last_progress_emit = 0.0

_SENSITIVE_LOG_MARKERS = (
    "googlevideo.com",
    "signature=",
    "sig=",
    "/videoplayback",
    "authorization",
    "cookie",
    "set-cookie",
    "pot=",
    "n=",
    "xtags=",
)


def _throttled_emit(callback: ProgressCallback | None, percent: int) -> None:
    global _last_progress_emit
    if callback is None:
        return
    now = time.monotonic()
    if percent >= 100 or now - _last_progress_emit >= 0.1:
        _last_progress_emit = now
        callback(percent)


def reset_progress_throttle() -> None:
    global _last_progress_emit
    _last_progress_emit = 0.0


def make_progress_hook(
    on_progress: ProgressCallback | None,
    is_cancelled: CancelCheck,
) -> Callable:
    def hook(d: dict) -> None:
        if is_cancelled():
            raise DownloadCancelled()

        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes") or 0
            if total and total > 0:
                pct = int(downloaded * 100 / total)
                _throttled_emit(on_progress, min(max(pct, 0), 99))
        elif status == "finished":
            _throttled_emit(on_progress, 99)

    return hook


class YdlLogger:
    """Forward yt-dlp logs without dumping signed media URLs."""

    def __init__(self, app_logger: logging.Logger | None = None,
                 is_cancelled: CancelCheck | None = None) -> None:
        self._log = app_logger or logger
        self._is_cancelled = is_cancelled or (lambda: False)

    def _safe(self, msg: str) -> str | None:
        if self._is_cancelled():
            raise DownloadCancelled()
        text = str(msg)
        lower = text.lower()
        if any(marker in lower for marker in _SENSITIVE_LOG_MARKERS):
            return None
        text = redact(text)
        if len(text) > 2000:
            return text[:2000] + "..."
        return text

    def debug(self, msg: str) -> None:
        safe = self._safe(msg)
        if safe is None:
            return
        if safe.startswith("[debug]"):
            self._log.debug("%s", safe)
        else:
            self._log.debug("%s", safe)

    def info(self, msg: str) -> None:
        safe = self._safe(msg)
        if safe is not None:
            self._log.info("%s", safe)

    def warning(self, msg: str) -> None:
        safe = self._safe(msg)
        if safe is not None:
            self._log.warning("%s", safe)

    def error(self, msg: str) -> None:
        safe = self._safe(msg)
        if safe is not None:
            self._log.error("%s", safe)


def url_domain(url: str) -> str:
    try:
        host = (urlparse(url.strip()).hostname or '').lower()
    except Exception:
        return "unknown"
    if host.startswith("www."):
        host = host[4:]
    return host or "unknown"


def _validate_ydl_opts(opts: dict) -> None:
    if "ffmpeg_location" in opts:
        loc = opts["ffmpeg_location"]
        if not isinstance(loc, str):
            raise TypeError(
                f"Invalid ffmpeg_location type: {type(loc).__name__}. "
                "Expected str path to FFmpeg directory."
            )
        if not loc.strip():
            del opts["ffmpeg_location"]

    for key, val in opts.items():
        if val is None:
            raise TypeError(f"yt-dlp option {key!r} must not be None")


def _video_format_sort(video_quality: str, container: str) -> list[str]:
    """Prefer max resolution and container-friendly codecs; never require exact IDs."""
    sort: list[str] = []
    height = video_height_filter(video_quality)
    if height is not None:
        sort.append(f"res:{height}")
    if container == "mp4":
        sort.extend(["vcodec:h264", "acodec:m4a"])
    elif container == "webm":
        sort.extend(["vcodec:vp9.2", "vcodec:vp9", "acodec:opus"])
    return sort


def build_ydl_opts(
    *,
    output_dir: Path,
    fmt: str,
    video_quality: str,
    audio_quality: str,
    ffmpeg_info: FFmpegInfo,
    cookies_browser: str | None = None,
    on_progress: ProgressCallback | None = None,
    is_cancelled: CancelCheck | None = None,
    use_generic_fallback: bool = False,
) -> dict:
    """Build yt-dlp options dict from user preferences (single source of truth)."""
    fmt_label = normalize_format_label(fmt)

    if not output_dir.is_absolute():
        output_dir = output_dir.resolve()
    out_dir = str(output_dir)
    outtmpl = str(Path(out_dir) / "%(title).200B [%(id)s].%(ext)s")

    opts: dict = {
        "outtmpl": outtmpl,
        "noprogress": True,
        "quiet": True,
        "no_warnings": False,
        "retries": 10,
        "fragment_retries": 10,
        "extractor_retries": 3,
        "file_access_retries": 3,
        "socket_timeout": 30,
        "ignoreerrors": False,
        "noplaylist": False,
        "windowsfilenames": True,
        "restrictfilenames": False,
        "logger": YdlLogger(is_cancelled=is_cancelled),
        "js_runtimes": resolve_js_runtimes(),
        "remote_components": [],
        "progress_hooks": [
            make_progress_hook(on_progress, is_cancelled or (lambda: False))
        ],
    }

    if ffmpeg_info.found and ffmpeg_info.ffmpeg_dir is not None:
        opts["ffmpeg_location"] = str(ffmpeg_info.ffmpeg_dir)

    if cookies_browser:
        opts["cookiesfrombrowser"] = (cookies_browser,)

    if fmt_label == FORMAT_MP3:
        opts["format"] = (
            GENERIC_FALLBACK_FORMAT if use_generic_fallback else "bestaudio/best"
        )
        pp: dict = {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }
        kbps = mp3_preferred_quality(audio_quality)
        if kbps is not None:
            pp["preferredquality"] = kbps
        opts["postprocessors"] = [pp]

    elif fmt_label == FORMAT_M4A:
        opts["format"] = (
            GENERIC_FALLBACK_FORMAT
            if use_generic_fallback
            else "bestaudio[ext=m4a]/bestaudio/best"
        )
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ]

    elif fmt_label == FORMAT_WEBM:
        opts["format"] = (
            GENERIC_FALLBACK_FORMAT if use_generic_fallback else DEFAULT_VIDEO_FORMAT
        )
        opts["format_sort"] = _video_format_sort(video_quality, "webm")
        opts["merge_output_format"] = "webm"
        opts["postprocessors"] = [{"key": "FFmpegVideoRemuxer", "preferedformat": "webm"}]

    else:
        opts["format"] = (
            GENERIC_FALLBACK_FORMAT if use_generic_fallback else DEFAULT_VIDEO_FORMAT
        )
        opts["format_sort"] = _video_format_sort(video_quality, "mp4")
        opts["merge_output_format"] = "mp4"
        opts["postprocessors"] = [{"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}]

    _validate_ydl_opts(opts)
    return opts


def describe_format_plan(opts: dict, video_quality: str, fmt: str) -> str:
    return (
        f"fmt={normalize_format_label(fmt)} quality={video_quality} "
        f"selector={opts.get('format')!r} format_sort={opts.get('format_sort')!r} "
        f"merge={opts.get('merge_output_format')!r} outtmpl={opts.get('outtmpl')!r}"
    )
