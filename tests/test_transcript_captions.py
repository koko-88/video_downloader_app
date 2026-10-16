import json
import unittest
from app.captions import CaptionError, Cue, export_captions, parse_captions

VTT = "WEBVTT\n\n00:00:00.125 --> 00:00:02.500\nHello &amp; <b>مرحبا</b> 🌍\n\nsecond\n00:00:01.000 --> 00:00:03.999 align:start\nRepeated\n\n00:00:04.000 --> 00:00:05.000\nRepeated\n"


class CaptionTests(unittest.TestCase):
    def test_unicode_overlaps_repeated_and_entities(self):
        cues = parse_captions(VTT, 'vtt')
        self.assertEqual(cues, [Cue(125, 2500, 'Hello & مرحبا 🌍'), Cue(1000, 3999, 'Repeated'), Cue(4000, 5000, 'Repeated')])

    def test_exact_timed_goldens_and_roundtrips(self):
        cues = [Cue(125, 2500, 'Hello & مرحبا 🌍'), Cue(3_601_000, 3_602_000, '<literal>')]
        expected = '1\n00:00:00,125 --> 00:00:02,500\nHello &amp; مرحبا 🌍\n\n2\n01:00:01,000 --> 01:00:02,000\n&lt;literal&gt;\n'
        self.assertEqual(export_captions(cues, 'srt', {}).decode(), expected)
        expected_vtt = 'WEBVTT\n\n00:00:00.125 --> 00:00:02.500\nHello &amp; مرحبا 🌍\n\n01:00:01.000 --> 01:00:02.000\n&lt;literal&gt;\n'
        self.assertEqual(export_captions(cues, 'vtt', {}).decode(), expected_vtt)
        for fmt in ('srt', 'vtt'):
            self.assertEqual(parse_captions(export_captions(cues, fmt, {}), fmt), cues)

    def test_exact_txt_json_and_markdown_semantics(self):
        cues = [Cue(0, 1000, '[link](https://evil) <script> & Unicode 文')]
        provenance = dict(title='*unsafe*', language='zh', kind='manual', acquisition='captions')
        self.assertEqual(export_captions(cues, 'txt', provenance).decode(), cues[0].text + '\n')
        data = json.loads(export_captions(cues, 'json', provenance))
        self.assertEqual(data, dict(schema=1, provenance=provenance, cues=[dict(start_ms=0, end_ms=1000, text=cues[0].text)]))
        md = export_captions(cues, 'md', provenance).decode()
        self.assertTrue(md.startswith('# \\*unsafe\\*\n\n'))
        self.assertIn('[00:00:00.000] \\[link\\]\\(https://evil\\)', md)
        self.assertIn('&lt;script&gt; &amp; Unicode 文', md)

    def test_json3_non_english_and_metadata_events(self):
        raw = dict(events=[{}, dict(tStartMs=25, dDurationMs=100, segs=[dict(utf8='日本'), dict(utf8='語')])])
        self.assertEqual(parse_captions(json.dumps(raw), 'json3'), [Cue(25, 125, '日本語')])

    def test_malformed_input_is_not_silently_partial(self):
        bad = ['WEBVTT\n\n00:61:00.000 --> 00:00:01.000\nx', 'WEBVTT\n\n00:00:01.000 --> 00:00:00.000\nx', VTT + '\nBAD BLOCK', 'WEBVTT', 'garbage', 'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\n<b></b>']
        for text in bad:
            with self.subTest(text=text), self.assertRaises(CaptionError):
                parse_captions(text, 'vtt')
        for values in ((-1, 1, 'x'), (0, 0, 'x'), (0.5, 1, 'x'), (True, 1, 'x')):
            with self.assertRaises(CaptionError):
                Cue(*values)
        with self.assertRaises(CaptionError):
            parse_captions(b'\xff', 'srt')

    def test_vtt_notes_header_metadata_and_bom(self):
        text = '\ufeffWEBVTT\nKind: captions\n\nNOTE ignored\nanything\n\nSTYLE\n::cue {color:red}\n\n00:00:00.000 --> 00:00:01.000\n<b>ok</b>'
        self.assertEqual(parse_captions(text, 'vtt'), [Cue(0, 1000, 'ok')])

    def test_large_output_and_size_limit(self):
        cues = [Cue(i * 1000, (i+1)*1000, '文字 ' * 100) for i in range(3000)]
        self.assertEqual(len(json.loads(export_captions(cues, 'json', {}))['cues']), 3000)
        with self.assertRaises(CaptionError):
            parse_captions(b'x' * (16*1024*1024+1), 'vtt')
