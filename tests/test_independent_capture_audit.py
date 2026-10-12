import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

capture = load('capture_readiness')
independent = load('independent_capture_audit')

class IndependentDojo(unittest.TestCase):
    def test_empty_directory_agreement(self):
        with tempfile.TemporaryDirectory() as d:
            r = independent.verify(d, capture.audit(d))
            self.assertTrue(r['independent_match'])
            self.assertFalse(r['engineering_accepted'])
    def test_full_synthetic_directory_agreement(self):
        with tempfile.TemporaryDirectory() as d:
            for n in capture.REQUIRED_FILES:
                (Path(d) / n).write_bytes(b'{}')
            r = independent.verify(d, capture.audit(d))
            self.assertTrue(r['independent_match'])
            self.assertEqual(r['certification'], 'NOT_CERTIFIED')
    def test_forged_certification_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            report = capture.audit(d)
            report['engineering_accepted'] = True
            self.assertFalse(independent.verify(d, report)['independent_match'])
    def test_forged_count_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            report = capture.audit(d)
            report['present_count'] = 7
            self.assertEqual(independent.verify(d, report)['status'], 'HOLD_MISMATCH')
    def test_forged_status_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            report = capture.audit(d)
            report['status'] = 'FILES_PRESENT_CONTENT_UNVERIFIED'
            self.assertEqual(independent.verify(d, report)['status'], 'HOLD_MISMATCH')

if __name__ == '__main__':
    unittest.main()
