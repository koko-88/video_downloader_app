"""Unit tests for centralized yt-dlp option building."""

from __future__ import annotations

import unittest
from pathlib import Path

from app.errors import (
    FORMAT_UNAVAILABLE_MSG,
    FFMPEG_FAILURE_MSG,
    NETWORK_ERROR_MSG,
    PERMISSION_ERROR_MSG,
    UNSUPPORTED_URL_MSG,
    VIDEO_UNAVAILABLE_MSG,
    is_format_unavailable_error,
    map_error,
)
from app.ffmpeg_resolver import FFmpegInfo
from app.formats import FORMAT_M4A, FORMAT_MP3, FORMAT_MP4, FORMAT_WEBM
from app.ydl_options import (
    DEFAULT_VIDEO_FORMAT,
    GENERIC_FALLBACK_FORMAT,
    YdlLogger,
    build_ydl_opts,
)


def _ffmpeg() -> FFmpegInfo:
    return FFmpegInfo(
        found=True,
        ffmpeg_path=Path("C:/ffmpeg/bin/ffmpeg.exe"),
        ffprobe_path=Path("C:/ffmpeg/bin/ffprobe.exe"),
        ffmpeg_dir=Path("C:/ffmpeg/bin"),
        source="test",
    )


class FormatSelectionTests(unittest.TestCase):
    def _opts(self, **kwargs):
        defaults = dict(
            output_dir=Path("C:/out"),
            fmt=FORMAT_MP4,
            video_quality="Best",
            audio_quality="192 kbps",
            ffmpeg_info=_ffmpeg(),
        )
        defaults.update(kwargs)
        return build_ydl_opts(**defaults)

    def test_best_quality_uses_native_selector(self):
        opts = self._opts(video_quality="Best")
        self.assertEqual(opts["format"], DEFAULT_VIDEO_FORMAT)
        self.assertNotIn("137", opts["format"])
        self.assertNotIn("140", opts["format"])
        self.assertNotIn("height=", opts["format"])
        self.assertTrue(any(s.startswith("vcodec:") for s in opts["format_sort"]))

    def test_1080p_prefers_max_resolution_not_exact_id(self):
        opts = self._opts(video_quality="1080")
        self.assertEqual(opts["format"], DEFAULT_VIDEO_FORMAT)
        self.assertIn("res:1080", opts["format_sort"])
        self.assertNotIn("height=1080", opts["format"])
        self.assertNotIn("137+140", opts["format"])

    def test_720p_preference(self):
        opts = self._opts(video_quality="720")
        self.assertIn("res:720", opts["format_sort"])
        self.assertEqual(opts["format"], "bv*+ba/b")

    def test_480p_preference(self):
        opts = self._opts(video_quality="480")
        self.assertIn("res:480", opts["format_sort"])

    def test_360p_preference(self):
        opts = self._opts(video_quality="360")
        self.assertIn("res:360", opts["format_sort"])

    def test_mp4_output_preference(self):
        opts = self._opts(fmt=FORMAT_MP4, video_quality="1080")
        self.assertEqual(opts["merge_output_format"], "mp4")
        self.assertIn("vcodec:h264", opts["format_sort"])
        self.assertIn("acodec:m4a", opts["format_sort"])

    def test_missing_exact_resolution_does_not_require_equals_filter(self):
        opts = self._opts(video_quality="1080")
        self.assertNotIn("height=", str(opts["format"]))
        self.assertTrue(any(item.startswith("res:") for item in opts["format_sort"]))

    def test_fallback_selection(self):
        opts = self._opts(video_quality="1080", use_generic_fallback=True)
        self.assertEqual(opts["format"], GENERIC_FALLBACK_FORMAT)
        self.assertEqual(GENERIC_FALLBACK_FORMAT, "bestvideo*+bestaudio/best")

    def test_webm_and_audio_modes(self):
        webm = self._opts(fmt=FORMAT_WEBM, video_quality="720")
        self.assertEqual(webm["merge_output_format"], "webm")
        mp3 = self._opts(fmt=FORMAT_MP3, video_quality="Best")
        self.assertEqual(mp3["format"], "bestaudio/best")
        self.assertEqual(mp3["postprocessors"][0]["key"], "FFmpegExtractAudio")
        m4a = self._opts(fmt=FORMAT_M4A, video_quality="Best")
        self.assertIn("bestaudio", m4a["format"])

    def test_paths_containing_spaces(self):
        opts = self._opts(output_dir=Path("C:/Users/Test User/My Videos"))
        self.assertIn("My Videos", opts["outtmpl"])
        self.assertIn("Test User", opts["outtmpl"])

    def test_unicode_filenames_template(self):
        opts = self._opts(output_dir=Path("C:/ダウンロード/видео"))
        self.assertIn("%(title).200B", opts["outtmpl"])
        self.assertFalse(opts["restrictfilenames"])
        self.assertIn("видео", opts["outtmpl"])

    def test_playlist_follows_existing_enabled_behavior(self):
        opts = self._opts()
        self.assertFalse(opts["noplaylist"])

    def test_retries_not_disabled(self):
        opts = self._opts()
        self.assertGreaterEqual(opts["retries"], 10)
        self.assertGreaterEqual(opts["fragment_retries"], 10)
        self.assertGreaterEqual(opts["socket_timeout"], 20)

    def test_no_none_values(self):
        opts = self._opts()
        for key, val in opts.items():
            self.assertIsNotNone(val, key)


