"""Independent metadata cross-check; never certifies original Civil NX results."""
from __future__ import annotations
import os
import stat
from pathlib import Path

EXPECTED = (
    'summary.json', 'request_without_credentials.json',
    'response_original_bytes.bin', 'elem_before.bin', 'stld_before.bin',
    'elem_after.bin', 'stld_after.bin',
)
LIMIT = 2_097_152


def verify(folder: str | Path, claimed: object) -> dict:
    verdict = {'status': 'HOLD', 'independent_match': False,
               'engineering_accepted': False, 'certification': 'NOT_CERTIFIED'}
    if type(claimed) is not dict or claimed.get('engineering_accepted') is not False or claimed.get('certification') != 'NOT_CERTIFIED':
        return verdict
    try:
        root = os.fspath(folder)
        root_stat = os.lstat(root)
        if not stat.S_ISDIR(root_stat.st_mode):
            expected_status, present, missing, invalid = 'HOLD_UNSAFE_DIRECTORY', 0, [], []
        else:
            present, missing, invalid = 0, [], []
            for name in EXPECTED:
                path = os.path.join(root, name)
                try:
                    st = os.lstat(path)
                except FileNotFoundError:
                    missing.append(name)
                    continue
                if not stat.S_ISREG(st.st_mode):
                    invalid.append(name + ':NOT_REGULAR')
                elif st.st_size < 1 or st.st_size > LIMIT:
                    invalid.append(name + ':SIZE_HOLD')
                else:
                    present += 1
            expected_status = ('HOLD_INVALID_FILE_METADATA' if invalid else
                               'HOLD_MISSING_CAPTURE_FILES' if missing else
                               'FILES_PRESENT_CONTENT_UNVERIFIED')
    except (OSError, ValueError, TypeError):
        expected_status, present, missing, invalid = 'HOLD_UNREADABLE_DIRECTORY', 0, [], []
    expected = {'status': expected_status, 'present_count': present,
                'missing': missing, 'invalid': invalid}
    verdict['independent_match'] = all(claimed.get(k) == v for k, v in expected.items())
    verdict['status'] = 'INDEPENDENT_METADATA_MATCH_NOT_CERTIFIED' if verdict['independent_match'] else 'HOLD_MISMATCH'
    return verdict
