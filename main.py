"""Video Downloader — application entry point."""

from __future__ import annotations

import logging
import sys
import traceback

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from app.logger_setup import setup_logging
from app.main_window import MainWindow


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    logging.getLogger("videodownloader").critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_tb),
    )
    traceback.print_exception(exc_type, exc_value, exc_tb)


def _dark_palette() -> QPalette:
    from PySide6.QtCore import Qt

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    return palette


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--smoke-report":
        from pathlib import Path
        from app.packaged_smoke import run
        return run(Path(sys.argv[2]))
    setup_logging()
    sys.excepthook = _excepthook

    app = QApplication(sys.argv)
    app.setApplicationName("Video Downloader")
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
