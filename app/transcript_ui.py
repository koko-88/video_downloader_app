"""Transcript desktop controls and a worker whose lifetime follows native QThread finish."""
from __future__ import annotations

import copy
import os
import threading
from pathlib import Path

from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QHeaderView,
                               QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton,
                               QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)

from app.captions import FORMATS
from app.transcript_batch import Choices, TranscriptBatch
from app.transcript_source import SourceError


class TranscriptThread(QThread):
    update = Signal(str, object)
    result = Signal(object)
    error = Signal(str)

    def __init__(self, urls, folder, choices, retry=False, batch_factory=TranscriptBatch, parent=None):
        super().__init__(parent)
        self.urls, self.folder, self.choices, self.retry = urls, folder, choices, retry
        self.batch_factory = batch_factory
        self.cancelled = threading.Event()
        self.output_root = None

    def request_cancel(self):
        self.cancelled.set()

    def run(self):
        try:
            batch = self.batch_factory(self.urls, self.folder, choices=self.choices,
                                       cancelled=self.cancelled.is_set,
                                       progress=lambda stage, data: self.update.emit(stage, copy.deepcopy(data)))
            self.output_root = batch.root
            self.result.emit(batch.run(retry_failed=self.retry))
        except SourceError as exc:
            self.error.emit(exc.reason)
        except (OSError, ValueError):
            self.error.emit('Cannot access output folder or valid manifest; existing files preserved.')
        except Exception:
            self.error.emit('Transcript processing failed; inspect the preserved manifest and retry.')


