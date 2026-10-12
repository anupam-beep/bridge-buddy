"""Offline-only Bridge Buddy health report. No Civil NX contact."""
import datetime
import json
import pathlib
from capture_readiness import REQUIRED_FILES

ROOT = pathlib.Path(__file__).resolve().parents[1]
report = {
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'mode': 'offline_read_only',
    'civil_nx_network_access': False,
    'production_promotion': False,
    'certification': 'NOT_CERTIFIED',
    'evidence_contract': 'V458_CANDIDATE_NOT_VENDOR_VALIDATED',
    'expected_capture_labels': list(REQUIRED_FILES),
    'evidence_capture_scanned': False,
    'civil_nx_result_extraction': 'UNRESOLVED',
    'matrix_skill': 'CANDIDATE_ONLY_NOT_CERTIFIED',
    'notes': 'Only an offline contract inventory. No original Civil NX capture was read or verified.',
}
path = ROOT / 'reports' / 'health.json'
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
