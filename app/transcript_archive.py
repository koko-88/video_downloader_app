"""Locked transcript archives with verified resume and non-destructive publication."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

from app.captions import export_captions
from app.paths import sanitize_filename_component
from app.transcript_source import SourceError, public_url

STATUSES = ('succeeded', 'caption_absent', 'inaccessible', 'failed', 'pending')


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def contained(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise SourceError('unsafe_output_path')
    path = Path(relative)
    if (path.is_absolute() or path.drive or '..' in path.parts
            or any(part.endswith((' ', '.')) or re.search(r'[<>:"|?*\x00-\x1f]', part)
                   or re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part)
                   for part in path.parts)):
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


class TranscriptArchive:
    """Own the on-disk contract; batch scheduling never handles publication details."""

    def __init__(self, output_dir, urls, choices):
        self._choices = deepcopy(choices)
        self._inputs = [public_url(url) for url in urls]
        batch_id = fingerprint([urls, choices])[:24]
        self.root = contained(Path(output_dir).resolve(), f'transcripts/{batch_id}')
        self.root.mkdir(parents=True, exist_ok=True)
        self._manifest_path = contained(self.root, 'manifest.json')

    @contextmanager
    def open(self):
        """Hold the OS lock while a validated, integrity-checked batch is in use."""
        with batch_lock(self.root):
            document = self._load()
            for record in document['videos'].values():
                if record['status'] == 'succeeded' and not self._verify_outputs(record):
                    record.update(status='failed', reason='output_integrity_changed')
            yield document

    def _load(self):
        inputs = self._inputs
        if self._manifest_path.exists():
            try:
                data = json.loads(self._manifest_path.read_text(encoding='utf-8'))
                if (type(data['schema']) is not int or data['schema'] != 1 or data['urls'] != inputs
                        or data['choices'] != self._choices
                        or not isinstance(data['videos'], dict)
                        or not isinstance(data['inputs'], list)
                        or type(data['cancelled']) is not bool
                        or data.get('halt_reason', '') not in ('', 'rate_limited')
                        or len(data['inputs']) != len(inputs)):
                    raise ValueError()
                for index, item in enumerate(data['inputs']):
                    if (not isinstance(item, dict) or item['url'] != inputs[index]
                            or item['state'] not in ('pending', 'scanning', 'complete', 'incomplete', 'failed')
                            or not isinstance(item['target'], str) or not isinstance(item['reason'], str)
                            or not isinstance(item['videos'], list)
                            or any(not isinstance(key, str) or key not in data['videos'] for key in item['videos'])
                            or len(set(item['videos'])) != len(item['videos'])):
                        raise ValueError()
                for key, video in data['videos'].items():
                    if (not isinstance(video, dict) or video['status'] not in STATUSES
                            or type(video['attempts']) is not int or video['attempts'] < 0
                            or not isinstance(video['extractor'], str) or not video['extractor']
                            or not isinstance(video['video_id'], str) or not video['video_id']
                            or fingerprint([video['extractor'], video['video_id']]) != key
                            or not isinstance(video['inputs'], list) or not video['inputs']
                            or any(type(i) is not int or not 0 <= i < len(inputs) for i in video['inputs'])
                            or len(set(video['inputs'])) != len(video['inputs'])
                            or not isinstance(video['source_url'], str)
                            or public_url(video['source_url']) != video['source_url']
                            or not isinstance(video['title'], str) or not isinstance(video['reason'], str)
                            or not isinstance(video['track'], dict)
                            or not isinstance(video['outputs'], list)):
                        raise ValueError()
                    if any((index in video['inputs']) != (key in item['videos'])
                           for index, item in enumerate(data['inputs'])):
                        raise ValueError()
                    paths = set()
                    for output in video['outputs']:
                        if (not isinstance(output, dict) or not isinstance(output['path'], str)
                                or not isinstance(output['sha256'], str)
                                or not re.fullmatch('[0-9a-f]{64}', output['sha256'])
                                or output['path'] in paths):
                            raise ValueError()
                        contained(self.root, output['path'])
                        paths.add(output['path'])
                    if video['status'] == 'succeeded' and (
                            video['attempts'] == 0 or len(paths) != len(self._choices['formats'])
                            or {Path(p).suffix[1:] for p in paths} != set(self._choices['formats'])
                            or any(not isinstance(video['track'].get(field), str)
                                   for field in ('language', 'kind', 'representation', 'acquisition'))):
                        raise ValueError()
                return data
            except (KeyError, TypeError, ValueError, OSError):
                raise SourceError('invalid_manifest_preserved') from None
        return dict(schema=1, urls=list(inputs), choices=deepcopy(self._choices),
                    inputs=[dict(url=url, target='', state='pending', reason='', videos=[]) for url in inputs],
                    videos={}, cancelled=False)

    def save(self, document):
        counts = {status: 0 for status in STATUSES}
        for video in document['videos'].values():
            counts[video['status']] += 1
        counts.update(discovered=sum(counts.values()),
                      attempted=sum(v['attempts'] > 0 for v in document['videos'].values()),
                      exported=counts['succeeded'],
                      not_attempted=sum(v['attempts'] == 0 for v in document['videos'].values()))
        document['counts'] = counts
        data = json.dumps(document, ensure_ascii=False, indent=2).encode('utf-8')
        fd, name = tempfile.mkstemp(dir=self.root, prefix='.manifest-', suffix='.tmp')
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
            os.replace(name, self._manifest_path)
        finally:
            Path(name).unlink(missing_ok=True)

    def export(self, key, cues, provenance, check_cancelled):
        """Publish every selected representation, reusing identical partial exports."""
        # Prefix protects Windows device names; digest binds path to canonical identity.
        stem = 'video-' + sanitize_filename_component(provenance['title'], 60).rstrip(' .') + '-' + key[:16]
        outputs = []
        for fmt in sorted(self._choices['formats']):
            check_cancelled()
            relative = f'{stem}/transcript.{fmt}'
            data = export_captions(cues, fmt, provenance)
            self._write_output(relative, data)
            outputs.append(dict(path=relative, sha256=hashlib.sha256(data).hexdigest()))
        return outputs

    @staticmethod
    def _hash_file(path):
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()

    def _verify_outputs(self, record):
        outputs = record.get('outputs') or []
        if len(outputs) != len(self._choices['formats']):
            return False
        try:
            if {Path(item['path']).suffix[1:] for item in outputs} != set(self._choices['formats']):
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
                if os.name == 'nt':
                    os.rename(name, path)  # Windows rename refuses existing files, including on exFAT.
                else:
                    os.link(name, path)
            except FileExistsError:
                if path.stat().st_size != len(data) or self._hash_file(path) != hashlib.sha256(data).hexdigest():
                    raise SourceError('output_conflict_preserved') from None
        finally:
            Path(name).unlink(missing_ok=True)
