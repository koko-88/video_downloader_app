"""Silent browser-cookie fallback for YouTube authentication errors."""

from __future__ import annotations

import logging
import re

from app.errors import is_youtube_url

logger = logging.getLogger("videodownloader")

BROWSER_FALLBACK_ORDER: tuple[str | None, ...] = (None, "edge", "chrome", "firefox")

_AUTH_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"sign in to confirm",
        r"confirm you.re not a bot",
        r"cookies[- ]from[- ]browser",
        r"cookiesfrombrowser",
        r"http error 403",
        r"please sign in",
        r"login required",
        r"not a bot",
        r"\bbot\b",
        r"sign in to confirm your age",
        r"this content isn.t available",
        r"use --cookies",
        r"authentication",
        r"members[- ]only",
        r"private video",
    )
]

_COOKIE_DB_LOCKED_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"could not copy",
        r"database is locked",
        r"permission denied",
        r"being used by another process",
    )
]


def is_cookie_db_locked(exc: BaseException) -> bool:
    text = str(exc)
    return any(p.search(text) for p in _COOKIE_DB_LOCKED_PATTERNS)


def is_youtube_auth_error(exc: BaseException) -> bool:
    text = str(exc)
    if hasattr(exc, "exc_info") and exc.exc_info:  # type: ignore[attr-defined]
        text += " " + str(exc.exc_info)
    return any(p.search(text) for p in _AUTH_PATTERNS)


def should_attempt_cookie_fallback(url: str, exc: BaseException) -> bool:
    return is_youtube_url(url) and is_youtube_auth_error(exc)


def browsers_to_try(url: str) -> tuple[str | None, ...]:
    """Anonymous first; browser cookies only for YouTube URLs."""
    if is_youtube_url(url):
        return BROWSER_FALLBACK_ORDER
    return (None,)


def log_attempt(url: str, browser: str | None, success: bool, detail: str = "") -> None:
    label = browser or "anonymous"
    level = logging.DEBUG if success else logging.WARNING
    logger.log(level, "Download attempt [%s] url=%s %s", label, url, detail)
