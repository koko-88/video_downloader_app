"""Resumable transcript batch with honest discovery and non-destructive exports."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from app.captions import FORMATS, export_captions
from app.paths import sanitize_filename_component
from app.transcript_source import (Cancelled, SourceError, TranscriptSource,
                                   classified_error, normalize_target, public_url)

STATUSES = ('succeeded', 'caption_absent', 'inaccessible', 'failed', 'pending')


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class Choices:
    language: str = 'en'
    preference: str = 'manual-first'
    formats: tuple[str, ...] = ('txt',)
    local_asr: bool = False

    def __post_init__(self):
        if (not self.language.strip() or len(self.language) > 80
                or self.preference not in ('manual-first', 'auto-first', 'manual-only', 'auto-only')
                or not self.formats or len(set(self.formats)) != len(self.formats)
                or any(fmt not in FORMATS for fmt in self.formats)):
            raise ValueError('Invalid transcript choices')

    def document(self):
        return dict(language=self.language, preference=self.preference,
                    formats=sorted(self.formats), local_asr=self.local_asr)


def contained(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or path.drive or '..' in path.parts:
        raise SourceError('unsafe_output_path')
    candidate = root / path
    try:
        candidate.resolve().relative_to(root.resolve())
    except (ValueError, OSError):
        raise SourceError('unsafe_output_path') from None
    return candidate


@contextmanager
def batch_lock(root: Path):
    path = contained(root, '.batch.lock')
    stream = path.open('a+b')
    try:
        if not path.stat().st_size:
            stream.write(b'0'); stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise SourceError('batch_already_running') from None
        yield
    finally:
        stream.close()  # OS lock released even after process interruption.


class TranscriptBatch:
    def __init__(self, urls, output_dir, choices=None, cancelled=lambda: False,
                 progress=lambda stage, data: None, source_factory=TranscriptSource):
        self.urls = [str(url).strip() for url in urls if str(url).strip()]
        if not self.urls:
            raise ValueError('At least one URL required')
        self.choices = choices or Choices()
        self.cancelled, self.progress, self.source_factory = cancelled, progress, source_factory
        output_dir = Path(output_dir).resolve()
        batch_id = fingerprint([self.urls, self.choices.document()])[:24]
        self.root = contained(output_dir, f'transcripts/{batch_id}')
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest_path = contained(self.root, 'manifest.json')
        self.document = None
        self._last_scan_save = 0.0

    def check(self):
        if self.cancelled():
            raise Cancelled()

    def _load(self):
        inputs = [public_url(url) for url in self.urls]
        if self.manifest_path.exists():
            try:
                data = json.loads(self.manifest_path.read_text(encoding='utf-8'))
                if (data['schema'] != 1 or data['urls'] != inputs
                        or data['choices'] != self.choices.document()
                        or not isinstance(data['videos'], dict)
                        or len(data['inputs']) != len(inputs)):
                    raise ValueError()
                for key, video in data['videos'].items():
                    if (video['status'] not in STATUSES or not isinstance(video['attempts'], int)
                            or fingerprint([video['extractor'], video['video_id']]) != key
                            or not isinstance(video['inputs'], list)):
                        raise ValueError()
                    for output in video.get('outputs', []):
                        contained(self.root, output['path'])
                self.document = data
                return
            except (KeyError, TypeError, ValueError, OSError):
                raise SourceError('invalid_manifest_preserved') from None
        self.document = dict(schema=1, urls=inputs, choices=self.choices.document(),
                             inputs=[dict(url=url, target='', state='pending', reason='', videos=[]) for url in inputs],
                             videos={}, cancelled=False)

    def counts(self):
        counts = {status: 0 for status in STATUSES}
        for video in self.document['videos'].values():
            counts[video['status']] += 1
        counts.update(discovered=sum(counts.values()),
                      attempted=sum(v['attempts'] > 0 for v in self.document['videos'].values()),
                      exported=counts['succeeded'],
                      not_attempted=sum(v['attempts'] == 0 for v in self.document['videos'].values()))
        return counts

    def save(self):
        self.document['counts'] = self.counts()
        data = json.dumps(self.document, ensure_ascii=False, indent=2).encode('utf-8')
        fd, name = tempfile.mkstemp(dir=self.root, prefix='.manifest-', suffix='.tmp')
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
            os.replace(name, self.manifest_path)
        finally:
            Path(name).unlink(missing_ok=True)

    def notify(self, stage):
        if stage == 'Scanning' and time.monotonic() - self._last_scan_save < 0.2:
            return
        self._last_scan_save = time.monotonic()
        self.save()
        self.progress(stage, self.document)

    def _add(self, info, index, fallback, position):
        extractor = str(info.get('extractor_key') or info.get('ie_key') or info.get('extractor') or 'Unknown')
        if extractor.lower().startswith('youtube'):
            extractor = 'Youtube'
        video_id = str(info.get('id') or f'unknown-{fingerprint([index, position])[:16]}')
        key = fingerprint([extractor, video_id])
        source_url = info.get('webpage_url') or info.get('url') or fallback
        if extractor == 'Youtube' and info.get('id'):
            from urllib.parse import urlencode
            source_url = 'https://www.youtube.com/watch?' + urlencode({'v': video_id})
        record = self.document['videos'].get(key)
        if record is None:
            inaccessible = not info.get('id') or info.get('availability') in ('private', 'premium_only', 'subscriber_only', 'needs_auth')
            record = dict(extractor=extractor, video_id=video_id, source_url=public_url(source_url),
                          title=str(info.get('title') or video_id)[:500], inputs=[], attempts=0,
                          status='inaccessible' if inaccessible else 'pending',
                          reason='unavailable_entry' if inaccessible else '', track={}, outputs=[])
            self.document['videos'][key] = record
        if index not in record['inputs']:
            record['inputs'].append(index)
        if key not in self.document['inputs'][index]['videos']:
            self.document['inputs'][index]['videos'].append(key)
        return key

    def _walk(self, source, info, index, fallback, ancestry=(), position=()):
        self.check()
        if len(ancestry) > 20:
            raise SourceError('collection_depth_limit')
        if not isinstance(info, dict):
            self._add({}, index, fallback, position)
            source.log.uncertain = True
            return
        kind = info.get('_type', 'video')
        if kind in ('url', 'url_transparent'):
            # Flat video references retain their visible unavailable records without resolving captions.
            key = info.get('ie_key', '')
            if info.get('id') and (key == 'Youtube' or info.get('availability') in ('private','needs_auth')):
                self._add(info, index, fallback, position)
                self.notify('Scanning')
                return
            target = info.get('url')
            identity = (str(target), str(key))
            if identity in ancestry:
                raise SourceError('collection_cycle')
            resolved = source.extract(target, ie_key=key or None)
            self._walk(source, resolved, index, target, ancestry + (identity,), position)
            return
        if kind in ('playlist', 'multi_video', 'compat_list'):
            identity = (str(info.get('extractor_key')), str(info.get('id')))
            if identity in ancestry:
                raise SourceError('collection_cycle')
            entries = info.get('entries')
            if entries is None:
                raise SourceError('missing_collection_entries')
            count = 0
            for count, entry in enumerate(entries, 1):
                self.check()
                try:
                    self._walk(source, entry, index, fallback, ancestry + (identity,), position + (count,))
                except SourceError as exc:
                    source.log.uncertain = True
                    if isinstance(entry, dict) and entry.get('id') and entry.get('_type') not in ('playlist', 'multi_video'):
                        key = self._add(entry, index, fallback, position + (count,))
                        record = self.document['videos'][key]
                        if record['status'] != 'succeeded':
                            record.update(status=exc.status, reason=exc.reason)
            expected = info.get('playlist_count')
            if expected is not None and int(expected) != count:
                raise SourceError('collection_count_mismatch')
        elif kind == 'video':
            self._add(info, index, fallback, position)
            self.notify('Scanning')
        else:
            raise SourceError('unsupported_metadata')

    @staticmethod
    def _hash_file(path):
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()

    def _verify_outputs(self, record):
        outputs = record.get('outputs') or []
        if len(outputs) != len(self.choices.formats):
            return False
        try:
            if {Path(item['path']).suffix[1:] for item in outputs} != set(self.choices.formats):
                return False
            return all(self._hash_file(contained(self.root, item['path'])) == item['sha256'] for item in outputs)
        except (OSError, KeyError, SourceError):
            return False

    def _write_output(self, relative, data):
        path = contained(self.root, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if path.stat().st_size != len(data) or self._hash_file(path) != hashlib.sha256(data).hexdigest():
                raise SourceError('output_conflict_preserved')
            return
        fd, name = tempfile.mkstemp(dir=path.parent, prefix='.export-', suffix='.tmp')
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
            try:
                os.link(name, path)  # exclusive atomic publication; never replace a user file
            except FileExistsError:
                if path.stat().st_size != len(data) or self._hash_file(path) != hashlib.sha256(data).hexdigest():
                    raise SourceError('output_conflict_preserved') from None
        finally:
            Path(name).unlink(missing_ok=True)

    def _process(self, key, record):
        self.check()
        record['attempts'] += 1
        self.notify('Extracting')
        try:
            with self.source_factory(self.cancelled) as source:
                info = source.extract(record['source_url'])
                # A video reference may resolve through a transparent URL.
                for _ in range(20):
                    if not isinstance(info, dict):
                        raise SourceError('invalid_video_metadata')
                    if info.get('_type') not in ('url', 'url_transparent'):
                        break
                    info = source.extract(info['url'], ie_key=info.get('ie_key'))
                if info.get('_type', 'video') != 'video':
                    raise SourceError('expected_single_video')
                if info.get('id') is not None and str(info['id']) != record['video_id']:
                    raise SourceError('video_identity_changed')
                cues, track = source.captions(info, self.choices.language, self.choices.preference)
            record['track'] = track
            self.check()
            self.notify('Exporting')
            provenance = dict(source_url=record['source_url'], extractor=record['extractor'],
                              video_id=record['video_id'], title=record['title'], **track)
            # Prefix protects Windows device names; digest binds path to canonical identity.
            stem = 'video-' + sanitize_filename_component(record['title'], 60).rstrip(' .') + '-' + key[:16]
            outputs = []
            for fmt in sorted(self.choices.formats):
                self.check()
                relative = f'{stem}/transcript.{fmt}'
                data = export_captions(cues, fmt, provenance)
                self._write_output(relative, data)
                outputs.append(dict(path=relative, sha256=hashlib.sha256(data).hexdigest()))
            record.update(status='succeeded', reason='', outputs=outputs)
        except Cancelled:
            record.update(status='pending', reason='cancelled')
            raise
        except Exception as exc:
            error = classified_error(exc)
            reason = error.reason
            if reason == 'caption_absent' and self.choices.local_asr:
                reason = 'caption_absent; local_asr_backend_model_unavailable'
            record.update(status=error.status, reason=reason)

    def run(self, retry_failed=False):
        with batch_lock(self.root):
            self._load()
            self.document['cancelled'] = False
            try:
                for record in self.document['videos'].values():
                    if record['status'] == 'succeeded' and not self._verify_outputs(record):
                        record.update(status='failed', reason='output_integrity_changed')
                if not retry_failed:
                    for index, url in enumerate(self.urls):
                        input_record = self.document['inputs'][index]
                        if input_record['state'] == 'complete':
                            continue
                        self.check()
                        input_record.update(state='scanning', reason='')
                        self.notify('Scanning')
                        try:
                            input_record['target'] = public_url(normalize_target(url))
                            with self.source_factory(self.cancelled) as source:
                                info = source.extract(url)
                                self._walk(source, info, index, url)
                                if source.log.uncertain:
                                    raise SourceError('extractor_warning_or_feed_loop')
                            input_record['state'] = 'complete'
                        except Cancelled:
                            input_record.update(state='incomplete', reason='cancelled')
                            raise
                        except Exception as exc:
                            error = classified_error(exc)
                            input_record.update(state='incomplete' if input_record['videos'] else 'failed', reason=error.reason)
                        self.notify('Scanning')
                for key, record in self.document['videos'].items():
                    if (record['status'] == 'pending' and not retry_failed) or (record['status'] == 'failed' and retry_failed):
                        self._process(key, record)
                        self.notify('Processed')
            except Cancelled:
                self.document['cancelled'] = True
            self.notify('Cancelled' if self.document['cancelled'] else 'Finished')
            return self.document
