"""
Optional YouTube smoke test. Not part of the default suite.

Run:
  set RUN_YOUTUBE_SMOKE=1
  python -m unittest tests.test_youtube_smoke
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

SMOKE_URL = "https://www.youtube.com/watch?v=LpMLDtejfvs"


@unittest.skipUnless(
    os.environ.get("RUN_YOUTUBE_SMOKE") == "1",
    "Set RUN_YOUTUBE_SMOKE=1 to run the live YouTube smoke test",
)
class YoutubeSmokeTest(unittest.TestCase):
    def test_download_sample_video(self):
        from app.downloader_worker import DownloaderWorker
        from app.formats import FORMAT_MP4

        with tempfile.TemporaryDirectory() as tmp:
            worker = DownloaderWorker(
                url=SMOKE_URL,
                output_dir=Path(tmp),
                fmt=FORMAT_MP4,
                video_quality="1080",
                audio_quality="Best",
            )
            success, message, output_path = worker.run()
            self.assertTrue(success, msg=message)
            self.assertIsNotNone(output_path)
            path = Path(output_path)
            self.assertTrue(path.is_file(), msg=f"missing output: {output_path}")
            self.assertGreater(path.stat().st_size, 10_000)
            self.assertNotIn("Requested format is not available", message)


if __name__ == "__main__":
    unittest.main()
