"""Persistent application settings."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from app.formats import (
    DEFAULT_AUDIO_QUALITY,
    FORMAT_MP4,
    normalize_format_label,
)
from app.paths import app_data_dir

logger = logging.getLogger("videodownloader")


@dataclass
class Settings:
    last_output_dir: str = ""
    last_format: str = FORMAT_MP4
    last_video_quality: str = "720"
    last_audio_quality: str = DEFAULT_AUDIO_QUALITY

    @classmethod
    def config_path(cls) -> Path:
        return app_data_dir() / "config.json"

    @classmethod
    def load(cls) -> Settings:
        path = cls.config_path()
        if not path.is_file():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            fmt = normalize_format_label(data.get("last_format", FORMAT_MP4))
            return cls(
                last_output_dir=data.get("last_output_dir", ""),
                last_format=fmt,
                last_video_quality=data.get(
                    "last_video_quality",
                    data.get("last_resolution", "720"),
                ),
                last_audio_quality=data.get("last_audio_quality", DEFAULT_AUDIO_QUALITY),
            )
        except Exception as e:
            logger.warning("Failed to load config: %s", e)
            return cls()

    def save(self) -> None:
        path = self.config_path()
        tmp = path.with_suffix(".tmp")
        try:
            tmp.write_text(
                json.dumps(asdict(self), indent=2),
                encoding="utf-8",
            )
            tmp.replace(path)
        except Exception as e:
            logger.error("Failed to save config: %s", e)
