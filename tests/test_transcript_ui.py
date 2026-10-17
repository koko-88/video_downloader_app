import copy
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QThread, QTimer, Slot
from PySide6.QtWidgets import QApplication
from app.captions import Cue
from app.config import Settings
from app.download_queue import DownloadQueue, JobStatus
from app.formats import ALL_FORMATS
from app.main_window import MainWindow
from app.transcript_batch import Choices, TranscriptBatch
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
        self.assertEqual(panel.results.model().rowCount(),2); self.assertEqual(panel.results.model().index(0,1).data(),'succeeded')
        self.assertIn('exported 2',panel.summary.text()); self.assertEqual(panel.inputs.model().index(0,1).data(),'complete')
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

    def test_rate_limit_terminal_state_is_visible(self):
        panel=self.panel()
        data=dict(cancelled=False,halt_reason='rate_limited',inputs=[],videos={},
                  counts=dict(discovered=0,attempted=0,exported=0,caption_absent=0,
                              inaccessible=0,failed=0,pending=0))
        panel._finished_result(data)
        self.assertIn('Rate limited',panel.summary.text())

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
            window._append_log('<b>untrusted caption metadata</b>')
            self.assertIn('<b>untrusted caption metadata</b>',window.log_box.toPlainText())
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

    def test_download_progress_runs_on_gui_thread_and_pending_cancel_is_reported(self):
        observed=[]
        class Queue(DownloadQueue):
            @Slot(int,int)
            def _on_progress(self,row,percent):
                observed.append(QThread.currentThread())
                super()._on_progress(row,percent)
        class Worker:
            def __init__(self,**kwargs): self.options=kwargs; self.cancelled=False
            def request_cancel(self): self.cancelled=True
            def run(self):
                self.options['on_progress'](50)
                while not self.cancelled: time.sleep(.002)
                return False,'Download cancelled.',None
        with patch('app.download_queue.DownloaderWorker',Worker):
            queue=Queue(); finished=[]; done=[]
            queue.job_finished.connect(lambda row,*args:finished.append(row))
            queue.queue_finished.connect(lambda:done.append(True))
            queue.start([(0,'first'),(1,'queued')],self.root,'MP4 Video','720','Best')
            self.pump(lambda:bool(observed))
            queue.cancel(); self.pump(lambda:bool(done))
            self.assertEqual(set(finished),{0,1})
            self.assertTrue(all(t==self.app.thread() for t in observed))
            self.assertTrue(all(j.status==JobStatus.CANCELLED for j in queue.jobs()))

    def test_corrupt_download_settings_do_not_discard_valid_transcript_choices(self):
        import json
        cases=[dict(last_output_dir=['invalid']),dict(last_video_quality={'invalid':True}),
               dict(last_audio_quality=192),dict(last_format=['MP4']),
               dict(last_format='unknown'),dict(last_video_quality='999'),dict(last_audio_quality='bad')]
        config=self.root/'config.json'
        with patch.object(Settings,'config_path',return_value=config):
            for fields in cases:
                with self.subTest(fields=fields):
                    config.write_text(json.dumps(dict(transcript_language='ar',transcript_formats=['json'],**fields)),encoding='utf-8')
                    before=config.read_bytes(); settings=Settings.load()
                    self.assertEqual(settings.last_output_dir,'')
                    self.assertEqual(settings.last_format,'MP4 Video')
                    self.assertEqual(settings.last_video_quality,'720')
                    self.assertEqual(settings.last_audio_quality,'192 kbps')
                    self.assertEqual(settings.transcript_language,'ar')
                    self.assertEqual(settings.transcript_formats,['json'])
                    self.assertEqual(config.read_bytes(),before)

    def test_native_window_opens_with_malformed_download_preferences(self):
        import json
        config=self.root/'config.json'
        config.write_text(json.dumps(dict(last_output_dir=['invalid'],last_format='MP4 Video',
                                         last_video_quality=720,last_audio_quality={'bad':True})),encoding='utf-8')
        with patch.object(Settings,'config_path',return_value=config),patch.object(MainWindow,'_log_startup'):
            window=MainWindow()
            try:
                window.show(); self.app.processEvents()
                self.assertTrue(window.isVisible())
                self.assertEqual(window.video_quality_combo.currentText(),'720')
                self.assertEqual(window.audio_quality_combo.currentText(),'192 kbps')
            finally: window.close()

    def test_valid_legacy_download_preferences_are_preserved(self):
        import json
        config=self.root/'config.json'
        config.write_text(json.dumps(dict(last_output_dir=str(self.root/'مرحبا'),last_format='mp3',
                                         last_resolution='1080',last_audio_quality='Best',
                                         transcript_language='ar')),encoding='utf-8')
        with patch.object(Settings,'config_path',return_value=config):
            settings=Settings.load()
            self.assertEqual(settings.last_output_dir,str(self.root/'مرحبا'))
            self.assertEqual(settings.last_format,'MP3 Audio')
            self.assertEqual(settings.last_video_quality,'1080')
            self.assertEqual(settings.last_audio_quality,'Best')
            self.assertEqual(settings.transcript_language,'ar')

    def test_download_queue_stops_on_rate_limit_and_retries_only_on_explicit_action(self):
        from app.errors import RATE_LIMITED_MSG
        attempts={}
        root=self.root
        class Worker:
            def __init__(self,**kwargs): self.options=kwargs
            def request_cancel(self): pass
            def run(self):
                url=self.options['url']; attempts[url]=attempts.get(url,0)+1
                if url=='limited' and attempts[url]==1: return False,RATE_LIMITED_MSG,None
                return True,'Completed',str(root/'example.mp4')
        with patch('app.download_queue.DownloaderWorker',Worker),patch('app.download_queue.append_entry') as history:
            queue=DownloadQueue(); done=[]; rows=[]
            queue.queue_finished.connect(lambda:done.append(True))
            queue.job_finished.connect(lambda row,*args:rows.append(row))
            queue.start([(0,'limited'),(1,'next'),(2,'last')],self.root,'MP4 Video','720','Best')
            self.pump(lambda:len(done)==1)
            self.assertEqual(attempts,{'limited':1})
            self.assertEqual(set(rows),{0,1,2})
            self.assertTrue(all(j.status==JobStatus.FAILED for j in queue.jobs()))
            self.assertIn('Not attempted',queue.jobs()[1].message)
            history.assert_not_called()
            queue.retry_failed(); self.pump(lambda:len(done)==2)
            self.assertEqual(attempts,{'limited':2,'next':1,'last':1})
            self.assertTrue(all(j.status==JobStatus.COMPLETED for j in queue.jobs()))
            self.assertEqual(history.call_count,3)

    def test_mp3_quality_survives_settings_load_and_busy_state_changes(self):
        import json
        config=self.root/'config.json'
        for quality in ('Best','320 kbps','256 kbps','192 kbps','128 kbps'):
            with self.subTest(quality=quality):
                config.write_text(json.dumps(dict(last_format='MP3 Audio',last_audio_quality=quality)),encoding='utf-8')
                with patch.object(Settings,'config_path',return_value=config),patch.object(MainWindow,'_log_startup'):
                    window=MainWindow()
                    try:
                        self.assertEqual(window.audio_quality_combo.currentText(),quality)
                        window._set_busy(True); window._set_busy(False)
                        self.assertEqual(window.audio_quality_combo.currentText(),quality)
                        window._on_format_changed('MP3 Audio')
                        self.assertEqual(window.audio_quality_combo.currentText(),quality)
                    finally: window.close()

    def test_history_unavailable_does_not_stall_completed_download_queue(self):
        class Worker:
            def __init__(self,**kwargs): pass
            def request_cancel(self): pass
            def run(self): return True,'Completed','example.mp4'
        with patch('app.download_queue.DownloaderWorker',Worker),\
             patch('app.history.history_path',side_effect=PermissionError('fixture history unavailable')):
            queue=DownloadQueue(); done=[]; logs=[]
            queue.queue_finished.connect(lambda:done.append(True)); queue.log_line.connect(logs.append)
            queue.start([(0,'first'),(1,'second')],self.root,'MP4 Video','720','Best')
            self.pump(lambda:bool(done))
            self.assertTrue(all(job.status==JobStatus.COMPLETED for job in queue.jobs()))
            self.assertFalse(queue.is_active)
            self.assertTrue(any('history' in line.lower() for line in logs))

    def test_packaged_diagnostic_preserves_normal_preferences(self):
        from app.packaged_smoke import run
        sentinel=self.root/'normal-config.json'
        original=b'{"marker":"ordinary preferences must remain untouched"}'
        sentinel.write_bytes(original)
        with patch.object(Settings,'config_path',return_value=sentinel):
            self.assertEqual(run(self.root/'isolated-smoke.json'),0)
        self.assertEqual(sentinel.read_bytes(),original)

    def test_failed_packaged_diagnostic_preserves_normal_preferences(self):
        from app.packaged_smoke import run
        sentinel=self.root/'normal-config.json'
        original=b'{"marker":"ordinary preferences must remain untouched"}'
        for target in ('app.packaged_smoke.TranscriptThread','app.packaged_smoke.parse_captions'):
            with self.subTest(target=target):
                sentinel.write_bytes(original)
                with patch.object(Settings,'config_path',return_value=sentinel),\
                     patch(target,side_effect=RuntimeError('fixture diagnostic failure')):
                    self.assertEqual(run(self.root/'failed-isolated-smoke.json'),1)
                self.assertEqual(sentinel.read_bytes(),original)

    def test_large_transcript_results_display_updates_without_replacing_rows(self):
        panel=self.panel()
        records={str(i):dict(title='Video '+str(i),status='pending',track={},reason='') for i in range(10000)}
        data=dict(counts=dict(discovered=10000,attempted=0,exported=0,caption_absent=0,inaccessible=0,failed=0,pending=10000),
                  inputs=[dict(url='source',target='',state='complete',reason='')],videos=records)
        panel._update('Scanning',data)
        self.assertEqual(panel.results.model().rowCount(),10000)
        before=panel.results.model().index(9999,0)
        resets=[]; panel.results.model().modelReset.connect(lambda:resets.append(True))
        records['9999']['status']='succeeded'
        panel._update('Processed',data)
        self.assertEqual(before.data(),'Video 9999')
        self.assertEqual(panel.results.model().index(9999,1).data(),'succeeded')
        self.assertEqual(resets,[])

    def test_worker_update_volume_grows_with_changed_rows(self):
        from tests.test_transcript_batch import BASE,FixtureSource,video
        count=30
        urls=[BASE+str(i) for i in range(count)]
        FixtureSource.metadata={url:video(str(i)) for i,url in enumerate(urls)}
        FixtureSource.outcomes={}; FixtureSource.extracted=[]; FixtureSource.uncertainty=False; FixtureSource.on_caption=None
        def factory(*args,**kwargs): return TranscriptBatch(*args,**kwargs,source_factory=FixtureSource)
        thread=TranscriptThread(urls,self.root,Choices(),batch_factory=factory)
        transmitted=[]; results=[]
        thread.update.connect(lambda stage,data:transmitted.append(len(data.get('video_rows',data.get('videos',{})))))
        thread.result.connect(results.append)
        thread.start(); self.pump(lambda:not thread.isRunning() and bool(results))
        self.assertEqual(results[0]['counts']['succeeded'],count)
        self.assertLessEqual(sum(transmitted),6*count)
        thread.wait(); thread.deleteLater()
