import copy
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QThread, QTimer
from PySide6.QtWidgets import QApplication
from app.captions import Cue
from app.config import Settings
from app.download_queue import DownloadQueue, JobStatus
from app.formats import ALL_FORMATS
from app.main_window import MainWindow
from app.transcript_batch import TranscriptBatch
from app.transcript_source import Cancelled
from app.transcript_ui import TranscriptPanel, TranscriptThread


class UISource:
    def __init__(self,cancelled): self.cancelled=cancelled; self.log=type('Log',(),{'uncertain':False})()
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def extract(self,url,ie_key=None):
        time.sleep(0.02)
        if self.cancelled(): raise Cancelled()
        return dict(id=url.split('v=')[-1],extractor_key='Youtube',title='Unicode مرحبا',webpage_url=url)
    def captions(self,info,language,preference):
        time.sleep(0.04)
        if self.cancelled(): raise Cancelled()
        return [Cue(0,1000,'UI test')],dict(language=language,kind='manual',representation='vtt',acquisition='captions')


class QtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
    def pump(self,predicate,seconds=5):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            self.app.processEvents()
            if predicate(): return
            time.sleep(0.002)
        self.fail('Qt operation did not complete before bounded deadline')
    def panel(self):
        def batch_factory(*args,**kwargs): return TranscriptBatch(*args,**kwargs,source_factory=UISource)
        def thread_factory(*args,**kwargs): return TranscriptThread(*args,**kwargs,batch_factory=batch_factory)
        panel=TranscriptPanel(thread_factory=thread_factory)
        panel.urls.setPlainText('https://youtube.com/watch?v=a\nhttps://youtube.com/watch?v=b')
        panel.folder.setText(str(self.root)); panel.show(); self.addCleanup(panel.close)
        return panel

    def test_real_worker_keeps_event_loop_responsive_and_gui_slots(self):
        panel=self.panel(); ticks=[]; timer=QTimer(); timer.timeout.connect(lambda:ticks.append(1)); timer.start(5)
        observed=[]
        original=panel._update
        # Receiver remains QWidget's decorated slot; inspect resulting widget affinity too.
        panel._start(); thread=panel._thread
        thread.update.connect(lambda stage,data:observed.append(QThread.currentThread()))
        self.assertFalse(panel.start.isEnabled()); self.assertTrue(panel.cancel.isEnabled())
        self.pump(lambda:not panel.is_active); timer.stop()
        self.assertGreater(len(ticks),5)
        self.assertTrue(observed); self.assertTrue(all(t==self.app.thread() for t in observed))
        self.assertEqual(panel.results.rowCount(),2); self.assertEqual(panel.results.item(0,1).text(),'succeeded')
        self.assertIn('exported 2',panel.summary.text()); self.assertEqual(panel.inputs.item(0,1).text(),'complete')
        self.assertTrue(panel.start.isEnabled()); self.assertFalse(panel.cancel.isEnabled())
        self.assertTrue(panel.open_folder.isEnabled()); self.assertFalse(panel.retry.isEnabled())
        self.assertTrue(list(self.root.rglob('manifest.json')))
        self.assertEqual(panel.results.thread(),self.app.thread())

    def test_cancel_and_resume_controls_and_thread_lifetime(self):
        panel=self.panel(); panel._start(); thread=panel._thread
        QTimer.singleShot(10,panel.cancel_work)
        self.pump(lambda:not panel.is_active)
        self.assertIn('Cancelled',panel.summary.text()); self.assertTrue(panel.start.isEnabled())
        panel._start(); self.pump(lambda:not panel.is_active)
        self.assertIn('exported 2',panel.summary.text())

    def test_shutdown_refuses_to_destroy_running_thread(self):
        panel=self.panel(); panel._start()
        # Native request cannot finish immediately; caller must ignore its close event.
        finished=panel.shutdown(0)
        if not finished: self.assertIsNotNone(panel._thread)
        self.pump(lambda:not panel.is_active)
        self.assertTrue(panel.shutdown())

    def test_main_window_download_controls_and_settings_roundtrip(self):
        config=self.root/'config.json'
        with patch.object(Settings,'config_path',return_value=config), patch.object(MainWindow,'_log_startup'):
            window=MainWindow(); window.show()
            self.assertEqual(window.tabs.tabText(0),'Downloads'); self.assertEqual(window.tabs.tabText(1),'Transcripts')
            self.assertEqual([window.format_combo.itemText(i) for i in range(window.format_combo.count())],list(ALL_FORMATS))
            window.format_combo.setCurrentText('MP3 Audio'); window._on_format_changed(window.format_combo.currentText())
            self.assertTrue(window.audio_quality_combo.isEnabled())
            window._settings.transcript_language='ar'; window._settings.transcript_formats=['srt','json']
            window.close(); self.app.processEvents()
            loaded=Settings.load(); self.assertEqual(loaded.transcript_language,'ar'); self.assertEqual(loaded.transcript_formats,['srt','json'])

    def test_existing_download_queue_sequential_and_retry(self):
        attempts={}; history=[]
        class Worker:
            def __init__(self,**kwargs): self.options=kwargs; self.cancelled=False
            def request_cancel(self): self.cancelled=True
            def run(self):
                url=self.options['url']; attempts[url]=attempts.get(url,0)+1
                self.options['on_progress'](50); time.sleep(.01)
                if url=='bad' and attempts[url]==1: return False,'network error',None
                return True,'Completed',str(Path('example.mp4'))
        with patch('app.download_queue.DownloaderWorker',Worker), patch('app.download_queue.append_entry',side_effect=lambda **kw:history.append(kw)):
            queue=DownloadQueue(); done=[]; queue.queue_finished.connect(lambda:done.append(True))
            queue.start([(0,'good'),(1,'bad')],self.root,'MP4 Video','720','192 kbps')
            self.pump(lambda:len(done)==1)
            self.assertEqual([job.status for job in queue.jobs()],[JobStatus.COMPLETED,JobStatus.FAILED])
            queue.retry_failed(); self.pump(lambda:len(done)==2)
            self.assertTrue(all(job.status==JobStatus.COMPLETED for job in queue.jobs()))
            self.assertEqual(attempts,{'good':1,'bad':2}); self.assertEqual(len(history),2)
            self.assertTrue(queue.wait_for_thread())

    def test_corrupted_transcript_settings_fall_back_to_valid_values(self):
        import json
        config=self.root/'config.json'
        config.write_text(json.dumps(dict(transcript_formats=None,transcript_language=22,transcript_preference='bad',transcript_output_dir=[])),encoding='utf-8')
        with patch.object(Settings,'config_path',return_value=config):
            settings=Settings.load()
            self.assertEqual(settings.transcript_formats,['txt'])
            self.assertEqual(settings.transcript_language,'en')
            self.assertEqual(settings.transcript_preference,'manual-first')
            self.assertEqual(settings.transcript_output_dir,'')
