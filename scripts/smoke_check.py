#!/usr/bin/env python3
"""Internal smoke test for FFmpeg resolution and yt-dlp options."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _check_opts(label: str, opts: dict) -> None:
    print(f"\n--- {label} ---")
    if "ffmpeg_location" in opts:
        loc = opts["ffmpeg_location"]
        print(f"ffmpeg_location: {loc!r} (type={type(loc).__name__})")
        assert isinstance(loc, str), f"ffmpeg_location must be str, got {type(loc)}"
        assert "object at 0x" not in repr(loc)
    else:
        print("ffmpeg_location: (not set)")

    if "postprocessors" in opts:
        for pp in opts["postprocessors"]:
            pq = pp.get("preferredquality")
            print(f"postprocessor: {pp.get('preferredcodec')} quality={pq!r}")

    print(f"format: {opts.get('format', '')[:80]}...")

    for key, val in opts.items():
        if val is None:
            raise AssertionError(f"opts[{key!r}] is None")
        if repr(val).startswith("<object object"):
            raise AssertionError(f"opts[{key!r}] is object(): {val!r}")


def main() -> int:
    from app.ffmpeg_resolver import FFmpegInfo, resolve_ffmpeg
    from app.formats import FORMAT_M4A, FORMAT_MP3, FORMAT_MP4, FORMAT_WEBM
    from app.ydl_options import build_ydl_opts

    print("=== smoke_check ===")
    info = resolve_ffmpeg()
    print(f"found={info.found} source={info.source}")
    print(f"type(ffmpeg_dir)={type(info.ffmpeg_dir).__name__} dir={info.ffmpeg_dir}")

    assert isinstance(info, FFmpegInfo)
    out = ROOT / "data" / "smoke_test_output"
    out.mkdir(parents=True, exist_ok=True)

    cases = [
        ("MP4 Best", FORMAT_MP4, "Best", "192 kbps"),
        ("MP4 720", FORMAT_MP4, "720", "192 kbps"),
        ("WEBM Best", FORMAT_WEBM, "Best", "Best"),
        ("WEBM 1080", FORMAT_WEBM, "1080", "Best"),
        ("MP3 Best", FORMAT_MP3, "Best", "Best"),
        ("MP3 320", FORMAT_MP3, "Best", "320 kbps"),
        ("MP3 256", FORMAT_MP3, "Best", "256 kbps"),
        ("MP3 192", FORMAT_MP3, "Best", "192 kbps"),
        ("MP3 128", FORMAT_MP3, "Best", "128 kbps"),
        ("M4A Best", FORMAT_M4A, "Best", "Best"),
    ]

    for label, fmt, vq, aq in cases:
        opts = build_ydl_opts(
            output_dir=out,
            fmt=fmt,
            video_quality=vq,
            audio_quality=aq,
            ffmpeg_info=info,
        )
        _check_opts(label, opts)

    print("\n=== PASS ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
