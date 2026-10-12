"""Metadata-only triage for a local, isolated Civil NX probe folder.

No captured content is read, transmitted, parsed, or uploaded. File presence
never proves solver completion, correct model identity, or numerical validity.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import stat
import sys

# Names traced to V4.58 candidate/offline_midas_probe_audit.py.
# This is a candidate *local capture* contract, NOT a vendor API schema.
REQUIRED_FILES = (
    'summary.json', 'request_without_credentials.json',
    'response_original_bytes.bin', 'elem_before.bin', 'stld_before.bin',
    'elem_after.bin', 'stld_after.bin',
)
MAX_FILE_BYTES = 2_097_152


def audit(folder: str | Path) -> dict:
    """Return only allowlisted filenames and reason codes; fail closed."""
    result = {
        'status': 'HOLD', 'contract': 'V458_CANDIDATE_NOT_VENDOR_VALIDATED',
        'required_count': len(REQUIRED_FILES), 'present_count': 0,
        'missing': [], 'invalid': [], 'civil_nx_contacted': False,
        'numeric_results_verified': False, 'solver_completion_verified': False,
        'model_identity_verified': False, 'engineering_accepted': False,
        'certification': 'NOT_CERTIFIED',
    }
    try:
        root = Path(folder)
        mode = root.lstat().st_mode
        if not stat.S_ISDIR(mode) or root.is_symlink():
            result['status'] = 'HOLD_UNSAFE_DIRECTORY'
            return result
        for name in REQUIRED_FILES:
            item = root / name
            try:
                meta = item.lstat()
            except FileNotFoundError:
                result['missing'].append(name)
                continue
            if not stat.S_ISREG(meta.st_mode) or item.is_symlink():
                result['invalid'].append(name + ':NOT_REGULAR')
            elif meta.st_size == 0 or meta.st_size > MAX_FILE_BYTES:
                result['invalid'].append(name + ':SIZE_HOLD')
            else:
                result['present_count'] += 1
        if result['invalid']:
            result['status'] = 'HOLD_INVALID_FILE_METADATA'
        elif result['missing']:
            result['status'] = 'HOLD_MISSING_CAPTURE_FILES'
        else:
            result['status'] = 'FILES_PRESENT_CONTENT_UNVERIFIED'
    except (OSError, ValueError, TypeError):
        result['status'] = 'HOLD_UNREADABLE_DIRECTORY'
    return result


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python scripts/capture_readiness.py <local-isolated-folder>')
    print(json.dumps(audit(sys.argv[1]), indent=2))
