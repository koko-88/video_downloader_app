"""Explicit local diagnostic for both source and frozen Windows runtime."""
from __future__ import annotations

import json
import platform
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from app.captions import Cue, parse_captions
from app.config import Settings
from app.main_window import MainWindow
from app.download_queue import JobStatus
from app.errors import is_valid_url
from app.runtime_status import collect_runtime_status
import app.history as history
from app.transcript_batch import Choices, TranscriptBatch
from app.transcript_ui import TranscriptThread


def run(report_path: Path, download_url: str | None = None) -> int:
    report_path = report_path.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    report = dict(status='FAIL', frozen=bool(getattr(sys,'frozen',False)), executable=sys.executable,
                  windows=platform.win32_ver(), qt_platform=QGuiApplication.platformName(),
                  runtime=asdict(collect_runtime_status()))
    original_config_path=Settings.__dict__['config_path']
    original_history_path=history.history_path
    window=None
    class Source:
        def __init__(self,cancelled): self.log=SimpleNamespace(uncertain=False)
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def extract(self,url,ie_key=None):
            return dict(id='fixture',extractor_key='Youtube',title='Packaged مرحبا',webpage_url=url)
        def captions(self,*args):
            return [Cue(25,1250,'Packaged مرحبا')], dict(language='ar',kind='manual',representation='vtt',acquisition='captions')
    try:
        with tempfile.TemporaryDirectory(dir=report_path.parent) as temp:
            def factory(*args,**kwargs): return TranscriptBatch(*args,**kwargs,source_factory=Source)
            Settings.config_path=classmethod(lambda cls:Path(temp)/'config.json')
            history.history_path=lambda:Path(temp)/'history.json'
            try:
                window=MainWindow(); window.tabs.setCurrentIndex(1); window.show()
                panel=window.transcripts
                def thread_factory(*args,**kwargs):
                    thread=TranscriptThread(*args,**kwargs,batch_factory=factory)
                    thread.finished.connect(app.quit)
                    return thread
                panel.thread_factory=thread_factory
                panel.urls.setPlainText('https://youtube.com/watch?v=fixture')
                panel.folder.setText(temp); panel.language.setText('ar')
                for box in panel.formats.values(): box.setChecked(True)
                panel._start(); thread=panel._thread
                deadline=QTimer(); deadline.setSingleShot(True)
                deadline.timeout.connect(lambda:(thread.request_cancel(),app.quit()))
                deadline.start(30000)
                app.exec()
                deadline.stop()
                if panel._thread is not None and not panel._thread.wait(30000):
                    raise RuntimeError('Worker timeout')
                app.processEvents()
                if not panel._result or panel._result['counts']['succeeded'] != 1:
                    raise RuntimeError('Worker/export smoke failed')
                outputs=list(Path(temp).rglob('transcript.*'))
                if len(outputs)!=5: raise RuntimeError('Export count mismatch')
                for path in outputs:
                    if path.suffix in ('.vtt','.srt'):
                        if parse_captions(path.read_bytes(),path.suffix[1:]) != [Cue(25,1250,'Packaged مرحبا')]:
                            raise RuntimeError('Timed export roundtrip failed')
                report.update(status='PASS', output_formats=sorted(p.suffix for p in outputs),
                              counts=panel._result['counts'], tabs=[window.tabs.tabText(i) for i in range(window.tabs.count())])
                if download_url is not None:
                    if not is_valid_url(download_url) or report['runtime']['ffmpeg']=='not found':
                        raise RuntimeError('Live download input or runtime unavailable')
                    window.tabs.setCurrentIndex(0)
                    window.url_input.setPlainText(download_url)
                    window.path_input.setText(str(Path(temp)/'media'))
                    window.format_combo.setCurrentText('MP4 Video')
                    window.video_quality_combo.setCurrentText('360')
                    window._queue.queue_finished.connect(app.quit)
                    deadline.timeout.disconnect()
                    deadline.timeout.connect(lambda:(window._queue.cancel(),app.quit()))
                    deadline.start(180000)
                    window._start_download()
                    app.exec()
                    deadline.stop()
                    if not window._queue.wait_for_thread(35000):
                        raise RuntimeError('Live download cancellation timeout')
                    app.processEvents()
                    jobs=window._queue.jobs()
                    report['downloads']=[dict(status=job.status.value,message=job.message,
                                               bytes=Path(job.output_path).stat().st_size if job.output_path else 0)
                                         for job in jobs]
                    if len(jobs)!=1 or jobs[0].status!=JobStatus.COMPLETED:
                        raise RuntimeError('Live download failed')
                window.grab().save(str(report_path.with_suffix('.png')))
            finally:
                if window is not None:
                    window.close(); app.processEvents()
    except Exception as exc:
        report['status']='FAIL'
        report['error_type']=type(exc).__name__
    finally:
        Settings.config_path=original_config_path
        history.history_path=original_history_path
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['status']=='PASS' else 1