class TranscriptPanel(QWidget):
    def __init__(self, settings=None, thread_factory=TranscriptThread):
        super().__init__()
        self.settings, self.thread_factory = settings, thread_factory
        self._thread = None
        self._result = None
        self._output_root = None
        self._run_identity = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Video, playlist or channel URLs (one per line):'))
        self.urls = QTextEdit(); self.urls.setMaximumHeight(80)
        self.urls.setPlaceholderText('Supported media links; bare YouTube channels scan the Videos tab')
        layout.addWidget(self.urls)
        row = QHBoxLayout(); self.folder = QLineEdit(); self.browse = QPushButton('Browse')
        row.addWidget(QLabel('Export folder:')); row.addWidget(self.folder); row.addWidget(self.browse)
        self.browse.clicked.connect(self._browse); layout.addLayout(row)
        row = QHBoxLayout(); self.language = QLineEdit('en'); self.language.setMaximumWidth(130)
        self.language.setToolTip('Exact language code offered by the source, e.g. en, ar, en-US. No implicit language fallback.')
        self.preference = QComboBox(); self.preference.addItems(['manual-first','auto-first','manual-only','auto-only'])
        row.addWidget(QLabel('Language:')); row.addWidget(self.language)
        row.addWidget(QLabel('Track preference:')); row.addWidget(self.preference); row.addStretch(); layout.addLayout(row)
        row = QHBoxLayout(); row.addWidget(QLabel('Export formats:')); self.formats = {}
        for fmt in FORMATS:
            box = QCheckBox(fmt.upper()); box.setChecked(fmt == 'txt'); self.formats[fmt] = box; row.addWidget(box)
        row.addStretch(); layout.addLayout(row)
        self.asr = QCheckBox('Try local speech recognition when captions are absent')
        self.asr.setToolTip('Unavailable: no verified local backend/model. Selecting this records that limitation; no model download or cloud processing.')
        layout.addWidget(self.asr)
        layout.addWidget(QLabel('Local speech recognition: backend/model unavailable. Caption exports need no FFmpeg.'))
        self.summary = QLabel('Ready. Reuse identical inputs and choices to resume.'); self.summary.setWordWrap(True)
        self.scan_summary = QLabel('Discovery has not started.'); self.scan_summary.setWordWrap(True)
        layout.addWidget(self.summary); layout.addWidget(self.scan_summary)
        self.progress = QProgressBar(); layout.addWidget(self.progress)
        self.inputs = QTableWidget(0,3); self.inputs.setHorizontalHeaderLabels(['Input / target','Discovery','Reason'])
        self.inputs.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.inputs.setMaximumHeight(120); layout.addWidget(self.inputs)
        self.results = QTableWidget(0,4); self.results.setHorizontalHeaderLabels(['Video','Status','Track','Reason'])
        self.results.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        for table in (self.inputs,self.results):
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.results)
        row=QHBoxLayout(); self.start=QPushButton('Extract / Resume'); self.retry=QPushButton('Retry failed')
        self.cancel=QPushButton('Cancel'); self.open_folder=QPushButton('Open folder')
        self.retry.setEnabled(False); self.cancel.setEnabled(False); self.open_folder.setEnabled(False)
        for button in (self.start,self.retry,self.cancel,self.open_folder): row.addWidget(button)
        layout.addLayout(row)
        self.start.clicked.connect(lambda:self._start(False)); self.retry.clicked.connect(lambda:self._start(True))
        self.cancel.clicked.connect(self.cancel_work); self.open_folder.clicked.connect(self._open_folder)
        if settings:
            self.folder.setText(settings.transcript_output_dir or settings.last_output_dir)
            self.language.setText(settings.transcript_language)
            self.preference.setCurrentText(settings.transcript_preference)
            for fmt,box in self.formats.items(): box.setChecked(fmt in settings.transcript_formats)

    @property
    def is_active(self):
        return self._thread is not None

    def _browse(self):
        path=QFileDialog.getExistingDirectory(self,'Select transcript folder',self.folder.text())
        if path: self.folder.setText(path)

    def _choices(self):
        return Choices(self.language.text().strip(), self.preference.currentText(),
                       tuple(fmt for fmt,box in self.formats.items() if box.isChecked()), self.asr.isChecked())

    def _start(self,retry=False):
        if self.is_active: return
        urls=[line.strip() for line in self.urls.toPlainText().splitlines() if line.strip()]
        folder=self.folder.text().strip()
        try:
            choices=self._choices()
            if not urls or not folder: raise ValueError()
            identity=(tuple(urls),str(Path(folder).resolve()),choices)
        except (ValueError, OSError):
            QMessageBox.warning(self,'Transcript inputs','Enter URLs, an export folder, a language and at least one format.'); return
        if retry and identity != self._run_identity:
            QMessageBox.warning(self,'Choices changed','Use Extract / Resume after changing inputs or export choices.'); return
        if identity != self._run_identity:
            self._result=None; self._output_root=None
            self.inputs.setRowCount(0); self.results.setRowCount(0)
            self.scan_summary.setText("Discovery has not started for these inputs.")
        self._run_identity=identity
        if self.settings:
            self.settings.transcript_output_dir=folder
            self.settings.transcript_language=choices.language
            self.settings.transcript_preference=choices.preference
            self.settings.transcript_formats=list(choices.formats)
            self.settings.save()
        self._thread=self.thread_factory(urls,Path(folder),choices,retry=retry,parent=self)
        self._thread.update.connect(self._update)
        self._thread.result.connect(self._finished_result)
        self._thread.error.connect(self._error)
        self._thread.finished.connect(self._thread_finished)
        self._set_busy(True); self.summary.setText('Starting transcript batch…'); self._thread.start()

    def _set_busy(self,busy):
        for widget in (self.urls,self.folder,self.browse,self.language,self.preference,self.asr,*self.formats.values(),self.start):
            widget.setEnabled(not busy)
        self.cancel.setEnabled(busy); self.retry.setEnabled(False)
        self.open_folder.setEnabled(not busy and self._output_root is not None)

    @Slot(str,object)
    def _update(self,stage,data):
        self._result=data
        counts=data['counts']; complete=sum(i['state']=='complete' for i in data['inputs'])
        self.scan_summary.setText(f'Discovery complete for {complete}/{len(data["inputs"])} inputs. Coverage is limited to accessible entries returned by each source.')
        self.summary.setText(f'{stage}: discovered {counts["discovered"]}; attempted {counts["attempted"]}; exported {counts["exported"]}; absent {counts["caption_absent"]}; inaccessible {counts["inaccessible"]}; failed {counts["failed"]}; pending {counts["pending"]}')
        if stage=='Scanning': self.progress.setRange(0,0)
        else:
            self.progress.setRange(0,100)
            total=counts['discovered']; self.progress.setValue(int((total-counts['pending'])*100/total) if total else 0)
        self.inputs.setRowCount(len(data['inputs']))
        for row,record in enumerate(data['inputs']):
            for col,value in enumerate((record['target'] or record['url'],record['state'],record['reason'])):
                self.inputs.setItem(row,col,QTableWidgetItem(str(value)))
        self.results.setRowCount(len(data['videos']))
        for row,record in enumerate(data['videos'].values()):
            track=record.get('track') or {}
            for col,value in enumerate((record['title'],record['status'],f'{track.get("language", "")} {track.get("kind", "")}',record['reason'])):
                item=QTableWidgetItem(str(value)); item.setToolTip(str(value)); self.results.setItem(row,col,item)

    @Slot(object)
    def _finished_result(self,data):
        self._update('Cancelled' if data['cancelled'] else 'Finished',data)

    @Slot(str)
    def _error(self,message):
        self.summary.setText(message)

    @Slot()
    def _thread_finished(self):
        thread=self._thread
        if thread is None: return
        self._output_root=thread.output_root
        self._thread=None; thread.deleteLater(); self._set_busy(False)
        self.progress.setRange(0,100)
        self.retry.setEnabled(bool(self._result and self._result['counts']['failed']))

    def cancel_work(self):
        if self._thread: self._thread.request_cancel(); self.cancel.setEnabled(False)

    def shutdown(self,timeout=100):
        if not self._thread: return True
        self.cancel_work()
        return self._thread.wait(timeout)

    def _open_folder(self):
        if self._output_root and self._output_root.is_dir(): os.startfile(self._output_root)
