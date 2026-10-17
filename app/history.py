"""Download history persistence."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from app.paths import app_data_dir

logger = logging.getLogger("videodownloader")

MAX_ENTRIES = 500


def history_path() -> Path:
    return app_data_dir() / "history.json"


def _load_entries() -> list[dict] | None:
    try:
        data = json.loads(history_path().read_text(encoding="utf-8"))
        if not isinstance(data, list) or any(not isinstance(entry, dict) for entry in data):
            logger.warning("Invalid history preserved; no new entry appended")
            return None
        return data
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.warning("History preserved because it could not be read: %s", e)
        return None


def append_entry(
    *,
    url: str,
    fmt: str,
    resolution: str,
    output_path: str,
    status: str,
    audio_quality: str = "",
) -> bool:
    entries = _load_entries()
    if entries is None:
        return False
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
    name = None
    try:
        path = history_path()
        fd, name = tempfile.mkstemp(dir=path.parent, prefix=".history-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(entries, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        return True
    except Exception as e:
        logger.error("Failed to save history: %s", e)
        return False
    finally:
        if name is not None:
            try:
                Path(name).unlink(missing_ok=True)
            except OSError as e:
                logger.warning("Could not remove temporary history file: %s", e)
