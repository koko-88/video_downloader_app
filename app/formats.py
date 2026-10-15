"""Format labels and quality helpers for UI and yt-dlp."""

from __future__ import annotations

FORMAT_MP4 = "MP4 Video"
FORMAT_MP3 = "MP3 Audio"
FORMAT_M4A = "M4A Audio"
FORMAT_WEBM = "WEBM Video"

ALL_FORMATS = (FORMAT_MP4, FORMAT_MP3, FORMAT_M4A, FORMAT_WEBM)

VIDEO_QUALITIES = ("Best", "2160", "1440", "1080", "720", "480", "360")
AUDIO_QUALITIES = ("Best", "320 kbps", "256 kbps", "192 kbps", "128 kbps")
DEFAULT_AUDIO_QUALITY = "192 kbps"

_LEGACY_FORMAT_MAP = {
    "MP4": FORMAT_MP4,
    "MP3": FORMAT_MP3,
    "M4A": FORMAT_M4A,
    "WEBM": FORMAT_WEBM,
}


def normalize_format_label(fmt: str) -> str:
    f = fmt.strip()
    return _LEGACY_FORMAT_MAP.get(f.upper(), f) if f.upper() in _LEGACY_FORMAT_MAP else f


def is_video_format(fmt: str) -> bool:
    fmt = normalize_format_label(fmt)
    return fmt in (FORMAT_MP4, FORMAT_WEBM)


def is_audio_format(fmt: str) -> bool:
    fmt = normalize_format_label(fmt)
    return fmt in (FORMAT_MP3, FORMAT_M4A)


def mp3_preferred_quality(audio_quality: str) -> str | None:
    """Return kbps string for yt-dlp, or None for Best (no forced bitrate)."""
    q = audio_quality.strip()
    if q == "Best":
        return None
    if q.endswith("kbps"):
        return q.split()[0]
    return q


def video_height_filter(video_quality: str) -> str | None:
    """Return preferred max height as a string, or None for Best (no cap)."""
    q = video_quality.strip()
    if q == "Best":
        return None
    return q if q.isdigit() else None
