"""Resumable transcript batch with honest discovery and non-destructive exports."""
from __future__ import annotations

import time
from dataclasses import dataclass

from app.captions import FORMATS
from app.transcript_archive import TranscriptArchive, fingerprint
from app.transcript_source import (Cancelled, SourceError, TranscriptSource,
                                   classified_error, normalize_target, public_url)


@dataclass(frozen=True)
class Choices:
    language: str = 'en'
    preference: str = 'manual-first'
    formats: tuple[str, ...] = ('txt',)
    local_asr: bool = False

    def __post_init__(self):
        if (not isinstance(self.language, str) or not self.language.strip() or len(self.language) > 80
                or type(self.local_asr) is not bool
                or self.preference not in ('manual-first', 'auto-first', 'manual-only', 'auto-only')
                or not self.formats or len(set(self.formats)) != len(self.formats)
                or any(fmt not in FORMATS for fmt in self.formats)):
            raise ValueError('Invalid transcript choices')

    def document(self):
        return dict(language=self.language, preference=self.preference,
                    formats=sorted(self.formats), local_asr=self.local_asr)


class TranscriptBatch:
    def __init__(self, urls, output_dir, choices=None, cancelled=lambda: False,
                 progress=lambda stage, data: None, source_factory=TranscriptSource):
        self.urls = [str(url).strip() for url in urls if str(url).strip()]
        if not self.urls:
            raise ValueError('At least one URL required')
        self.choices = choices or Choices()
        self.cancelled, self.progress, self.source_factory = cancelled, progress, source_factory
        self._archive = TranscriptArchive(output_dir, self.urls, self.choices.document())
        self.root = self._archive.root
        self.document = None
        self._last_scan_save = 0.0
        self._request_urls = {}
        self._changed_videos = {}
        self._changed_inputs = set(range(len(self.urls)))

    def check(self):
        if self.cancelled():
            raise Cancelled()

    def notify(self, stage):
        if stage == 'Scanning' and time.monotonic() - self._last_scan_save < 0.2:
            return
        self._last_scan_save = time.monotonic()
        self._archive.save(self.document)
        self.progress(stage, self.document)

    def progress_snapshot(self):
        """Copy only display values changed since the previous worker notification."""
        videos = self.document['videos']
        inputs = self.document['inputs']
        snapshot = dict(counts=dict(self.document['counts']),
                        input_count=len(inputs),
                        complete_inputs=sum(item['state'] == 'complete' for item in inputs),
                        input_rows={i: (inputs[i]['target'] or inputs[i]['url'], inputs[i]['state'], inputs[i]['reason'])
                                    for i in sorted(self._changed_inputs)},
                        video_rows={key: (videos[key]['title'], videos[key]['status'],
                                          f'{videos[key]["track"].get("language", "")} {videos[key]["track"].get("kind", "")}',
                                          videos[key]['reason']) for key in self._changed_videos})
        self._changed_inputs.clear()
        self._changed_videos.clear()
        return snapshot

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
        # Request URLs stay in memory; persisted provenance intentionally strips unknown queries.
        self._request_urls[key] = str(source_url)
        self._changed_videos[key] = None
        self._changed_inputs.add(index)
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
                    if exc.reason == 'rate_limited':
                        raise
            expected = info.get('playlist_count')
            if expected is not None and int(expected) != count:
                raise SourceError('collection_count_mismatch')
        elif kind == 'video':
            self._add(info, index, fallback, position)
            self.notify('Scanning')
        else:
            raise SourceError('unsupported_metadata')

    def _process(self, key, record):
        self.check()
        record['attempts'] += 1
        self._changed_videos[key] = None
        self.notify('Extracting')
        try:
            with self.source_factory(self.cancelled) as source:
                info = source.extract(self._request_urls.get(key, record['source_url']))
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
            self._changed_videos[key] = None
            self.check()
            self.notify('Exporting')
            provenance = dict(source_url=record['source_url'], extractor=record['extractor'],
                              video_id=record['video_id'], title=record['title'], **track)
            outputs = self._archive.export(key, cues, provenance, self.check)
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
        finally:
            self._changed_videos[key] = None

    def run(self, retry_failed=False):
        with self._archive.open() as document:
            self.document = document
            self.document['cancelled'] = False
            self.document['halt_reason'] = ''
            try:
                self._changed_videos.update(self.document['videos'])
                if not retry_failed or any(v['extractor'] != 'Youtube' and v['status'] == 'failed'
                                           for v in self.document['videos'].values()):
                    for index, url in enumerate(self.urls):
                        input_record = self.document['inputs'][index]
                        # Rehydrate non-YouTube request identities after process restart without
                        # persisting signed/unknown query parameters in the manifest.
                        rehydrate = any(self.document['videos'][key]['extractor'] != 'Youtube'
                                        and self.document['videos'][key]['status'] == ('failed' if retry_failed else 'pending')
                                        and key not in self._request_urls for key in input_record['videos'])
                        if not rehydrate and (retry_failed or input_record['state'] == 'complete'):
                            continue
                        self.check()
                        input_record.update(state='scanning', reason='')
                        self._changed_inputs.add(index)
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
                            self._changed_inputs.add(index)
                            raise
                        except Exception as exc:
                            error = classified_error(exc)
                            input_record.update(state='incomplete' if input_record['videos'] else 'failed', reason=error.reason)
                            if error.reason == 'rate_limited':
                                self.document['halt_reason'] = error.reason
                        self._changed_inputs.add(index)
                        self.notify('Scanning')
                        if self.document['halt_reason']:
                            break
                for key, record in self.document['videos'].items():
                    if self.document['halt_reason']:
                        break
                    if (record['status'] == 'pending' and not retry_failed) or (record['status'] == 'failed' and retry_failed):
                        self._process(key, record)
                        if record['reason'] == 'rate_limited':
                            self.document['halt_reason'] = 'rate_limited'
                        self.notify('Processed')
            except Cancelled:
                self.document['cancelled'] = True
            self.notify('Cancelled' if self.document['cancelled'] else
                        'Rate limited' if self.document['halt_reason'] else 'Finished')
            return self.document