class ErrorHandlingTests(unittest.TestCase):
    def test_format_selection_error(self):
        exc = Exception(
            "ERROR: [youtube] LpMLDtejfvs: Requested format is not available. "
            "Use --list-formats for a list of available formats"
        )
        self.assertTrue(is_format_unavailable_error(exc))
        self.assertEqual(map_error(exc), FORMAT_UNAVAILABLE_MSG)

    def test_unsupported_url(self):
        self.assertEqual(
            map_error(Exception("Unsupported URL: https://example.invalid/x")),
            UNSUPPORTED_URL_MSG,
        )

    def test_private_video(self):
        self.assertEqual(
            map_error(Exception("Private video. Sign in if you have access")),
            VIDEO_UNAVAILABLE_MSG,
        )

    def test_network_timeout(self):
        self.assertEqual(map_error(Exception("The read operation timed out")), NETWORK_ERROR_MSG)

    def test_ffmpeg_failure(self):
        self.assertEqual(
            map_error(Exception("ERROR: Postprocessing: Error merging with ffmpeg")),
            FFMPEG_FAILURE_MSG,
        )

    def test_permission(self):
        self.assertEqual(map_error(Exception("Permission denied: C:/out")), PERMISSION_ERROR_MSG)


class LoggerSafetyTests(unittest.TestCase):
    def test_strips_signed_media_urls(self):
        ydl_logger = YdlLogger()
        self.assertIsNone(
            ydl_logger._safe("https://googlevideo.com/videoplayback?signature=abc")
        )
        self.assertIsNotNone(ydl_logger._safe("[debug] Using ffmpeg"))


class RuntimeStatusTests(unittest.TestCase):
    def test_reports_yt_dlp_and_python_runtime_paths(self):
        import sys

        import yt_dlp

        from app.runtime_status import collect_runtime_status

        status = collect_runtime_status()
        self.assertEqual(status.ytdlp_version, yt_dlp.version.__version__)
        self.assertEqual(status.ytdlp_path, yt_dlp.__file__)
        self.assertEqual(status.python_executable, sys.executable)
        self.assertEqual(status.ytdlp_runtime, "Python package")


class FallbackWorkerTests(unittest.TestCase):
    def test_worker_retries_once_on_format_error(self):
        from unittest.mock import patch

        from yt_dlp.utils import DownloadError

        from app.downloader_worker import DownloaderWorker

        calls: list[str] = []

        class FakeYDL:
            def __init__(self, opts):
                self.opts = opts

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def extract_info(self, url, download=True):
                calls.append(self.opts["format"])
                if self.opts["format"] == DEFAULT_VIDEO_FORMAT:
                    raise DownloadError("Requested format is not available")
                return {"id": "abc", "title": "t", "requested_downloads": []}

            def prepare_filename(self, info):
                return str(Path("C:/out") / "t [abc].mp4")

        ffmpeg = _ffmpeg()
        worker = DownloaderWorker(
            url="https://www.youtube.com/watch?v=LpMLDtejfvs",
            output_dir=Path("C:/out"),
            fmt=FORMAT_MP4,
            video_quality="1080",
            audio_quality="Best",
        )
        with (
            patch("app.downloader_worker.resolve_ffmpeg", return_value=ffmpeg),
            patch("app.downloader_worker.needs_ffmpeg", return_value=False),
            patch("app.downloader_worker.yt_dlp.YoutubeDL", FakeYDL),
            patch("app.downloader_worker.browsers_to_try", return_value=(None,)),
        ):
            success, message, _path = worker.run()

        self.assertEqual(calls, [DEFAULT_VIDEO_FORMAT, GENERIC_FALLBACK_FORMAT])
        self.assertTrue(success)
        self.assertEqual(message, "Download complete.")

    def test_worker_does_not_retry_non_format_errors(self):
        from unittest.mock import patch

        from yt_dlp.utils import DownloadError

        from app.downloader_worker import DownloaderWorker

        class FakeYDL:
            def __init__(self, opts):
                self.opts = opts

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def extract_info(self, url, download=True):
                raise DownloadError("The read operation timed out")

        ffmpeg = _ffmpeg()
        worker = DownloaderWorker(
            url="https://www.youtube.com/watch?v=LpMLDtejfvs",
            output_dir=Path("C:/out"),
            fmt=FORMAT_MP4,
            video_quality="Best",
            audio_quality="Best",
        )
        with self.assertLogs("videodownloader", level="ERROR") as captured:
            with (
                patch("app.downloader_worker.resolve_ffmpeg", return_value=ffmpeg),
                patch("app.downloader_worker.needs_ffmpeg", return_value=False),
                patch("app.downloader_worker.yt_dlp.YoutubeDL", FakeYDL),
                patch("app.downloader_worker.browsers_to_try", return_value=(None,)),
            ):
                success, message, _path = worker.run()

        self.assertFalse(success)
        self.assertEqual(message, NETWORK_ERROR_MSG)
        self.assertIn("Final yt-dlp error", "\n".join(captured.output))
        self.assertIn("The read operation timed out", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
