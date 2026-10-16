"""Version-grounded yt-dlp metadata/caption adapter; no rendered media downloads."""
from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import yt_dlp
from yt_dlp.extractor import gen_extractor_classes
from yt_dlp.networking import Request

from app.captions import MAX_BYTES, parse_captions
from app.cookie_fallback import browsers_to_try, should_attempt_cookie_fallback


class Cancelled(Exception):
    pass


class SourceError(Exception):
    def __init__(self, reason: str, status: str = 'failed'):
        self.reason, self.status = reason, status
        super().__init__(reason)


def classified_error(exc: Exception) -> SourceError:
    if isinstance(exc, SourceError):
        return exc
    text = str(exc).lower()
    if '10013' in text or 'network access is denied' in text:
        return SourceError('network_access_denied')
    if any(x in text for x in ('429', 'too many requests', 'rate limit', 'throttl')):
        return SourceError('rate_limited')
    if any(x in text for x in ('private', 'deleted', 'unavailable', 'not available', '403', '401', 'sign in', 'permission', 'drm', 'geo', 'region', 'members-only', 'login required')):
        return SourceError('inaccessible', 'inaccessible')
    if any(x in text for x in ('timeout', 'timed out', 'network', 'connection', 'resolve', 'unreachable')):
        return SourceError('network_error')
    if 'unsupported' in text:
        return SourceError('unsupported_url')
    return SourceError('extraction_error')


def public_url(url: str) -> str:
    """Retain public identity without userinfo, fragments or unknown signed query fields."""
    try:
        parts = urlsplit(str(url))
        if parts.scheme not in ('http', 'https') or not parts.hostname:
            return ''
        host = parts.hostname
        if ':' in host:
            host = '[' + host + ']'
        if parts.port:
            host += ':' + str(parts.port)
        query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if k in ('v', 'list', 'index')])
        return urlunsplit((parts.scheme, host, parts.path, query, ''))
    except (ValueError, TypeError):
        return ''


def normalize_target(url: str) -> str:
    try:
        parts = urlsplit(url.strip())
        if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
            raise ValueError()
        _ = parts.port
        if any(re.search(r'(token|secret|password|signature|auth|cookie|api.key|^sig$)', key, re.I)
               for key, _ in parse_qsl(parts.query)):
            raise ValueError()
        if any(ord(c) < 32 for c in url):
            raise ValueError()
    except (ValueError, TypeError):
        raise SourceError('invalid_or_credential_url') from None
    path = parts.path.rstrip('/')
    host = parts.hostname.lower()
    if host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
        if re.fullmatch(r'/(@[^/]+|channel/[^/]+|c/[^/]+|user/[^/]+)', path):
            path += '/videos'
    return urlunsplit((parts.scheme, parts.netloc, path or '/', parts.query, ''))


class ScanLog:
    def __init__(self, cancelled):
        self.cancelled = cancelled
        self.uncertain = False

    def _check(self):
        if self.cancelled():
            raise Cancelled()

    def debug(self, message):
        self._check()
        if 'looping' in str(message).lower() or 'assuming end' in str(message).lower():
            self.uncertain = True

    info = debug

    def warning(self, message):
        self._check()
        self.uncertain = True

    error = warning


class TranscriptSource:
    def __init__(self, cancelled=lambda: False, factory=None):
        self.cancelled = cancelled
        self.log = ScanLog(cancelled)
        self.factory = factory or yt_dlp.YoutubeDL
        self.sessions = []
        self.ydl = None

    def _options(self, browser=None):
        opts = dict(skip_download=True, ignoreerrors=False, extract_flat=False,
                    quiet=True, no_warnings=False, logger=self.log, socket_timeout=20,
                    retries=1, extractor_retries=1, noplaylist=False, cachedir=False)
        if browser:
            opts['cookiesfrombrowser'] = (browser,)
        return opts

    def __enter__(self):
        self._session()
        return self

    def _session(self, browser=None):
        session = self.factory(self._options(browser))
        self.ydl = session.__enter__()
        self.sessions.append(session)

    def __exit__(self, *args):
        for session in reversed(self.sessions):
            session.__exit__(*args)

    def check(self):
        if self.cancelled():
            raise Cancelled()

    def extract(self, url: str, ie_key=None):
        self.check()
        target = normalize_target(url)
        if ie_key is None and not any(cls.ie_key() != 'Generic' and cls.suitable(target)
                                     for cls in gen_extractor_classes()):
            raise SourceError('unsupported_url')
        try:
            return self.ydl.extract_info(target, download=False, process=False, ie_key=ie_key)
        except Cancelled:
            raise
        except Exception as exc:
            if not should_attempt_cookie_fallback(target, exc):
                raise classified_error(exc) from None
            for browser in browsers_to_try(target):
                if browser is None:
                    continue
                self.check()
                try:
                    self._session(browser)
                    return self.ydl.extract_info(target, download=False, process=False, ie_key=ie_key)
                except Cancelled:
                    raise
                except Exception:
                    continue
            raise SourceError('authentication_unavailable', 'inaccessible') from None

    def captions(self, info: dict, language: str, preference: str):
        self.check()
        normal, automatic = info.get('subtitles') or {}, info.get('automatic_captions') or {}
        if not normal and not automatic:
            raise SourceError('caption_absent', 'caption_absent')
        order = {'manual-first': ('manual', 'automatic'), 'auto-first': ('automatic', 'manual'),
                 'manual-only': ('manual',), 'auto-only': ('automatic',)}[preference]
        for kind in order:
            tracks = (normal if kind == 'manual' else automatic).get(language) or []
            if not tracks:
                continue
            for representation in ('vtt', 'srt', 'json3'):
                for track in tracks:
                    if track.get('ext') != representation:
                        continue
                    if 'data' in track:
                        payload = track['data']
                    else:
                        url = track.get('url', '')
                        if urlsplit(url).scheme not in ('http', 'https'):
                            raise SourceError('unsafe_caption_url')
                        try:
                            headers = dict(info.get('http_headers') or {})
                            headers.update(track.get('http_headers') or {})
                            with self.ydl.urlopen(Request(url, headers=headers)) as response:
                                chunks, size = [], 0
                                while True:
                                    self.check()
                                    chunk = response.read(min(65536, MAX_BYTES + 1 - size))
                                    if not chunk:
                                        break
                                    chunks.append(chunk)
                                    size += len(chunk)
                                    if size > MAX_BYTES:
                                        raise SourceError('caption_size_limit')
                                payload = b''.join(chunks)
                        except Cancelled:
                            raise
                        except Exception as exc:
                            raise classified_error(exc) from None
                    try:
                        cues = parse_captions(payload, representation)
                    except ValueError:
                        raise SourceError('malformed_captions') from None
                    return cues, dict(language=language, kind=kind, representation=representation,
                                      acquisition='captions')
            raise SourceError('unsupported_caption_representation')
        raise SourceError('language_unavailable')
