"""Offline-only Bridge Buddy health report. Never contacts Civil NX or a broker."""
import datetime
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = [
    "civil_nx_post_response.json", "civil_nx_solver_status.json",
    "civil_nx_model_identity.json", "civil_nx_units.json",
    "civil_nx_result_table.json", "civil_nx_request_metadata.json",
    "civil_nx_provenance.json",
]
# Placeholder evidence labels: update only after inspecting actual source contract.
report = {
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "mode": "offline_read_only",
    "civil_nx_network_access": False,
    "production_promotion": False,
    "certification": "NOT_CERTIFIED",
    "evidence_contract": "PLACEHOLDER_NOT_VALIDATED",
    "expected_capture_labels": EXPECTED,
    "notes": "This is a starter health check, not a verified Civil NX extraction test.",
}
path = ROOT / "reports" / "health.json"
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
