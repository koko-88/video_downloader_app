"""Strict caption cues and dependency-free UTF-8 exports."""
from __future__ import annotations

import html
import json
import re
from dataclasses import asdict, dataclass

MAX_BYTES = 16 * 1024 * 1024
MAX_CUES = 100_000
FORMATS = ('md', 'txt', 'json', 'srt', 'vtt')


class CaptionError(ValueError):
    pass


@dataclass(frozen=True)
class Cue:
    start_ms: int
    end_ms: int
    text: str

    def __post_init__(self):
        if (type(self.start_ms) is not int or type(self.end_ms) is not int
                or not 0 <= self.start_ms < self.end_ms <= 10**12
                or not isinstance(self.text, str) or not self.text.strip()):
            raise CaptionError('Invalid or empty caption cue')


def _plain(text: str) -> str:
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = html.unescape(re.sub(r'<[^>]*>', '', text))
    return ''.join(c for c in text if c in '\n\t' or ord(c) >= 32).strip()


def _time(text: str) -> int:
    match = re.fullmatch(r'(?:(\d{2,}):)?(\d{2}):(\d{2})[.,](\d{3})', text)
    if not match:
        raise CaptionError('Malformed caption timestamp')
    hours, minutes, seconds, millis = match.groups()
    if int(minutes) >= 60 or int(seconds) >= 60:
        raise CaptionError('Caption timestamp outside range')
    return ((int(hours or 0) * 60 + int(minutes)) * 60 + int(seconds)) * 1000 + int(millis)


def timestamp(value: int, separator: str = '.') -> str:
    seconds, millis = divmod(value, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{millis:03d}'


def parse_captions(payload: bytes | str, representation: str) -> list[Cue]:
    if isinstance(payload, bytes):
        if len(payload) > MAX_BYTES:
            raise CaptionError('Caption exceeds size limit')
        try:
            text = payload.decode('utf-8-sig')
        except UnicodeError:
            raise CaptionError('Caption is not valid UTF-8') from None
    else:
        text = payload.lstrip('\ufeff')
        if len(text.encode('utf-8')) > MAX_BYTES:
            raise CaptionError('Caption exceeds size limit')
    cues = []
    if representation == 'json3':
        try:
            data = json.loads(text)
            for event in data['events']:
                if 'segs' not in event:
                    continue
                content = _plain(''.join(segment['utf8'] for segment in event['segs']))
                if not content:
                    continue
                start, duration = event['tStartMs'], event['dDurationMs']
                if type(start) is not int or type(duration) is not int:
                    raise CaptionError('Invalid JSON caption timestamp')
                cues.append(Cue(start, start + duration, content))
                if len(cues) > MAX_CUES:
                    raise CaptionError('Too many caption cues')
        except (KeyError, TypeError, ValueError):
            raise CaptionError('Malformed JSON captions') from None
    elif representation in ('vtt', 'srt'):
        text = text.replace('\r\n', '\n').replace('\r', '\n').strip()
        if representation == 'vtt':
            if not re.match(r'^WEBVTT(?:[ \t].*)?(?:\n|$)', text):
                raise CaptionError('Missing WEBVTT header')
            blocks = re.split(r'\n[ \t]*\n', text)
            # WEBVTT metadata is confined to the header block.
            text = '\n\n'.join(blocks[1:])
        for block in re.split(r'\n[ \t]*\n', text):
            lines = block.strip().splitlines()
            if not lines:
                continue
            if representation == 'vtt' and re.match(r'^(NOTE(?:\s|$)|STYLE$|REGION$)', lines[0]):
                continue
            index = 0 if '-->' in lines[0] else 1
            if index >= len(lines):
                raise CaptionError('Caption block missing timing')
            match = re.fullmatch(r'(\S+)\s+-->\s+(\S+)(?:[ \t]+.*)?', lines[index])
            if not match:
                raise CaptionError('Malformed caption timing line')
            content = _plain('\n'.join(lines[index + 1:]))
            cues.append(Cue(_time(match[1]), _time(match[2]), content))
            if len(cues) > MAX_CUES:
                raise CaptionError('Too many caption cues')
    else:
        raise CaptionError('Unsupported caption representation')
    if not cues:
        raise CaptionError('No valid caption cues')
    return sorted(cues, key=lambda cue: cue.start_ms)


def _markdown(text: str) -> str:
    text = html.escape(str(text), quote=False)
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~-])', r'\\\1', text)


def export_captions(cues: list[Cue], fmt: str, provenance: dict) -> bytes:
    if not cues or len(cues) > MAX_CUES:
        raise CaptionError('Invalid caption collection')
    if fmt == 'json':
        content = json.dumps({'schema': 1, 'provenance': provenance,
                              'cues': [asdict(cue) for cue in cues]}, ensure_ascii=False, indent=2) + '\n'
    elif fmt == 'txt':
        content = '\n'.join(cue.text for cue in cues) + '\n'
    elif fmt == 'md':
        content = '# ' + _markdown(provenance.get('title', 'Transcript')) + '\n\n'
        for key in ('source_url', 'extractor', 'video_id', 'language', 'kind', 'acquisition'):
            content += f'{key}: {_markdown(provenance.get(key, ""))}\n\n'
        content += '\n\n'.join(f'[{timestamp(cue.start_ms)}] {_markdown(cue.text)}' for cue in cues) + '\n'
    elif fmt in ('srt', 'vtt'):
        blocks = []
        separator = ',' if fmt == 'srt' else '.'
        for number, cue in enumerate(cues, 1):
            timing = f'{timestamp(cue.start_ms, separator)} --> {timestamp(cue.end_ms, separator)}'
            # Blank lines delimit subtitle cues. Plain text/JSON retain paragraphs;
            # timed formats collapse paragraph separators to a single line break.
            body = html.escape('\n'.join(line for line in cue.text.split('\n') if line.strip()), quote=False)
            blocks.append((f'{number}\n' if fmt == 'srt' else '') + timing + '\n' + body)
        content = ('WEBVTT\n\n' if fmt == 'vtt' else '') + '\n\n'.join(blocks) + '\n'
    else:
        raise CaptionError('Unsupported export format')
    return content.encode('utf-8')
