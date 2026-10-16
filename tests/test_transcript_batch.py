import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from app.captions import Cue
from app.transcript_batch import Choices, TranscriptBatch, batch_lock, contained
from app.transcript_source import Cancelled, SourceError

BASE = 'https://www.youtube.com/watch?v='

def video(id, **extras):
    return dict(id=id, extractor_key='Youtube', title='Title '+id, webpage_url=BASE+id, **extras)


def pages(ids, reached):
    for page in range(3):
        reached.append(page)
        for id in ids[page::3]:
            yield dict(_type='url',ie_key='Youtube',id=id,url=BASE+id,title='Title '+id)


class FixtureSource:
    metadata = {}
    outcomes = {}
    extracted = []
    uncertainty = False
    on_caption = None
    def __init__(self,cancelled): self.cancelled=cancelled; self.log=SimpleNamespace(uncertain=self.uncertainty)
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def extract(self,url,ie_key=None):
        self.extracted.append(url)
        result=self.metadata[url]
        if isinstance(result,Exception): raise result
        return result() if callable(result) else copy.deepcopy(result)
    def captions(self,info,language,preference):
        if self.cancelled(): raise Cancelled()
        if type(self).on_caption: type(self).on_caption(info)
        outcome=self.outcomes.get(info['id'])
        if isinstance(outcome,Exception): raise outcome
        return [Cue(0,1000,'Hello مرحبا')], dict(language=language,kind='manual',representation='vtt',acquisition='captions')


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        FixtureSource.metadata={BASE+'a':video('a'),BASE+'b':video('b')}
        FixtureSource.outcomes={}; FixtureSource.extracted=[]; FixtureSource.uncertainty=False; FixtureSource.on_caption=None
    def batch(self,urls=None,**kwargs):
        return TranscriptBatch(urls or [BASE+'a'],self.root,source_factory=FixtureSource,**kwargs)
    def assert_totals(self,data):
        self.assertEqual(data['counts']['discovered'],sum(data['counts'][s] for s in ('succeeded','caption_absent','inaccessible','failed','pending')))

    def test_multipage_nested_exhaustion_and_mixed_dedup(self):
        reached=[]; ids=list('abcdefghi')
        playlist='https://youtube.com/playlist?list=p'
        FixtureSource.metadata[playlist]=lambda:dict(_type='playlist',extractor_key='YoutubeTab',id='p',playlist_count=9,entries=pages(ids,reached))
        for id in ids: FixtureSource.metadata[BASE+id]=video(id)
        data=self.batch([playlist,BASE+'a',playlist]).run()
        self.assertEqual(reached,[0,1,2,0,1,2])
        self.assertEqual(data['counts']['succeeded'],9)
        self.assertTrue(all(i['state']=='complete' for i in data['inputs']))
        a=next(v for v in data['videos'].values() if v['video_id']=='a')
        self.assertEqual(a['inputs'],[0,1,2]); self.assertEqual(a['attempts'],1)
        self.assert_totals(data)

    def test_nested_playlist_empty_and_unavailable_visible(self):
        url='https://youtube.com/playlist?list=nested'
        FixtureSource.metadata[url]=dict(_type='playlist',id='outer',extractor_key='YoutubeTab',entries=[dict(_type='playlist',id='inner',extractor_key='YoutubeTab',entries=[video('a'),video('private',availability='private')]),dict(_type='playlist',id='empty',entries=[])])
        data=self.batch([url]).run()
        self.assertEqual(data['counts']['succeeded'],1); self.assertEqual(data['counts']['inaccessible'],1)
        self.assertEqual(data['inputs'][0]['state'],'complete'); self.assert_totals(data)
        FixtureSource.metadata[url]=dict(_type='playlist',id='p',entries=[])
        fresh=TranscriptBatch([url],self.root/'empty',source_factory=FixtureSource).run()
        self.assertEqual(fresh['counts']['discovered'],0); self.assertEqual(fresh['inputs'][0]['state'],'complete')

    def test_interrupted_iterator_preserves_partial_and_resumes(self):
        url='https://youtube.com/playlist?list=p'
        def interrupted():
            yield video('a')
            raise SourceError('network_error')
        FixtureSource.metadata[url]=lambda:dict(_type='playlist',id='p',entries=interrupted())
        batch=self.batch([url]); data=batch.run()
        self.assertEqual(data['inputs'][0]['state'],'incomplete'); self.assertEqual(data['counts']['succeeded'],1)
        FixtureSource.metadata[url]=dict(_type='playlist',id='p',entries=[video('a'),video('b')])
        data=batch.run(); self.assertEqual(data['inputs'][0]['state'],'complete')
        self.assertEqual(data['counts']['succeeded'],2)
        self.assertEqual(sorted(v['attempts'] for v in data['videos'].values()),[1,1])

    def test_warning_and_expected_count_mismatch_never_complete(self):
        FixtureSource.uncertainty=True
        data=self.batch().run(); self.assertEqual(data['inputs'][0]['state'],'incomplete')
        FixtureSource.uncertainty=False
        url='https://youtube.com/playlist?list=p'
        FixtureSource.metadata[url]=dict(_type='playlist',id='p',playlist_count=3,entries=[video('a')])
        data=self.batch([url]).run(); self.assertEqual(data['inputs'][0]['state'],'incomplete')
        self.assertEqual(data['inputs'][0]['reason'],'collection_count_mismatch')

    def test_cancel_mid_processing_resume_and_idempotent_rerun(self):
        cancelled=[False]
        def callback(stage,data):
            if stage=='Processed': cancelled[0]=True
        batch=self.batch([BASE+'a',BASE+'b'],cancelled=lambda:cancelled[0],progress=callback,choices=Choices(formats=('md','txt','json','srt','vtt')))
        data=batch.run(); self.assertTrue(data['cancelled'])
        self.assertEqual((data['counts']['succeeded'],data['counts']['pending']),(1,1))
        files=list(batch.root.rglob('transcript.*')); before={p:p.read_bytes() for p in files}
        cancelled[0]=False; batch.progress=lambda *args:None
        data=batch.run(); self.assertEqual(data['counts']['succeeded'],2)
        self.assertTrue(all(p.read_bytes()==content for p,content in before.items()))
        self.assertEqual(len(list(batch.root.rglob('transcript.*'))),10)
        FixtureSource.extracted=[]; data=batch.run(); self.assertEqual(FixtureSource.extracted,[])
        self.assertEqual(sorted(v['attempts'] for v in data['videos'].values()),[1,1]); self.assert_totals(data)

    def test_cancel_during_scan_resumes_without_loss(self):
        cancel=[False]; url='https://youtube.com/playlist?list=p'
        def entries():
            yield video('a'); cancel[0]=True; yield video('b')
        FixtureSource.metadata[url]=lambda:dict(_type='playlist',id='p',entries=entries())
        batch=self.batch([url],cancelled=lambda:cancel[0]); data=batch.run()
        self.assertEqual(data['inputs'][0]['state'],'incomplete'); self.assertEqual(data['counts']['pending'],1)
        cancel[0]=False; FixtureSource.metadata[url]=dict(_type='playlist',id='p',entries=[video('a'),video('b')])
        self.assertEqual(batch.run()['counts']['succeeded'],2)

    def test_failed_only_retry_and_absent_asr_are_distinct(self):
        FixtureSource.outcomes={'a':SourceError('network_error'),'b':SourceError('caption_absent','caption_absent')}
        batch=self.batch([BASE+'a',BASE+'b'],choices=Choices(local_asr=True)); data=batch.run()
        self.assertEqual((data['counts']['failed'],data['counts']['caption_absent']),(1,1))
        absent=next(v for v in data['videos'].values() if v['video_id']=='b')
        self.assertIn('local_asr_backend_model_unavailable',absent['reason'])
        FixtureSource.outcomes={}; data=batch.run(retry_failed=True)
        self.assertEqual((data['counts']['succeeded'],data['counts']['caption_absent']),(1,1))
        self.assertEqual(next(v for v in data['videos'].values() if v['video_id']=='a')['attempts'],2)
        self.assertEqual(absent['attempts'],1)

    def test_changed_outputs_never_overwritten_or_claimed_success(self):
        batch=self.batch(); data=batch.run(); record=next(iter(data['videos'].values()))
        output=batch.root/record['outputs'][0]['path']; output.write_text('USER EDIT',encoding='utf-8')
        data=batch.run(); self.assertEqual(data['counts']['failed'],1)
        self.assertEqual(next(iter(data['videos'].values()))['reason'],'output_integrity_changed')
        data=batch.run(retry_failed=True); self.assertEqual(data['counts']['failed'],1)
        self.assertEqual(output.read_text(),'USER EDIT')

    def test_cancelled_export_reuses_identical_partial_files(self):
        cancel=[False]; batch=self.batch(cancelled=lambda:cancel[0],choices=Choices(formats=('txt','srt')))
        original=batch._write_output
        def write(relative,data): original(relative,data); cancel[0]=True
        batch._write_output=write; data=batch.run()
        self.assertEqual(data['counts']['pending'],1)
        batch._write_output=original; cancel[0]=False
        self.assertEqual(batch.run()['counts']['succeeded'],1)
        self.assertEqual(len(list(batch.root.rglob('transcript.*'))),2)

    def test_hostile_title_confined_and_path_tamper_preserved(self):
        FixtureSource.metadata[BASE+'a']=video('a'); FixtureSource.metadata[BASE+'a']['title']='CON/../../x:*?\n<evil>'
        batch=self.batch(); data=batch.run()
        self.assertEqual(data['counts']['succeeded'],1)
        record=next(iter(data['videos'].values())); relative=record['outputs'][0]['path']
        self.assertTrue((batch.root/relative).resolve().is_relative_to(batch.root.resolve()))
        self.assertNotIn('..',Path(relative).parts)
        record['outputs'][0]['path']='../../user.txt'; batch.save(); prior=batch.manifest_path.read_bytes()
        with self.assertRaisesRegex(SourceError,'unsafe_output_path'): batch.run()
        self.assertEqual(batch.manifest_path.read_bytes(),prior)
        for path in ('../outside','C:/outside','/outside'):
            with self.assertRaises(SourceError): contained(batch.root,path)

    def test_batch_lock_and_corrupt_manifest(self):
        batch=self.batch()
        with batch_lock(batch.root):
            with self.assertRaisesRegex(SourceError,'batch_already_running'): batch.run()
        # OS releases the lock; retained lock file does not prevent resume.
        self.assertEqual(batch.run()['counts']['succeeded'],1)
        batch.manifest_path.write_text('BROKEN',encoding='utf-8')
        with self.assertRaisesRegex(SourceError,'invalid_manifest_preserved'): batch.run()
        self.assertEqual(batch.manifest_path.read_text(),'BROKEN')

    def test_per_input_failures_do_not_stop_valid_input(self):
        invalid='https://example.invalid/?token=SECRET'
        FixtureSource.metadata[invalid]=SourceError('invalid_or_credential_url')
        data=self.batch([invalid,BASE+'a']).run()
        self.assertEqual(data['inputs'][0]['state'],'failed'); self.assertEqual(data['counts']['succeeded'],1)
        self.assertNotIn('SECRET',json.dumps(data)); self.assert_totals(data)

    def test_unidentified_entry_does_not_stop_remaining_accessible_videos(self):
        url='https://youtube.com/playlist?list=p'
        FixtureSource.metadata[url]=dict(_type='playlist',id='p',entries=[None,video('a'),video('b')])
        data=self.batch([url]).run()
        self.assertEqual(data['counts']['succeeded'],2)
        self.assertEqual(data['counts']['inaccessible'],1)
        self.assertEqual(data['inputs'][0]['state'],'incomplete')
        self.assert_totals(data)

    def test_junction_or_symlink_escape_is_refused(self):
        import os
        batch=self.batch(); outside=self.root/'outside'; outside.mkdir()
        link=batch.root/'escape'
        if os.name=='nt':
            import _winapi
            _winapi.CreateJunction(str(outside),str(link))
        else:
            link.symlink_to(outside,target_is_directory=True)
        with self.assertRaisesRegex(SourceError,'unsafe_output_path'):
            contained(batch.root,'escape/user.txt')
        self.assertFalse((outside/'user.txt').exists())
