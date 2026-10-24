"""Sequential download queue with cancel and retry support."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot

from app.downloader_worker import DownloaderWorker
from app.errors import RATE_LIMITED_MSG
from app.formats import FORMAT_MP3, normalize_format_label
from app.history import append_entry

logger = logging.getLogger("videodownloader")


class JobStatus(str, Enum):
    PENDING = "Pending"
    DOWNLOADING = "Downloading"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


@dataclass
class DownloadJob:
    url: str
    row_index: int
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    message: str = ""
    output_path: str | None = None


class _WorkerThread(QThread):
    finished_result = Signal(bool, str, object)

    def __init__(self, worker: DownloaderWorker) -> None:
        super().__init__()
        self._worker = worker

    def run(self) -> None:
        success, message, path = self._worker.run()
        self.finished_result.emit(success, message, path)

    def request_cancel(self) -> None:
        self._worker.request_cancel()


class DownloadQueue(QObject):
    _worker_progress = Signal(int, int)
    log_line = Signal(str)
    job_started = Signal(int, str)
    job_progress = Signal(int, int)
    job_finished = Signal(int, bool, str, object)
    queue_finished = Signal()
    overall_progress = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._jobs: list[DownloadJob] = []
        self._batch_jobs: list[DownloadJob] = []
        self._pending: list[DownloadJob] = []
        self._current: DownloadJob | None = None
        self._thread: _WorkerThread | None = None
        self._output_dir = Path()
        self._fmt = "MP4 Video"
        self._video_quality = "720"
        self._audio_quality = "192 kbps"
        self._active = False
        self._cancel_requested = False
        self._batch_completed = 0
        self._worker_progress.connect(self._on_progress)

    @property
    def is_active(self) -> bool:
        return self._active

    def jobs(self) -> list[DownloadJob]:
        return list(self._jobs)

    def failed_jobs(self) -> list[DownloadJob]:
        return [j for j in self._jobs if j.status == JobStatus.FAILED]

    def clear_session(self) -> None:
        if self._active:
            return
        self._jobs.clear()
        self._batch_jobs.clear()
        self._pending.clear()
        self._current = None

    def start(
        self,
        job_specs: list[tuple[int, str]],
        output_dir: Path,
        fmt: str,
        video_quality: str,
        audio_quality: str,
    ) -> None:
        if self._active or not job_specs:
            return

        self._output_dir = output_dir
        self._fmt = normalize_format_label(fmt)
        self._video_quality = video_quality
        self._audio_quality = audio_quality
        self._cancel_requested = False
        self._batch_completed = 0

        new_jobs = [
            DownloadJob(url=url, row_index=row_index) for row_index, url in job_specs
        ]
        self._jobs.extend(new_jobs)
        self._batch_jobs = new_jobs
        self._pending = list(new_jobs)
        self._active = True
        self.overall_progress.emit(0)
        self._process_next()

    def retry_failed(
        self,
        output_dir: Path | None = None,
        fmt: str | None = None,
        video_quality: str | None = None,
        audio_quality: str | None = None,
    ) -> None:
        if self._active:
            return
        failed = [j for j in self._jobs if j.status == JobStatus.FAILED]
        if not failed:
            return
        if output_dir is not None:
            self._output_dir = output_dir
        if fmt is not None:
            self._fmt = normalize_format_label(fmt)
        if video_quality is not None:
            self._video_quality = video_quality
        if audio_quality is not None:
            self._audio_quality = audio_quality
        for j in failed:
            j.status = JobStatus.PENDING
            j.progress = 0
            j.message = ""
            j.output_path = None
        self._batch_jobs = list(failed)
        self._pending = list(failed)
        self._cancel_requested = False
        self._batch_completed = 0
        self._active = True
        self.overall_progress.emit(0)
        self._process_next()

    def cancel(self) -> None:
        self._cancel_requested = True
        if self._thread:
            self._thread.request_cancel()
        for job in self._pending:
            job.status = JobStatus.CANCELLED
            job.message = "Cancelled"
            self.job_finished.emit(job.row_index, False, "Cancelled", None)
        self._pending.clear()

    def wait_for_thread(self, ms: int = 5000) -> bool:
        if self._thread and self._thread.isRunning():
            return self._thread.wait(ms)
        return True

    @Slot()
    def _process_next(self) -> None:
        if self._cancel_requested and self._current is None:
            self._finish_queue()
            return

        if not self._pending:
            if self._thread and self._thread.isRunning():
                return
            self._finish_queue()
            return

        if self._thread and self._thread.isRunning():
            return

        job = self._pending.pop(0)
        self._current = job
        job.status = JobStatus.DOWNLOADING
        job.progress = 0
        self.job_started.emit(job.row_index, job.url)

        fmt_label = self._fmt
        if fmt_label == FORMAT_MP3:
            self.log_line.emit("Starting download (MP3)...")
        else:
            self.log_line.emit("Starting download...")

        worker = DownloaderWorker(
            url=job.url,
            output_dir=self._output_dir,
            fmt=self._fmt,
            video_quality=self._video_quality,
            audio_quality=self._audio_quality,
            on_progress=lambda p: self._worker_progress.emit(job.row_index, p),
            on_log=lambda m: self.log_line.emit(m),
        )

        self._thread = _WorkerThread(worker)
        self._thread.finished_result.connect(self._on_worker_finished)
        self._thread.start()

    @Slot(int, int)
    def _on_progress(self, row_index: int, percent: int) -> None:
        for job in self._jobs:
            if job.row_index == row_index:
                job.progress = percent
                break
        self.job_progress.emit(row_index, percent)
        self._emit_overall()

    def _emit_overall(self) -> None:
        total = len(self._batch_jobs)
        if total == 0:
            self.overall_progress.emit(0)
            return
        current_pct = 0
        if self._current and self._current in self._batch_jobs:
            current_pct = self._current.progress
        overall = int((self._batch_completed * 100 + current_pct) / total)
        self.overall_progress.emit(min(overall, 100))

    @Slot(bool, str, object)
    def _on_worker_finished(self, success: bool, message: str, output_path: object) -> None:
        thread = self._thread
        if thread is not None:
            # Result is emitted immediately before run returns; retain the native thread.
            thread.wait()
            thread.deleteLater()
        job = self._current
        if job is None:
            return

        path_str = str(output_path) if output_path else None

        cancelled = (
            self._cancel_requested
            or message == "Download cancelled."
            or (not success and message.strip().lower().startswith("download cancel"))
        )
        if cancelled:
            job.status = JobStatus.CANCELLED
            job.message = "Cancelled"
            job.progress = 0
            self.job_finished.emit(job.row_index, False, "Cancelled", None)
            self.log_line.emit("Cancelled.")
            self._current = None
            self._thread = None
            self._finish_queue()
            return

        if success:
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.message = "Completed"
            job.output_path = path_str
            self._batch_completed += 1
            history_saved = append_entry(
                url=job.url,
                fmt=self._fmt,
                resolution=self._video_quality,
                output_path=path_str or "",
                status="completed",
                audio_quality=self._audio_quality,
            )
            if history_saved is False:
                self.log_line.emit("Media saved; download history could not be updated. See the log file.")
            self.log_line.emit("Completed.")
        else:
            job.status = JobStatus.FAILED
            job.message = message
            job.progress = 0
            self.log_line.emit(f"Failed: {message}")

        self.job_finished.emit(job.row_index, success, message, path_str)
        self._current = None
        self._thread = None

        if not success and message == RATE_LIMITED_MSG:
            for pending in self._pending:
                pending.status = JobStatus.FAILED
                pending.message = "Not attempted: " + RATE_LIMITED_MSG
                self.job_finished.emit(pending.row_index, False, pending.message, None)
            self._pending.clear()
            self.log_line.emit("Source rate limit stopped further downloads. Wait before using Retry failed.")
            self._finish_queue()
        elif self._cancel_requested:
            self._finish_queue()
        else:
            self._emit_overall()
            self._process_next()

    def _finish_queue(self) -> None:
        self._active = False
        self._current = None
        if self._cancel_requested:
            self.log_line.emit("Downloads cancelled.")
        else:
            self.log_line.emit("Batch finished.")
        self.overall_progress.emit(100 if not self._cancel_requested else 0)
        self.queue_finished.emit()
