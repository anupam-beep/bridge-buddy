"""Bridge Dojo negative controls for offline evidence readiness."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('capture_readiness', ROOT / 'scripts' / 'capture_readiness.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CaptureDojo(unittest.TestCase):
    def _make(self, root, skip=()):
        for name in module.REQUIRED_FILES:
            if name not in skip:
                (root / name).write_bytes(b'{"synthetic":true}')

    def _locked(self, result):
        self.assertFalse(result['civil_nx_contacted'])
        self.assertFalse(result['numeric_results_verified'])
        self.assertFalse(result['solver_completion_verified'])
        self.assertFalse(result['model_identity_verified'])
        self.assertFalse(result['engineering_accepted'])
        self.assertEqual(result['certification'], 'NOT_CERTIFIED')

    def test_empty_directory_holds(self):
        with tempfile.TemporaryDirectory() as d:
            r = module.audit(d)
            self.assertEqual(r['status'], 'HOLD_MISSING_CAPTURE_FILES')
            self.assertEqual(len(r['missing']), 7)
            self._locked(r)

    def test_partial_capture_holds(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            self._make(p, skip=('response_original_bytes.bin',))
            r = module.audit(p)
            self.assertEqual(r['status'], 'HOLD_MISSING_CAPTURE_FILES')
            self.assertEqual(r['missing'], ['response_original_bytes.bin'])
            self._locked(r)

    def test_complete_metadata_never_certifies(self):
        with tempfile.TemporaryDirectory() as d:
            self._make(Path(d))
            r = module.audit(d)
            self.assertEqual(r['status'], 'FILES_PRESENT_CONTENT_UNVERIFIED')
            self.assertEqual(r['present_count'], 7)
            self._locked(r)

    def test_zero_length_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            self._make(p)
            (p / 'summary.json').write_bytes(b'')
            r = module.audit(p)
            self.assertEqual(r['status'], 'HOLD_INVALID_FILE_METADATA')
            self._locked(r)

    def test_oversize_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            self._make(p)
            with (p / 'summary.json').open('wb') as f:
                f.truncate(module.MAX_FILE_BYTES + 1)
            r = module.audit(p)
            self.assertEqual(r['status'], 'HOLD_INVALID_FILE_METADATA')
            self._locked(r)

    def test_missing_folder_holds(self):
        with tempfile.TemporaryDirectory() as d:
            r = module.audit(Path(d) / 'nonexistent')
            self.assertEqual(r['status'], 'HOLD_UNREADABLE_DIRECTORY')
            self._locked(r)

    def test_file_as_folder_holds(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'notfolder'
            p.write_bytes(b'x')
            r = module.audit(p)
            self.assertEqual(r['status'], 'HOLD_UNSAFE_DIRECTORY')
            self._locked(r)

    def test_symlink_file_holds_when_supported(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            self._make(p)
            (p / 'summary.json').unlink()
            try:
                (p / 'summary.json').symlink_to(p / 'stld_before.bin')
            except (OSError, NotImplementedError):
                self.skipTest('symlink creation unavailable')
            r = module.audit(p)
            self.assertEqual(r['status'], 'HOLD_INVALID_FILE_METADATA')
            self._locked(r)

    def test_directory_symlink_holds_when_supported(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            q = p / 'link'
            try:
                q.symlink_to(p, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('symlink creation unavailable')
            r = module.audit(q)
            self.assertEqual(r['status'], 'HOLD_UNSAFE_DIRECTORY')
            self._locked(r)

    def test_does_not_echo_sensitive_content_or_path(self):
        with tempfile.TemporaryDirectory(prefix='secret_token_') as d:
            p = Path(d)
            self._make(p)
            (p / 'summary.json').write_bytes(b'gho_PRIVATE_SAMPLE_DO_NOT_PRINT')
            serialized = json.dumps(module.audit(p))
            self.assertNotIn('PRIVATE_SAMPLE', serialized)
            self.assertNotIn('secret_token_', serialized)
            self._locked(json.loads(serialized))

    def test_contract_names_are_seven_v458_files(self):
        self.assertEqual(module.REQUIRED_FILES, (
            'summary.json', 'request_without_credentials.json',
            'response_original_bytes.bin', 'elem_before.bin', 'stld_before.bin',
            'elem_after.bin', 'stld_after.bin',
        ))

if __name__ == '__main__':
    unittest.main()
