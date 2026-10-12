import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SafetyTests(unittest.TestCase):
    def test_workflow_read_only_permissions(self):
        data = (ROOT / '.github/workflows/safe-hourly.yml').read_text(encoding='utf-8-sig')
        self.assertIn('contents: read', data)
        self.assertNotIn('contents: write', data)
        self.assertIn('workflow_dispatch:', data)
    def test_no_production_entrypoint(self):
        data = (ROOT / '.github/workflows/safe-hourly.yml').read_text(encoding='utf-8-sig')
        self.assertNotIn('gh pr merge', data)
        self.assertNotIn('midas', data.lower())
    def test_health_script_declares_uncertified(self):
        data = (ROOT / 'scripts/offline_health.py').read_text(encoding='utf-8-sig')
        self.assertIn('NOT_CERTIFIED', data)
        self.assertIn('V458_CANDIDATE_NOT_VENDOR_VALIDATED', data)
        self.assertIn('evidence_capture_scanned', data)

if __name__ == '__main__':
    unittest.main()
