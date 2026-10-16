import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import build_exe


class PackagingTests(unittest.TestCase):
    def test_existing_outputs_are_never_deleted(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root/'build_logs') as temporary:
            destination=Path(temporary); (destination/'dist').mkdir()
            sentinel=destination/'dist'/'USER-DATA'; sentinel.write_bytes(b'preserve')
            with patch('build_exe.subprocess.run') as process:
                result=build_exe.main(['--output-root',str(destination)])
            self.assertEqual(result,1); process.assert_not_called()
            self.assertEqual(sentinel.read_bytes(),b'preserve')

    def test_build_outside_workspace_refused(self):
        root=Path(__file__).resolve().parents[1]
        with patch('build_exe.subprocess.run') as process:
            result=build_exe.main(['--output-root',str(root.parent/'outside-build')])
        self.assertEqual(result,1); process.assert_not_called()

    def test_installer_uses_selected_feature_build_and_preserves_existing_setup(self):
        import build_installer
        from types import SimpleNamespace
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root/'build_logs') as temporary:
            source=Path(temporary)/'feature source'; source.mkdir(); (source/'VideoDownloader.exe').write_bytes(b'fixture')
            output=Path(temporary)/'setup output'
            def compiler(command,**kwargs):
                self.assertIn('/DBuildSource='+str(source),command)
                self.assertIn('/DBuildOutput='+str(output),command)
                (output/build_installer.INSTALLER_NAME).write_bytes(b'compiler fixture')
                return SimpleNamespace(returncode=0)
            with patch.object(build_installer,'find_iscc',return_value=Path('ISCC.exe')), patch.object(build_installer.subprocess,'run',side_effect=compiler) as process:
                self.assertEqual(build_installer.main(['--source-dir',str(source),'--output-dir',str(output)]),0)
                self.assertEqual(process.call_count,1)
                self.assertEqual(build_installer.main(['--source-dir',str(source),'--output-dir',str(output)]),1)
                self.assertEqual(process.call_count,1)
