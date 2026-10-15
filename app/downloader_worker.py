"""Background download worker using yt-dlp."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

import yt_dlp
from yt_dlp.utils import DownloadError

from app.cookie_fallback import (
    browsers_to_try,
    is_cookie_db_locked,
    log_attempt,
    should_attempt_cookie_fallback,
)
from app.errors import (
    DownloadCancelled,
    FFMPEG_MISSING_MSG,
    YOUTUBE_BLOCKED_MSG,
    is_format_unavailable_error,
    map_error,
)
from app.ffmpeg_resolver import FFmpegInfo, needs_ffmpeg, resolve_ffmpeg
from app.formats import FORMAT_MP3, FORMAT_M4A, normalize_format_label
from app.ydl_options import (
    GENERIC_FALLBACK_FORMAT,
    build_ydl_opts,
    describe_format_plan,
    url_domain,
)

logger = logging.getLogger("videodownloader")


def _normalize_info(info: dict[str, Any] | None) -> dict[str, Any] | None:
    if not info:
        return None
    if info.get("_type") in ("playlist", "multi_video") and info.get("entries"):
        entry = info["entries"][0]
        if entry:
            return entry
    return info


def _expected_extensions(fmt_label: str) -> list[str]:
    if fmt_label == FORMAT_MP3:
        return [".mp3"]
    if fmt_label == FORMAT_M4A:
        return [".m4a"]
    if fmt_label == "WEBM Video":
        return [".webm", ".mkv"]
    return [".mp4", ".mkv", ".webm"]


def _resolve_output_path(
    ydl: yt_dlp.YoutubeDL,
    info: dict[str, Any] | None,
    output_dir: Path,
    fmt: str,
) -> str | None:
    info = _normalize_info(info)
    if not info:
        return None

    fmt_label = normalize_format_label(fmt)
    exts = _expected_extensions(fmt_label)

    requested = info.get("requested_downloads") or []
    for item in reversed(requested):
        fp = item.get("filepath")
        if fp and Path(fp).is_file():
            return str(Path(fp).resolve())

    try:
        filepath = ydl.prepare_filename(info)
    except Exception:
        filepath = None

    if not filepath:
        return None

    path = Path(filepath)
    for ext in exts:
        candidate = path.with_suffix(ext)
        if candidate.is_file():
            return str(candidate.resolve())
        matches = sorted(output_dir.glob(f"{path.stem}*{ext}"))
        if matches:
            return str(matches[0].resolve())

    if path.is_file():
        return str(path.resolve())
    return str(path)


class DownloaderWorker:
    """Runs download in a QThread via run() — not a QObject subclass."""

    def __init__(
        self,
        url: str,
        output_dir: Path,
        fmt: str,
        video_quality: str,
        audio_quality: str,
        on_progress: Callable[[int], None] | None = None,
        on_log: Callable[[str], None] | None = None,
    ) -> None:
        self.url = url.strip()
        self.output_dir = Path(output_dir)
        self.fmt = normalize_format_label(fmt)
        self.video_quality = video_quality
        self.audio_quality = audio_quality
        self._on_progress = on_progress
        self._on_log = on_log
        self._cancelled = False
        self.output_path: str | None = None

    def request_cancel(self) -> None:
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled

    def _log(self, msg: str) -> None:
        logger.info("%s | %s", self.url, msg)
        if self._on_log:
            self._on_log(msg)

    def _final_failure(
        self,
        error: BaseException,
        user_message: str | None = None,
    ) -> tuple[bool, str, None]:
        label = (
            "Final yt-dlp error"
            if isinstance(error, DownloadError)
            else "Final download error"
        )
        logger.error(
            "%s domain=%s type=%s: %s",
            label,
            url_domain(self.url),
            type(error).__name__,
            str(error),
        )
        return False, user_message or map_error(error, url=self.url), None

    def run(self) -> tuple[bool, str, str | None]:
        if self._cancelled:
            return False, "Download cancelled.", None

        ffmpeg_info = resolve_ffmpeg()
        if needs_ffmpeg(self.fmt) and not ffmpeg_info.found:
            return False, FFMPEG_MISSING_MSG, None

        browsers = browsers_to_try(self.url)
        last_exc: BaseException | None = None
        youtube_auth_failures = 0

        for browser in browsers:
            if self._cancelled:
                return False, "Download cancelled.", None

            try:
                self._attempt_download(browser, ffmpeg_info)
                log_attempt(self.url, browser, True)
                return True, "Download complete.", self.output_path
            except DownloadCancelled:
                log_attempt(self.url, browser, False, "cancelled")
                return False, "Download cancelled.", None
            except DownloadError as e:
                last_exc = e
                if self._cancelled or isinstance(e.__cause__, DownloadCancelled):
                    return False, "Download cancelled.", None

                if is_cookie_db_locked(e):
                    log_attempt(
                        self.url, browser, False, "cookie DB locked, skipping browser"
                    )
                    continue

                if should_attempt_cookie_fallback(self.url, e):
                    youtube_auth_failures += 1
                    log_attempt(self.url, browser, False, str(e)[:200])
                    if browser == browsers[-1]:
                        break
                    continue

                log_attempt(self.url, browser, False, str(e)[:200])
                return self._final_failure(e)
            except TypeError as e:
                logger.exception("Invalid download configuration")
                return self._final_failure(e)
            except Exception as e:
                last_exc = e
                if self._cancelled:
                    return False, "Download cancelled.", None
                logger.exception("Unexpected download error")
                return self._final_failure(e)

        if (
            is_youtube_url_safe(self.url)
            and youtube_auth_failures > 0
            and browsers != (None,)
        ):
            assert last_exc is not None
            return self._final_failure(last_exc, YOUTUBE_BLOCKED_MSG)

        if last_exc is not None:
            return self._final_failure(last_exc)
        return False, "Download failed.", None

    def _attempt_download(self, browser: str | None, ffmpeg_info: FFmpegInfo) -> None:
        if self.fmt == FORMAT_MP3:
            self._log("Downloading audio...")
        else:
            self._log("Downloading...")

        opts = build_ydl_opts(
            output_dir=self.output_dir,
            fmt=self.fmt,
            video_quality=self.video_quality,
            audio_quality=self.audio_quality,
            ffmpeg_info=ffmpeg_info,
            cookies_browser=browser,
            on_progress=self._on_progress,
            is_cancelled=self.is_cancelled,
        )
        self._log_download_plan(opts, fallback=False)

        try:
            self._run_ydl(opts)
            return
        except DownloadError as e:
            if not is_format_unavailable_error(e):
                raise
            logger.warning(
                "Format selection failed url=%s domain=%s quality=%s selector=%s error=%s",
                self.url,
                url_domain(self.url),
                self.video_quality,
                opts.get("format"),
                str(e)[:300],
            )
            logger.warning(
                "Retrying once with generic fallback selector %s",
                GENERIC_FALLBACK_FORMAT,
            )
            self._log("Preferred format unavailable; retrying with automatic quality...")

        fallback_opts = build_ydl_opts(
            output_dir=self.output_dir,
            fmt=self.fmt,
            video_quality=self.video_quality,
            audio_quality=self.audio_quality,
            ffmpeg_info=ffmpeg_info,
            cookies_browser=browser,
            on_progress=self._on_progress,
            is_cancelled=self.is_cancelled,
            use_generic_fallback=True,
        )
        self._log_download_plan(fallback_opts, fallback=True)
        try:
            self._run_ydl(fallback_opts)
        except DownloadError as e:
            logger.error(
                "Fallback format selection also failed url=%s selector=%s error=%s",
                self.url,
                fallback_opts.get("format"),
                str(e)[:300],
            )
            raise

    def _log_download_plan(self, opts: dict, *, fallback: bool) -> None:
        logger.info(
            "Download start v-app domain=%s quality=%s fallback=%s %s",
            url_domain(self.url),
            self.video_quality,
            fallback,
            describe_format_plan(opts, self.video_quality, self.fmt),
        )
        logger.info("Destination directory: %s", self.output_dir)

    def _run_ydl(self, opts: dict) -> None:
        with yt_dlp.YoutubeDL(opts) as ydl:
            if self._cancelled:
                raise DownloadCancelled()
            info = ydl.extract_info(self.url, download=True)
            if self._cancelled:
                raise DownloadCancelled()

            if self.fmt == FORMAT_MP3:
                self._log("Converting to MP3...")
            elif self.fmt == FORMAT_M4A:
                self._log("Preparing M4A audio...")

            self.output_path = _resolve_output_path(
                ydl, info, self.output_dir, self.fmt
            )
            logger.info(
                "Download success url=%s output=%s",
                self.url,
                self.output_path,
            )


def is_youtube_url_safe(url: str) -> bool:
    from app.errors import is_youtube_url

    return is_youtube_url(url)
