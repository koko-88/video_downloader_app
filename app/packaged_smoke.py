"""Explicit local diagnostic for both source and frozen Windows runtime."""
from __future__ import annotations

import json
import platform
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from app.captions import Cue, parse_captions
from app.config import Settings
from app.main_window import MainWindow
from app.transcript_batch import Choices, TranscriptBatch
from app.transcript_ui import TranscriptThread


def run(report_path: Path) -> int:
    report_path = report_path.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    report = dict(status='FAIL', frozen=bool(getattr(sys,'frozen',False)), executable=sys.executable,
                  windows=platform.win32_ver(), qt_platform=QGuiApplication.platformName())
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
            original_config_path=Settings.__dict__['config_path']
            Settings.config_path=classmethod(lambda cls:Path(temp)/'config.json')
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
            QTimer.singleShot(30000,lambda:(thread.request_cancel(),app.quit()))
            app.exec()
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
            window.grab().save(str(report_path.with_suffix('.png')))
            window.close(); app.processEvents()
            Settings.config_path=original_config_path
    except Exception as exc:
        report['error_type']=type(exc).__name__
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['status']=='PASS' else 1
