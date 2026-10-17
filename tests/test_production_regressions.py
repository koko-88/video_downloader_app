"""Behavioral regressions from the production gap audit."""
import copy
import errno
import io
import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.captions import Cue, export_captions, parse_captions
from app.downloader_worker import DownloaderWorker
from app.ffmpeg_resolver import FFmpegInfo
from app.transcript_batch import Choices, TranscriptBatch, contained
from app.transcript_source import SourceError, TranscriptSource
from tests.test_transcript_batch import BASE, FixtureSource, video


class ProductionBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        FixtureSource.metadata = {BASE+'a': video('a')}
        FixtureSource.outcomes = {}
        FixtureSource.extracted = []
        FixtureSource.uncertainty = False
        FixtureSource.on_caption = None

    def batch(self, urls=None, **kwargs):
        return TranscriptBatch(urls or [BASE+'a'], self.root,
                               source_factory=FixtureSource, **kwargs)

    def test_non_youtube_query_identity_survives_restart(self):
        url = 'https://media.example/watch?episode=42'
        FixtureSource.metadata = {url: dict(id='42', extractor_key='Example',
                                           title='Episode', webpage_url=url)}
        cancel = [False]
        def progress(stage, data):
            if stage == 'Extracting':
                cancel[0] = True
        batch = self.batch([url], cancelled=lambda: cancel[0], progress=progress)
        first = batch.run()
        self.assertTrue(first['cancelled'])
        cancel[0] = False
        resumed = self.batch([url]).run()
        self.assertEqual(resumed['counts']['succeeded'], 1)
        self.assertEqual(resumed['counts']['failed'], 0)
        self.assertNotIn('episode=', json.dumps(resumed))

    def test_provider_rate_limit_stops_new_video_requests_and_preserves_resume(self):
        FixtureSource.metadata[BASE+'b']=video('b')
        FixtureSource.outcomes={'a':SourceError('rate_limited')}
        batch=self.batch([BASE+'a',BASE+'b'])
        first=batch.run()
        self.assertEqual(first.get('halt_reason'),'rate_limited')
        self.assertFalse(first['cancelled'])
        self.assertEqual((first['counts']['failed'],first['counts']['pending']),(1,1))
        self.assertEqual(next(v for v in first['videos'].values() if v['video_id']=='b')['attempts'],0)
        FixtureSource.outcomes={}
        resumed=batch.run()
        self.assertEqual(resumed['counts']['succeeded'],1)
        final=batch.run(retry_failed=True)
        self.assertEqual(final['counts']['succeeded'],2)

    def test_discovery_rate_limit_leaves_later_inputs_unattempted(self):
        playlist='https://youtube.com/playlist?list=limited'
        FixtureSource.metadata[playlist]=SourceError('rate_limited')
        result=self.batch([playlist,BASE+'a']).run()
        self.assertEqual(result.get('halt_reason'),'rate_limited')
        self.assertEqual(result['inputs'][1]['state'],'pending')
        self.assertEqual(FixtureSource.extracted,[playlist])

    def test_explicit_request_throttling_stops_subsequent_inputs(self):
        FixtureSource.metadata[BASE+'a'] = RuntimeError('request throttled')
        FixtureSource.metadata[BASE+'b'] = video('b')
        result = self.batch([BASE+'a', BASE+'b']).run()
        self.assertEqual(result.get('halt_reason'), 'rate_limited')
        self.assertEqual(result['inputs'][1]['state'], 'pending')
        self.assertEqual(FixtureSource.extracted, [BASE+'a'])

    def test_invalid_manifest_state_is_preserved_before_any_mutation(self):
        batch = self.batch()
        original = copy.deepcopy(batch.run())
        mutations = [
            lambda d: d['inputs'][0].update(state='imaginary'),
            lambda d: d['inputs'][0].update(videos=['missing-video']),
            lambda d: next(iter(d['videos'].values())).update(attempts=-1),
            lambda d: next(iter(d['videos'].values())).update(attempts=True),
            lambda d: next(iter(d['videos'].values())).update(inputs=[99]),
            lambda d: next(iter(d['videos'].values())).update(inputs=[]),
            lambda d: next(iter(d['videos'].values())).update(outputs={}),
            lambda d: next(iter(d['videos'].values()))['outputs'][0].update(sha256='invalid'),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data = copy.deepcopy(original)
                mutate(data)
                before = json.dumps(data).encode()
                batch.manifest_path.write_bytes(before)
                with self.assertRaisesRegex(SourceError, 'invalid_manifest_preserved'):
                    batch.run()
                self.assertEqual(batch.manifest_path.read_bytes(), before)

    def test_windows_alternate_stream_paths_are_rejected(self):
        for name in ('video/transcript.txt:secret', 'video./transcript.txt',
                     'video /transcript.txt', 'video/CON.txt'):
            with self.subTest(name=name), self.assertRaises(SourceError):
                contained(self.root, name)

    @unittest.skipUnless(os.name == 'nt', 'Windows publication contract')
    def test_windows_exports_do_not_require_filesystem_hard_links(self):
        with patch('app.transcript_batch.os.link', side_effect=OSError(errno.ENOTSUP, 'no hard links')):
            batch = self.batch()
            data = batch.run()
        self.assertEqual(data['counts']['succeeded'], 1)
        output = batch.root / next(iter(data['videos'].values()))['outputs'][0]['path']
        self.assertTrue(output.is_file())
        output.write_text('user data', encoding='utf-8')
        batch.run(retry_failed=True)
        self.assertEqual(output.read_text(encoding='utf-8'), 'user data')


class ProviderRateLimitTests(unittest.TestCase):
    def test_metadata_numbers_and_urls_do_not_imply_a_rate_limit(self):
        from app.cookie_fallback import should_attempt_cookie_fallback
        from app.errors import (RATE_LIMITED_MSG, is_format_unavailable_error,
                                is_rate_limited_error, map_error)
        messages = ('[youtube] ab-429-xyz: Requested format is not available',
                    'Unable to download webpage https://example.test/video/429',
                    'Cannot extract title Episode 429',
                    'Video Throttle Control is unavailable',
                    'Cannot find movie Throttled Dreams',
                    'Connection reset https://example.test/rate_limit')
        for message in messages:
            with self.subTest(message=message):
                error = RuntimeError(message)
                self.assertFalse(is_rate_limited_error(error))
                self.assertNotEqual(map_error(error), RATE_LIMITED_MSG)
                from app.transcript_source import classified_error
                self.assertNotEqual(classified_error(error).reason, 'rate_limited')
        self.assertTrue(is_format_unavailable_error(RuntimeError(messages[0])))
        self.assertTrue(should_attempt_cookie_fallback(
            BASE+'ab-429-xyz', RuntimeError('[youtube] ab-429-xyz: please sign in')))

    def test_explicit_http_limit_contexts_remain_rate_limited(self):
        from app.errors import is_rate_limited_error
        for message in ('HTTP Error 429: Permission denied', '<HTTPError 429: blocked>',
                        'HTTP 429', 'HTTP/1.1 429', 'Response status: 429',
                        'Status code 429', 'Too Many Requests', 'source rate_limited',
                        'request throttled', 'requests are being throttled',
                        'Your request has been throttled', 'source is throttling requests',
                        'throttled'):
            with self.subTest(message=message):
                self.assertTrue(is_rate_limited_error(RuntimeError(message)))

    def test_structured_http_status_survives_generic_wrapping(self):
        from types import SimpleNamespace
        from urllib.error import HTTPError as UrlHTTPError
        from yt_dlp.networking.exceptions import HTTPError
        from yt_dlp.utils import DownloadError
        from app.errors import is_rate_limited_error
        error = HTTPError(SimpleNamespace(status=429, reason='Wait'))
        error.args = ('Request failed',)
        self.assertTrue(is_rate_limited_error(error))
        wrapped = DownloadError('Extraction failed', exc_info=(type(error), error, None))
        self.assertTrue(is_rate_limited_error(wrapped))
        self.assertTrue(is_rate_limited_error(UrlHTTPError('https://example.test', 429, 'Wait', {}, None)))
        other = HTTPError(SimpleNamespace(status=404, reason='Not found'))
        wrapped = DownloadError('Could not open https://example.test/429', exc_info=(type(other), other, None))
        self.assertFalse(is_rate_limited_error(wrapped))

    def test_download_limit_dominates_cookie_database_and_format_fallbacks(self):
        from yt_dlp.utils import DownloadError
        messages=('HTTP Error 429: Sign in to confirm you are not a bot',
                  'HTTP Error 429: Permission denied',
                  'HTTP Error 429: Requested format is not available')
        for message in messages:
            with self.subTest(message=message):
                session=MagicMock(); session.__enter__.return_value=session
                session.extract_info.side_effect=DownloadError(message)
                runtime=FFmpegInfo(True,Path('ffmpeg.exe'),Path('ffprobe.exe'),Path('.'),'fixture')
                with patch('app.downloader_worker.resolve_ffmpeg',return_value=runtime),\
                     patch('app.downloader_worker.yt_dlp.YoutubeDL',return_value=session) as factory:
                    success,reason,path=DownloaderWorker(BASE+'a',Path('.'),'MP4 Video','Best','Best').run()
                self.assertFalse(success); self.assertIsNone(path)
                self.assertEqual(factory.call_count,1)
                self.assertIn('rate limit',reason.lower())

    def test_transcript_limit_with_auth_text_never_opens_browser_sessions(self):
        session=MagicMock(); session.__enter__.return_value=session
        session.extract_info.side_effect=RuntimeError('HTTP Error 429: please sign in')
        factory=MagicMock(return_value=session)
        with TranscriptSource(factory=factory) as source:
            with self.assertRaisesRegex(SourceError,'rate_limited'):
                source.extract(BASE+'a')
        self.assertEqual(factory.call_count,1)
        self.assertNotIn('cookiesfrombrowser',factory.call_args.args[0])

    def test_transcript_stops_if_an_authenticated_attempt_hits_limit(self):
        anonymous,limited,unused=MagicMock(),MagicMock(),MagicMock()
        for session in (anonymous,limited,unused): session.__enter__.return_value=session
        anonymous.extract_info.side_effect=RuntimeError('please sign in')
        limited.extract_info.side_effect=RuntimeError('HTTP Error 429: please sign in')
        unused.extract_info.return_value=dict(id='a')
        factory=MagicMock(side_effect=[anonymous,limited,unused])
        with TranscriptSource(factory=factory) as source:
            with self.assertRaisesRegex(SourceError,'rate_limited'):
                source.extract(BASE+'a')
        self.assertEqual(factory.call_count,2)
        unused.extract_info.assert_not_called()


class HistoryProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'history.json'
        self.patch=patch('app.history.history_path',return_value=self.path)
        self.patch.start(); self.addCleanup(self.patch.stop)

    def append(self):
        from app.history import append_entry
        return append_entry(url='https://example.test/video',fmt='MP4 Video',resolution='720',
                            output_path='example.mp4',status='completed')

    def test_malformed_history_is_preserved_when_a_download_completes(self):
        for raw in (b'{broken json',b'{"unexpected":"object"}',b'[null,42]'):
            with self.subTest(raw=raw):
                self.path.write_bytes(raw)
                result=self.append()
                self.assertEqual(self.path.read_bytes(),raw)
                self.assertIs(result,False)

    def test_legacy_entries_and_new_download_are_retained(self):
        old=dict(timestamp='old',url='https://example.test/old',format='MP3')
        self.path.write_text(json.dumps([old]),encoding='utf-8')
        self.assertIs(self.append(),True)
        entries=json.loads(self.path.read_text(encoding='utf-8'))
        self.assertEqual(entries[0],old)
        self.assertEqual(entries[1]['output_path'],'example.mp4')

    def test_failed_history_publication_preserves_existing_file(self):
        self.path.write_bytes(b'[]')
        with patch('pathlib.Path.replace',side_effect=PermissionError('fixture publication refused')),\
             patch('os.replace',side_effect=PermissionError('fixture publication refused')):
            result=self.append()
        self.assertEqual(self.path.read_bytes(),b'[]')
        self.assertEqual(list(self.path.parent.iterdir()),[self.path])
        self.assertIs(result,False)


class CaptionProductionTests(unittest.TestCase):
    def test_mixed_blank_lines_remain_valid_in_timed_exports(self):
        for text in ('a\n\n \nb', 'a\n \n \nb', 'a\n\t\n\n \t\nb',
                     'a<br> <br> <br>b'):
            raw = json.dumps({'events': [{'tStartMs': 0, 'dDurationMs': 1000,
                                         'segs': [{'utf8': text}]}]})
            cues = parse_captions(raw, 'json3')
            self.assertEqual(export_captions(cues, 'txt', {}).decode(), cues[0].text+'\n')
            self.assertEqual(json.loads(export_captions(cues, 'json', {}))['cues'][0]['text'], cues[0].text)
            for fmt in ('srt', 'vtt'):
                with self.subTest(text=text, fmt=fmt):
                    self.assertEqual(parse_captions(export_captions(cues, fmt, {}), fmt),
                                     [Cue(0, 1000, 'a\nb')])

    def test_json3_paragraphs_export_as_valid_timed_cues(self):
        data = json.dumps({'events': [{'tStartMs': 0, 'dDurationMs': 1000,
                                      'segs': [{'utf8': 'First\n\nSecond'}]}]})
        cues = parse_captions(data, 'json3')
        self.assertEqual(export_captions(cues, 'txt', {}), b'First\n\nSecond\n')
        for fmt in ('vtt', 'srt'):
            with self.subTest(fmt=fmt):
                parsed = parse_captions(export_captions(cues, fmt, {}), fmt)
                self.assertEqual(parsed, [Cue(0, 1000, 'First\nSecond')])


class DownloadProductionTests(unittest.TestCase):
    def test_playlist_finds_valid_later_output_and_rejects_invalid_candidates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); output = root/'media'; output.mkdir()
            valid = output/'good.mp4'; valid.write_bytes(b'completed fixture')
            foreign = root/'outside.mp4'; foreign.write_bytes(b'outside output')
            wrong = output/'wrong.webm'; wrong.write_bytes(b'wrong container')
            invalid = [dict(id='missing'), None,
                       dict(id='foreign', requested_downloads=[dict(filepath=str(foreign))]),
                       dict(id='wrong', requested_downloads=[dict(filepath=str(wrong))])]
            for entries, expected in ((invalid+[dict(id='good')], valid), (invalid, None)):
                with self.subTest(has_completed_output=expected is not None):
                    class YDL:
                        def __init__(self, opts): pass
                        def __enter__(self): return self
                        def __exit__(self, *args): pass
                        def extract_info(self, *args, **kwargs):
                            return dict(_type='playlist', entries=entries)
                        def prepare_filename(self, info): return str(output/(info['id']+'.mp4'))
                    with patch('app.downloader_worker.resolve_ffmpeg', return_value=FFmpegInfo(found=True)), \
                         patch('app.downloader_worker.browsers_to_try', return_value=(None,)), \
                         patch('app.downloader_worker.yt_dlp.YoutubeDL', YDL):
                        success, message, result = DownloaderWorker(BASE+'playlist', output,
                                                                   'MP4 Video', 'Best', 'Best').run()
                    self.assertEqual(success, expected is not None, message)
                    self.assertEqual(result, str(expected.resolve()) if expected else None)

    def test_cancel_stops_metadata_retry_logging(self):
        from app.errors import DownloadCancelled
        from app.ydl_options import YdlLogger
        log=YdlLogger(is_cancelled=lambda:True)
        with self.assertRaises(DownloadCancelled):
            log.warning('retrying metadata after timeout')

    def test_packaged_local_javascript_runtime_is_enabled_without_remote_downloads(self):
        from app.js_runtime import resolve_js_runtimes
        from app.transcript_source import TranscriptSource
        from app.ydl_options import build_ydl_opts
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); executable=root/'tools/javascript/node.exe'
            executable.parent.mkdir(parents=True); executable.write_bytes(b'runtime fixture')
            with patch('app.js_runtime.resource_path',side_effect=lambda path:root/path), \
                 patch('app.js_runtime.shutil.which',return_value=None):
                expected={'node':{'path':str(executable)}}
                self.assertEqual(resolve_js_runtimes(),expected)
                self.assertEqual(TranscriptSource()._options()['js_runtimes'],expected)
                options=build_ydl_opts(output_dir=root,fmt='MP4 Video',video_quality='720',audio_quality='Best',ffmpeg_info=FFmpegInfo(found=False))
                self.assertEqual(options['js_runtimes'],expected)
                self.assertEqual(options['remote_components'],[])

    def test_installer_preserves_user_files_and_allows_isolated_current_user_acceptance(self):
        script=(Path(__file__).resolve().parents[1]/'installer/VideoDownloader.iss').read_text(encoding='utf-8')
        self.assertIn('PrivilegesRequiredOverridesAllowed=commandline',script)
        self.assertNotIn('[UninstallDelete]',script)

    def test_no_finished_file_cannot_be_reported_as_success(self):
        with tempfile.TemporaryDirectory() as temp:
            session = MagicMock()
            session.__enter__.return_value = session
            session.extract_info.return_value = {'id': 'a'}
            session.prepare_filename.return_value = str(Path(temp)/'missing.mp4')
            worker = DownloaderWorker(BASE+'a', Path(temp), 'MP4 Video', '720', 'Best')
            with patch('app.downloader_worker.resolve_ffmpeg', return_value=FFmpegInfo(found=True)), \
                 patch('app.downloader_worker.yt_dlp.YoutubeDL', return_value=session):
                success, message, output = worker.run()
            self.assertFalse(success)
            self.assertIsNone(output)


