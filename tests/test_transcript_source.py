import contextlib
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import MagicMock, patch
from app.transcript_source import (Cancelled, ScanLog, SourceError, TranscriptSource,
                                   classified_error, normalize_target, public_url)

TEXT = 'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nمرحبا &amp; hello\n'


class SourceTests(unittest.TestCase):
    def test_channel_scope_and_input_validation(self):
        for url in ('https://youtube.com/@name', 'https://www.youtube.com/channel/UCabc/'):
            self.assertTrue(normalize_target(url).endswith('/videos'))
        for path in ('/watch?v=abc', '/playlist?list=abc', '/@name/shorts', '/@name/streams'):
            self.assertEqual(normalize_target('https://youtube.com'+path), 'https://youtube.com'+path)
        for url in ('file:///etc/passwd', 'https://user:secret@youtube.com/a', 'https://youtube.com/a?token=secret', 'https://x:bad/a'):
            with self.assertRaises(SourceError): normalize_target(url)
        self.assertEqual(public_url('https://user:pass@site/a?v=x&sig=SECRET#secret'), 'https://site/a?v=x')

    def test_raw_extraction_has_no_media_processing(self):
        session = MagicMock()
        session.__enter__.return_value = session
        factory = MagicMock(return_value=session)
        session.extract_info.return_value = dict(id='abc')
        with TranscriptSource(factory=factory) as source:
            self.assertEqual(source.extract('https://youtube.com/watch?v=abc'), dict(id='abc'))
        session.extract_info.assert_called_once_with('https://youtube.com/watch?v=abc', download=False, process=False, ie_key=None)
        self.assertTrue(factory.call_args.args[0]['skip_download'])
        self.assertFalse(factory.call_args.args[0]['ignoreerrors'])
        with TranscriptSource(factory=factory) as source:
            with self.assertRaisesRegex(SourceError, 'unsupported_url'):
                source.extract('https://example.invalid/arbitrary-page')

    def test_language_precedence_and_provenance(self):
        info = dict(subtitles={'ar': [dict(ext='vtt', data=TEXT)]}, automatic_captions={'ar': [dict(ext='srt', data='1\n00:00:00,000 --> 00:00:01,000\nauto')]})
        source = TranscriptSource()
        for preference, expected in (('manual-first','manual'),('auto-first','automatic'),('manual-only','manual'),('auto-only','automatic')):
            cues, track = source.captions(info, 'ar', preference)
            self.assertEqual(track['kind'], expected)
            self.assertEqual(track['language'], 'ar')
            self.assertEqual(track['acquisition'], 'captions')
        with self.assertRaisesRegex(SourceError, 'language_unavailable'):
            source.captions(info, 'en', 'manual-first')
        with self.assertRaises(SourceError) as absent:
            source.captions({}, 'en', 'manual-first')
        self.assertEqual(absent.exception.status, 'caption_absent')
        with self.assertRaisesRegex(SourceError, 'unsupported_caption_representation'):
            source.captions(dict(subtitles={'en':[dict(ext='ttml')]}), 'en', 'manual-first')

    def test_warning_and_feed_loop_are_incomplete_signals(self):
        log = ScanLog(lambda: False)
        log.debug('Detected YouTube feed looping - assuming end of feed.')
        self.assertTrue(log.uncertain)
        log = ScanLog(lambda: False)
        log.warning('remote problem with SECRET')
        self.assertTrue(log.uncertain)
        with self.assertRaises(Cancelled): ScanLog(lambda: True).debug('request')

    def test_error_classification_does_not_retain_secrets(self):
        for error, reason, status in [('HTTP 429 https://x?sig=SECRET','rate_limited','failed'), ('private video cookie=SECRET','inaccessible','inaccessible'), ('connection timeout SECRET','network_error','failed'), ('weird SECRET','extraction_error','failed')]:
            result = classified_error(RuntimeError(error))
            self.assertEqual((result.reason,result.status), (reason,status))
            self.assertNotIn('SECRET', str(result))

    def test_cancel_before_fetch_and_unsafe_caption_url(self):
        source = TranscriptSource(cancelled=lambda: True)
        with self.assertRaises(Cancelled): source.captions({}, 'en','manual-first')
        source = TranscriptSource()
        for url in ('file:///secret','data:text/plain,secret'):
            with self.assertRaisesRegex(SourceError,'unsafe_caption_url'):
                source.captions(dict(subtitles={'en':[dict(ext='vtt',url=url)]}), 'en','manual-first')

    def test_actual_http_transport_and_subtitle_headers(self):
        observed=[]
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                observed.append(self.headers.get('X-Test'))
                data=TEXT.encode()
                self.send_response(200); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
            def log_message(self,*args): pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            with TranscriptSource() as source:
                info=dict(subtitles={'ar':[dict(ext='vtt',url=f'http://127.0.0.1:{server.server_port}/captions?sig=SECRET',http_headers={'X-Test':'works'})]})
                cues,track=source.captions(info,'ar','manual-first')
                self.assertEqual(cues[0].text,'مرحبا & hello')
                self.assertNotIn('SECRET',json.dumps(track))
            self.assertEqual(observed,['works'])
        finally:
            server.shutdown(); server.server_close(); thread.join(2)

    def test_browser_fallback_only_on_auth_failure(self):
        first, second = MagicMock(), MagicMock()
        first.__enter__.return_value=first; second.__enter__.return_value=second
        first.extract_info.side_effect=RuntimeError('please sign in')
        second.extract_info.return_value=dict(id='x')
        factory=MagicMock(side_effect=[first,second])
        with TranscriptSource(factory=factory) as source:
            self.assertEqual(source.extract('https://youtube.com/watch?v=x')['id'],'x')
        self.assertEqual(factory.call_args.args[0]['cookiesfrombrowser'],('edge',))


class InstalledYoutubeContinuationTests(unittest.TestCase):
    def test_installed_extractor_follows_real_continuation_shapes(self):
        from yt_dlp.extractor.youtube import YoutubeTabIE
        from yt_dlp import YoutubeDL
        calls=[]
        def entry(id):
            return {'videoRenderer': {'videoId': id, 'title': {'runs': [{'text': id}]}}}
        def continuation(token):
            return {'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': token}}}}
        class Extractor(YoutubeTabIE):
            def generate_api_headers(self, **kwargs): return {}
            def _extract_visitor_data(self, *args): return None
            def _extract_response(self, **kwargs):
                calls.append(kwargs['query']['continuation'])
                contents = ([entry('bbbbbbbbbbb'), continuation('page3')] if len(calls)==1 else [entry('ccccccccccc')])
                return {'onResponseReceivedActions': [{'appendContinuationItemsAction': {'continuationItems': contents}}]}
        tab={'content': {'richGridRenderer': {'contents': [{'richItemRenderer': {'content': entry('aaaaaaaaaaa')}}, continuation('page2')]}}}
        with YoutubeDL({'quiet':True, 'cachedir':False}) as ydl:
            extractor=Extractor(ydl)
            result=list(extractor._entries(tab,'fixture',{},None,None))
        self.assertEqual([v['id'] for v in result],['aaaaaaaaaaa','bbbbbbbbbbb','ccccccccccc'])
        self.assertEqual(calls,['page2','page3'])

    def test_network_permission_is_failed_network_not_site_inaccessible(self):
        result=classified_error(PermissionError('[WinError 10013] permission denied'))
        self.assertEqual((result.reason,result.status),('network_access_denied','failed'))
