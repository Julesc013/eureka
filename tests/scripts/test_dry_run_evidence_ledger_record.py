import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class EvidenceLedgerDryRunTests(unittest.TestCase):
    def test_dry_run_json_validates(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/dry_run_evidence_ledger_record.py", "--label", "Windows XP compatibility evidence example", "--evidence-kind", "compatibility_observation", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertFalse(payload["no_truth_guarantees"]["accepted_as_truth"])
        self.assertFalse(payload["no_runtime_guarantees"]["ledger_write_performed"])
        self._validate(payload)

    def test_private_label_redacted(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/dry_run_evidence_ledger_record.py", "--label", "evidence C:\\Users\\Alice\\private.txt", "--evidence-kind", "compatibility_observation", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "rejected_future")
        self.assertEqual(payload["evidence_identity"]["canonical_evidence_label"], "<redacted-evidence-ledger-label>")
        self._validate(payload)

    def _validate(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EVIDENCE_LEDGER_RECORD.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run([sys.executable, "scripts/validate_evidence_ledger_record.py", "--record", str(path), "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")


if __name__ == "__main__":
    unittest.main()
