"""Download history persistence."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.paths import app_data_dir

logger = logging.getLogger("videodownloader")

MAX_ENTRIES = 500


def history_path() -> Path:
    return app_data_dir() / "history.json"


def _load_entries() -> list[dict]:
    path = history_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.warning("Failed to load history: %s", e)
        return []


def append_entry(
    *,
    url: str,
    fmt: str,
    resolution: str,
    output_path: str,
    status: str,
    audio_quality: str = "",
) -> None:
    entries = _load_entries()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "format": fmt,
        "resolution": resolution,
        "output_path": output_path,
        "status": status,
    }
    if audio_quality:
        entry["audio_quality"] = audio_quality
    entries.append(entry)
    entries = entries[-MAX_ENTRIES:]
    path = history_path()
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        tmp.replace(path)
    except Exception as e:
        logger.error("Failed to save history: %s", e)