class CrashHandlerProductionTests(unittest.TestCase):
    def test_windowed_or_unwritable_stderr_keeps_primary_error_logged(self):
        from main import _excepthook
        failed_stream = MagicMock()
        failed_stream.write.side_effect = OSError('fixture console unavailable')
        for stream in (None, failed_stream):
            with self.subTest(stream=stream), patch('main.sys.stderr', stream), \
                 patch('main.logging.getLogger') as logger:
                error = RuntimeError('primary failure')
                _excepthook(type(error), error, None)
                logger.return_value.critical.assert_called_once_with(
                    'Uncaught exception', exc_info=(type(error), error, None))

    def test_console_traceback_remains_redacted(self):
        from main import _excepthook
        stream = io.StringIO()
        with patch('main.sys.stderr', stream), patch('main.logging.getLogger'):
            error = RuntimeError('token=CONSOLESECRET')
            _excepthook(type(error), error, None)
        self.assertIn('RuntimeError', stream.getvalue())
        self.assertNotIn('CONSOLESECRET', stream.getvalue())


class PrivacyProductionTests(unittest.TestCase):
    def test_logging_redacts_formatted_values_and_tracebacks(self):
        from app.privacy import PrivacyFilter
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.addFilter(PrivacyFilter())
        log = logging.getLogger('production-privacy-test')
        log.handlers = [handler]
        log.propagate = False
        log.setLevel(logging.DEBUG)
        try:
            log.warning('URL %s Cookie: %s', 'https://user:PASSWORD@host/video?sig=SIGNED&v=abc', 'SESSION=COOKIESECRET')
            try:
                raise RuntimeError('Authorization: Bearer BEARERSECRET')
            except RuntimeError:
                log.exception('provider failed https://cdn/video?token=TOKENSECRET')
        finally:
            log.handlers = []
            handler.close()
        output = stream.getvalue()
        for secret in ('PASSWORD', 'SIGNED', 'COOKIESECRET', 'BEARERSECRET', 'TOKENSECRET'):
            self.assertNotIn(secret, output)
        self.assertIn('provider failed', output)

    def test_friendly_errors_and_ytdlp_logs_do_not_expose_credentials(self):
        from app.errors import map_error, is_valid_url
        from app.ydl_options import YdlLogger, url_domain
        self.assertFalse(is_valid_url('https://user:pass@host/video'))
        self.assertFalse(is_valid_url('https://host:invalid/video'))
        self.assertEqual(url_domain('https://user:pass@host:443/a'), 'host')
        self.assertNotIn('SECRET', map_error(RuntimeError('failed https://host/a?token=SECRET')))
        log = MagicMock()
        YdlLogger(log).warning('Provider https://host/a?token=SECRET')
        self.assertNotIn('SECRET', str(log.warning.call_args))
