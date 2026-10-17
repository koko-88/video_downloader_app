"""User-facing error messages and exception mapping."""

from __future__ import annotations

import re
from urllib.error import HTTPError as UrlHTTPError
from urllib.parse import urlparse
from yt_dlp.networking.exceptions import HTTPError as YdlHTTPError
from app.privacy import redact

YOUTUBE_BLOCKED_MSG = (
    "YouTube blocked anonymous download. Open YouTube once in Edge or Chrome, "
    "make sure you are signed in, then try again."
)

FFMPEG_MISSING_MSG = (
    "FFmpeg was not found. Place ffmpeg.exe in tools/ffmpeg or install FFmpeg "
    "and add it to PATH. MP3 extraction and MP4 merging require FFmpeg."
)

FORMAT_UNAVAILABLE_MSG = (
    "No matching video format was available for the selected quality. "
    "Try Best quality or another resolution."
)

UNSUPPORTED_URL_MSG = "This link is not supported. Check the URL and try again."
VIDEO_UNAVAILABLE_MSG = (
    "This video is private, removed, or otherwise unavailable."
)
NETWORK_ERROR_MSG = "Network error. Check your connection and try again."
PERMISSION_ERROR_MSG = (
    "Cannot write to the output folder. Choose another folder or fix permissions."
)
DISK_ERROR_MSG = "Not enough disk space to complete the download."
FFMPEG_FAILURE_MSG = (
    "FFmpeg failed while merging or converting the file. See the log for details."
)
GENERIC_EXTRACT_MSG = "Could not extract video information. See the log file for details."
RATE_LIMITED_MSG = "The source is rate limiting requests. Wait before retrying."

URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)

_FORMAT_UNAVAILABLE = re.compile(
    r"requested format is not available|requested format not available",
    re.IGNORECASE,
)
_RATE_LIMITED = re.compile(
    r"\bHTTP(?:/\d+(?:\.\d+)?)?(?:\s*Error)?\s*[:=]?\s*429\b|"
    r"\bstatus(?:\s+code)?\s*[:=]?\s*429\b|"
    r"\btoo many requests\b|\brate[- _]?limit(?:ed|ing|s)?\b|"
    r"\brequests?\s+(?:(?:is|are|was|were|has\s+been|have\s+been)\s+)?(?:being\s+)?throttled\b|"
    r"\b(?:source|server|provider)\s+(?:is\s+)?throttling\s+requests?\b|^\s*throttled[.!]?\s*$",
    re.IGNORECASE,
)
_UNSUPPORTED_URL = re.compile(
    r"unsupported url|no suitable extractor|no extractor",
    re.IGNORECASE,
)
_UNAVAILABLE_VIDEO = re.compile(
    r"private video|video unavailable|has been removed|this video is not available|"
    r"account terminated|copyright|login required|members[- ]only",
    re.IGNORECASE,
)
_NETWORK = re.compile(
    r"timed out|timeout|network|temporarily unavailable|http error 5|"
    r"unable to download webpage|connection (reset|aborted|refused)|ssl",
    re.IGNORECASE,
)
_PERMISSION = re.compile(r"permission denied|errno 13|access is denied", re.IGNORECASE)
_DISK = re.compile(r"no space|errno 28|not enough space|disk full", re.IGNORECASE)
_FFMPEG_FAIL = re.compile(
    r"ffmpeg.+error|error.+ffmpeg|postprocessing|merging of multiple formats failed",
    re.IGNORECASE,
)


def is_format_unavailable_error(exc: BaseException) -> bool:
    return not is_rate_limited_error(exc) and bool(_FORMAT_UNAVAILABLE.search(str(exc)))


def is_rate_limited_error(exc: BaseException) -> bool:
    pending, seen = [exc], set()
    while pending and len(seen) < 16:
        current = pending.pop()
        if not isinstance(current, BaseException) or id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, (YdlHTTPError, UrlHTTPError)) and (
                getattr(current, "status", None) == 429 or getattr(current, "code", None) == 429):
            return True
        if _RATE_LIMITED.search(redact(str(current))):
            return True
        nested = getattr(current, "exc_info", None)
        if isinstance(nested, tuple) and len(nested) > 1:
            pending.append(nested[1])
        pending.extend((current.__cause__, getattr(current, "cause", None)))
    return False


class DownloadCancelled(Exception):
    """Raised when the user cancels an in-progress download."""


def is_valid_url(url: str) -> bool:
    """Validate HTTP(S) locations without embedded credentials or malformed ports."""
    url = url.strip()
    if not URL_PATTERN.match(url):
        return False
    try:
        parsed = urlparse(url)
        _ = parsed.port
        return bool(parsed.hostname and not parsed.username and not parsed.password
                    and not any(ord(char) < 32 for char in url))
    except ValueError:
        return False


def is_youtube_url(url: str) -> bool:
    try:
        host = urlparse(url.strip()).netloc.lower()
    except Exception:
        return False
    if host.startswith("www."):
        host = host[4:]
    return host in ("youtube.com", "youtu.be", "m.youtube.com", "www.youtube.com")


def map_error(exc: BaseException, *, url: str = "") -> str:
    """Map exceptions to friendly messages."""
    if isinstance(exc, DownloadCancelled):
        return "Download cancelled."

    if is_rate_limited_error(exc):
        return RATE_LIMITED_MSG

    msg = redact(str(exc).strip())
    lower = msg.lower()

    if isinstance(exc, TypeError) and "ffmpeg_location" in lower:
        return FFMPEG_MISSING_MSG

    if "path should be string" in lower or "os.pathlike" in lower:
        return (
            "Internal path error while preparing the download. "
            "Restart the app and try again."
        )

    if "ffmpeg" in lower and ("not found" in lower or "no such file" in lower):
        return FFMPEG_MISSING_MSG

    if _FORMAT_UNAVAILABLE.search(msg):
        return FORMAT_UNAVAILABLE_MSG

    if _UNSUPPORTED_URL.search(msg):
        return UNSUPPORTED_URL_MSG

    if _UNAVAILABLE_VIDEO.search(msg):
        return VIDEO_UNAVAILABLE_MSG

    if "unable to download" in lower or _NETWORK.search(msg):
        return NETWORK_ERROR_MSG

    if _PERMISSION.search(msg):
        return PERMISSION_ERROR_MSG

    if "disk" in lower or _DISK.search(msg):
        return DISK_ERROR_MSG

    if _FFMPEG_FAIL.search(msg) or (
        "ffmpeg" in lower and ("not found" not in lower)
    ):
        return FFMPEG_FAILURE_MSG

    if "error" in lower and ("extract" in lower or "youtube" in lower):
        return GENERIC_EXTRACT_MSG

    if len(msg) > 300:
        msg = msg[:297] + "..."
    return msg or "Download failed. See the log file for details."
