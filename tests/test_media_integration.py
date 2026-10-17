"""Real local HTTP and FFmpeg checks for requested video containers."""
import functools
import json
import subprocess
import tempfile
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app.downloader_worker import DownloaderWorker
from app.ffmpeg_resolver import resolve_ffmpeg


@unittest.skipUnless(resolve_ffmpeg().found, 'Local FFmpeg required for media integration')
class MediaIntegrationTests(unittest.TestCase):
    def test_progressive_webm_is_remuxed_to_requested_mp4(self):
        runtime=resolve_ffmpeg()
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); original=root/'clip.webm'; output=root/'output'; output.mkdir()
            subprocess.run([str(runtime.ffmpeg_path),'-v','error','-f','lavfi','-i',
                            'color=c=black:s=16x16:r=5','-t','0.4','-c:v','libvpx-vp9',str(original)],
                           check=True,capture_output=True,timeout=30)
            class Handler(SimpleHTTPRequestHandler):
                def log_message(self,*args): pass
            handler=functools.partial(Handler,directory=str(root))
            server=ThreadingHTTPServer(('127.0.0.1',0),handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
            try:
                worker=DownloaderWorker(f'http://127.0.0.1:{server.server_port}/clip.webm',output,
                                        'MP4 Video','Best','Best')
                success,message,result=worker.run()
                self.assertTrue(success,message)
                self.assertEqual(Path(result).suffix,'.mp4')
                probe=json.loads(subprocess.check_output([str(runtime.ffprobe_path),'-v','error',
                                 '-show_entries','format=format_name','-of','json',result],text=True,timeout=15))
                self.assertIn('mp4',probe['format']['format_name'])
            finally:
                server.shutdown(); server.server_close(); thread.join(2)
