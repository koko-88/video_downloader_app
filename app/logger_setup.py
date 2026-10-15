"""Application logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.paths import logs_dir


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("videodownloader")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    log_file = logs_dir() / "app.log"

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
