"""Main application window."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QMovie, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.config import Settings
from app.download_queue import DownloadQueue, JobStatus
from app.errors import FFMPEG_MISSING_MSG, is_valid_url
from app.formats import (
    ALL_FORMATS,
    AUDIO_QUALITIES,
    DEFAULT_AUDIO_QUALITY,
    FORMAT_M4A,
    FORMAT_MP3,
    is_audio_format,
    is_video_format,
    normalize_format_label,
    VIDEO_QUALITIES,
)
from app.ffmpeg_resolver import needs_ffmpeg, resolve_ffmpeg
from app.paths import ensure_dir, logs_dir, optional_resource
from app.privacy import redact

logger = logging.getLogger("videodownloader")

STATUS_COLORS = {
    JobStatus.PENDING: QColor(180, 180, 180),
    JobStatus.DOWNLOADING: QColor(255, 193, 7),
    JobStatus.COMPLETED: QColor(76, 175, 80),
    JobStatus.FAILED: QColor(244, 67, 54),
    JobStatus.CANCELLED: QColor(255, 152, 0),
}


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._settings = Settings.load()
        self._queue = DownloadQueue()
        self._last_success_folder: Path | None = None
        self._busy_cursor = False
        self._display_counter = 0

        self.setWindowTitle("Video Downloader")
        self.setMinimumSize(720, 600)

        self._apply_window_icon()
        self._build_ui()
        self._connect_signals()
        self._load_settings()
        self._log_startup()

    def _apply_window_icon(self) -> None:
        icon_path = optional_resource("resources/icon.ico")
        if icon_path:
            from PySide6.QtGui import QIcon

            self.setWindowIcon(QIcon(str(icon_path)))

    def _build_ui(self) -> None:
        from app.transcript_ui import TranscriptPanel

        outer = QVBoxLayout(self)
        self.tabs = QTabWidget()
        downloads = QWidget()
        layout = QVBoxLayout(downloads)
        self.transcripts = TranscriptPanel(self._settings)
        self.tabs.addTab(downloads, "Downloads")
        self.tabs.addTab(self.transcripts, "Transcripts")
        outer.addWidget(self.tabs)

        layout.addWidget(QLabel("Video URLs (one per line):"))
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText(
            "Paste one or more http:// or https:// links, each on a new line"
        )
        self.url_input.setFixedHeight(90)
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel("Download folder:"))
        folder_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(self.path_input)
        folder_row.addWidget(self.browse_btn)
        layout.addLayout(folder_row)

        opts_row = QHBoxLayout()
        opts_row.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(list(ALL_FORMATS))
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        opts_row.addWidget(self.format_combo)

        self.video_quality_label = QLabel("Video Quality:")
        opts_row.addWidget(self.video_quality_label)
        self.video_quality_combo = QComboBox()
        self.video_quality_combo.addItems(list(VIDEO_QUALITIES))
        opts_row.addWidget(self.video_quality_combo)

        self.audio_quality_label = QLabel("Audio Quality:")
        opts_row.addWidget(self.audio_quality_label)
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(list(AUDIO_QUALITIES))
        opts_row.addWidget(self.audio_quality_combo)
        opts_row.addStretch()
        layout.addLayout(opts_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        status_header = QHBoxLayout()
        status_header.addWidget(QLabel("Download status:"))
        status_header.addStretch()
        self.clear_list_btn = QPushButton("Clear list")
        self.clear_list_btn.clicked.connect(self._clear_list)
        status_header.addWidget(self.clear_list_btn)
        layout.addLayout(status_header)

        self.status_table = QTableWidget(0, 4)
        self.status_table.setHorizontalHeaderLabels(["#", "URL", "Status", "Progress"])
        self.status_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.status_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.status_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.status_table)

        layout.addWidget(QLabel("Activity:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(120)
        layout.addWidget(self.log_box)

        self.loader_label = QLabel()
        self.loader_label.hide()
        self._loader_movie: QMovie | None = None
        gif_path = optional_resource("resources/loader.gif")
        if gif_path:
            self._loader_movie = QMovie(str(gif_path))
            self.loader_label.setMovie(self._loader_movie)
            layout.addWidget(self.loader_label)

        btn_row = QHBoxLayout()
        self.download_btn = QPushButton("Download")
        self.cancel_btn = QPushButton("Cancel")
        self.retry_btn = QPushButton("Retry failed")
        self.open_folder_btn = QPushButton("Open folder")
        self.open_log_btn = QPushButton("Open log file")
        self.cancel_btn.setEnabled(False)
        self.retry_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(False)

        self.download_btn.clicked.connect(self._start_download)
        self.cancel_btn.clicked.connect(self._cancel_download)
        self.retry_btn.clicked.connect(self._retry_failed)
        self.open_folder_btn.clicked.connect(self._open_folder)
        self.open_log_btn.clicked.connect(self._open_log_file)

        btn_row.addWidget(self.download_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.retry_btn)
        btn_row.addWidget(self.open_folder_btn)
        btn_row.addWidget(self.open_log_btn)
        layout.addLayout(btn_row)

    def _connect_signals(self) -> None:
        q = self._queue
        q.log_line.connect(self._append_log)
        q.job_started.connect(self._on_job_started)
        q.job_progress.connect(self._on_job_progress)
        q.job_finished.connect(self._on_job_finished)
        q.overall_progress.connect(self.progress_bar.setValue)
        q.queue_finished.connect(self._on_queue_finished)

    def _load_settings(self) -> None:
        s = self._settings
        if s.last_output_dir:
            self.path_input.setText(s.last_output_dir)
        idx = self.format_combo.findText(normalize_format_label(s.last_format))
        if idx >= 0:
            self.format_combo.setCurrentIndex(idx)
        idx = self.video_quality_combo.findText(s.last_video_quality)
        if idx >= 0:
            self.video_quality_combo.setCurrentIndex(idx)
        idx = self.audio_quality_combo.findText(s.last_audio_quality)
        if idx >= 0:
            self.audio_quality_combo.setCurrentIndex(idx)
        self._on_format_changed(self.format_combo.currentText())

    def _log_startup(self) -> None:
        from app.runtime_status import collect_runtime_status

        info = resolve_ffmpeg()
        status = collect_runtime_status()
        mode = "installed" if getattr(sys, "frozen", False) else "dev"
        logger.info("Application started v%s mode=%s", __version__, mode)
        logger.info("Application executable: %s", sys.executable)
        logger.info("Python executable: %s", status.python_executable)
        logger.info("Data folder: %s", Settings.config_path().parent)
        logger.info("yt-dlp runtime: %s", status.ytdlp_runtime)
        logger.info("yt-dlp version: %s", status.ytdlp_version)
        logger.info("yt-dlp package path: %s", status.ytdlp_path)
        logger.info("yt-dlp-ejs: %s", status.ytdlp_ejs)
        logger.info("JS runtime: %s", status.js_runtime)
        if info.found:
            logger.info("FFmpeg (%s): %s", info.source, info.ffmpeg_path)
            logger.info("ffprobe: %s", info.ffprobe_path)
        else:
            logger.info("FFmpeg: not found")

        self._append_log("Ready. Paste a link and click Download.")

    def _on_format_changed(self, fmt: str) -> None:
        fmt = normalize_format_label(fmt)
        show_video = is_video_format(fmt)
        show_audio = is_audio_format(fmt)

        self.video_quality_label.setVisible(show_video)
        self.video_quality_combo.setVisible(show_video)
        self.video_quality_combo.setEnabled(show_video)

        self.audio_quality_label.setVisible(show_audio)
        self.audio_quality_combo.setVisible(show_audio)

        if fmt == FORMAT_M4A:
            self.audio_quality_combo.clear()
            self.audio_quality_combo.addItems(["Best"])
            self.audio_quality_combo.setEnabled(False)
        elif fmt == FORMAT_MP3:
            audio_quality = self.audio_quality_combo.currentText()
            self.audio_quality_combo.clear()
            self.audio_quality_combo.addItems(list(AUDIO_QUALITIES))
            self.audio_quality_combo.setEnabled(True)
            if self.audio_quality_combo.findText(audio_quality) < 0:
                audio_quality = DEFAULT_AUDIO_QUALITY
            self.audio_quality_combo.setCurrentText(audio_quality)
        else:
            self.audio_quality_combo.setEnabled(False)

    def _browse_folder(self) -> None:
        start = self.path_input.text().strip() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Select download folder", start)
        if folder:
            self.path_input.setText(folder)
            self._settings.last_output_dir = folder
            self._settings.save()

    def _parse_urls(self) -> list[str]:
        lines = self.url_input.toPlainText().strip().splitlines()
        return [u.strip() for u in lines if u.strip()]

    def _validate_inputs(self) -> tuple[list[str], Path] | None:
        urls = self._parse_urls()
        if not urls:
            QMessageBox.warning(self, "Input required", "Enter at least one URL.")
            return None

        invalid = [u for u in urls if not is_valid_url(u)]
        if invalid:
            QMessageBox.warning(
                self,
                "Invalid URL",
                "Each link must start with http:// or https://\n\n"
                + "\n".join(invalid[:5]),
            )
            return None

        folder_text = self.path_input.text().strip()
        if not folder_text:
            QMessageBox.warning(self, "Input required", "Choose a download folder.")
            return None

        folder = Path(folder_text)
        try:
            ensure_dir(folder)
        except OSError:
            QMessageBox.warning(self, "Folder error", "Cannot create or access that folder.")
            return None

        if not os.access(folder, os.W_OK):
            QMessageBox.warning(self, "Folder error", "Cannot write to the selected folder.")
            return None

        fmt = self.format_combo.currentText()
        if needs_ffmpeg(fmt) and not resolve_ffmpeg().found:
            QMessageBox.warning(self, "FFmpeg required", FFMPEG_MISSING_MSG)
            return None

        return urls, folder

    def _append_table_rows(self, urls: list[str]) -> list[tuple[int, str]]:
        specs: list[tuple[int, str]] = []
        for url in urls:
            row = self.status_table.rowCount()
            self.status_table.insertRow(row)
            self._display_counter += 1
            self.status_table.setItem(row, 0, QTableWidgetItem(str(self._display_counter)))
            display = url if len(url) <= 80 else url[:77] + "..."
            item_url = QTableWidgetItem(display)
            item_url.setToolTip(url)
            self.status_table.setItem(row, 1, item_url)
            self._set_status_cell(row, JobStatus.PENDING, 0)
            specs.append((row, url))
        return specs

    def _start_download(self) -> None:
        if self._queue.is_active:
            return

        validated = self._validate_inputs()
        if not validated:
            return

        urls, folder = validated
        fmt = self.format_combo.currentText()
        video_quality = self.video_quality_combo.currentText()
        audio_quality = self.audio_quality_combo.currentText()

        self._settings.last_output_dir = str(folder)
        self._settings.last_format = fmt
        self._settings.last_video_quality = video_quality
        self._settings.last_audio_quality = audio_quality
        self._settings.save()

        job_specs = self._append_table_rows(urls)
        self._set_busy(True)
        self.progress_bar.setValue(0)
        self._last_success_folder = folder

        self._queue.start(
            job_specs,
            folder,
            fmt,
            video_quality,
            audio_quality,
        )

    def _set_status_cell(self, row: int, status: JobStatus, progress: int) -> None:
        if row < 0 or row >= self.status_table.rowCount():
            return
        status_item = QTableWidgetItem(status.value)
        color = STATUS_COLORS.get(status, QColor(200, 200, 200))
        status_item.setForeground(color)
        self.status_table.setItem(row, 2, status_item)
        prog_item = QTableWidgetItem(f"{progress}%")
        prog_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_table.setItem(row, 3, prog_item)

    def _on_job_started(self, row_index: int, url: str) -> None:
        self._set_status_cell(row_index, JobStatus.DOWNLOADING, 0)
        self._append_log("Downloading...")

    def _on_job_progress(self, row_index: int, percent: int) -> None:
        status_item = self.status_table.item(row_index, 2)
        if status_item:
            status_item.setText(JobStatus.DOWNLOADING.value)
        prog = self.status_table.item(row_index, 3)
        if prog:
            prog.setText(f"{percent}%")

    def _on_job_finished(
        self, row_index: int, success: bool, message: str, output_path: object
    ) -> None:
        if message == "Cancelled":
            self._set_status_cell(row_index, JobStatus.CANCELLED, 0)
        elif success:
            self._set_status_cell(row_index, JobStatus.COMPLETED, 100)
            if output_path:
                self._last_success_folder = Path(str(output_path)).parent
            self.open_folder_btn.setEnabled(True)
        else:
            self._set_status_cell(row_index, JobStatus.FAILED, 0)
            status_item = self.status_table.item(row_index, 2)
            if status_item:
                status_item.setToolTip(message)

    def _on_queue_finished(self) -> None:
        self._set_busy(False)
        has_failed = any(j.status == JobStatus.FAILED for j in self._queue.jobs())
        self.retry_btn.setEnabled(has_failed)

        for job in self._queue.jobs():
            if job.status == JobStatus.PENDING:
                self._set_status_cell(job.row_index, JobStatus.CANCELLED, 0)

    def _clear_list(self) -> None:
        if self._queue.is_active:
            QMessageBox.information(
                self,
                "Busy",
                "Wait until the current download batch finishes.",
            )
            return
        self.status_table.setRowCount(0)
        self._display_counter = 0
        self._queue.clear_session()
        self.retry_btn.setEnabled(False)
        self.progress_bar.setValue(0)

    def _cancel_download(self) -> None:
        self._queue.cancel()
        self.cancel_btn.setEnabled(False)

    def _retry_failed(self) -> None:
        if self._queue.is_active:
            return
        failed = self._queue.failed_jobs()
        if not failed:
            return

        folder_text = self.path_input.text().strip()
        if not folder_text:
            QMessageBox.warning(self, "Input required", "Choose a download folder.")
            return

        folder = Path(folder_text)
        fmt = self.format_combo.currentText()
        if needs_ffmpeg(fmt) and not resolve_ffmpeg().found:
            QMessageBox.warning(self, "FFmpeg required", FFMPEG_MISSING_MSG)
            return

        for job in failed:
            self._set_status_cell(job.row_index, JobStatus.PENDING, 0)

        self._set_busy(True)
        self.progress_bar.setValue(0)
        self._queue.retry_failed(
            output_dir=folder,
            fmt=fmt,
            video_quality=self.video_quality_combo.currentText(),
            audio_quality=self.audio_quality_combo.currentText(),
        )

    def _open_folder(self) -> None:
        path = self._last_success_folder or Path(self.path_input.text().strip())
        if path.is_dir():
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            QMessageBox.information(self, "Open folder", "No download folder available yet.")

    def _open_log_file(self) -> None:
        log_file = logs_dir() / "app.log"
        if log_file.is_file():
            os.startfile(log_file)  # type: ignore[attr-defined]
        else:
            QMessageBox.information(
                self,
                "Log file",
                f"No log file yet.\nExpected:\n{log_file}",
            )

    def _set_busy(self, busy: bool) -> None:
        self.download_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.clear_list_btn.setEnabled(not busy)
        self.url_input.setEnabled(not busy)
        self.path_input.setEnabled(not busy)
        self.browse_btn.setEnabled(not busy)
        self.format_combo.setEnabled(not busy)

        fmt = self.format_combo.currentText()
        if busy:
            self.video_quality_combo.setEnabled(False)
            self.audio_quality_combo.setEnabled(False)
        else:
            self._on_format_changed(fmt)

        if busy:
            if self._loader_movie:
                self.loader_label.show()
                self._loader_movie.start()
            else:
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                self._busy_cursor = True
        else:
            if self._loader_movie:
                self._loader_movie.stop()
                self.loader_label.hide()
            if self._busy_cursor:
                QApplication.restoreOverrideCursor()
                self._busy_cursor = False

    def _append_log(self, text: str) -> None:
        self.log_box.moveCursor(QTextCursor.MoveOperation.End)
        self.log_box.insertPlainText(redact(text) + '\n')

    def closeEvent(self, event) -> None:  # noqa: N802
        if not self.transcripts.shutdown():
            event.ignore()
            self.transcripts.summary.setText("Cancelling; close again after the current request finishes.")
            return
        if self._queue.is_active:
            self._queue.cancel()
            if not self._queue.wait_for_thread(100):
                event.ignore()
                return
        self._settings.last_output_dir = self.path_input.text().strip()
        self._settings.last_format = self.format_combo.currentText()
        self._settings.last_video_quality = self.video_quality_combo.currentText()
        self._settings.last_audio_quality = self.audio_quality_combo.currentText()
        self._settings.save()
        super().closeEvent(event)
