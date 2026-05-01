import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "evidence_ledger" / "minimal_compatibility_evidence_observation_v0" / "EVIDENCE_LEDGER_RECORD.json"
ABSENCE = ROOT / "examples" / "evidence_ledger" / "minimal_absence_evidence_observation_v0" / "EVIDENCE_LEDGER_RECORD.json"


class EvidenceLedgerRecordValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/validate_evidence_ledger_record.py", "--all-examples"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/validate_evidence_ledger_record.py", "--all-examples", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 3)

    def test_examples_encode_truth_and_review_boundaries(self) -> None:
        for path in sorted((ROOT / "examples" / "evidence_ledger").glob("*/EVIDENCE_LEDGER_RECORD.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(payload["no_truth_guarantees"]["accepted_as_truth"])
            self.assertTrue(payload["confidence"]["confidence_not_truth"])
            self.assertTrue(payload["review"]["promotion_policy_required"])
            self.assertTrue(payload["review"]["master_index_review_required"])
            self.assertFalse(payload["conflicts"]["destructive_merge_allowed"])
            for field in ("evidence_ledger_runtime_implemented", "ledger_write_performed", "live_source_called", "external_calls_performed", "telemetry_exported", "credentials_used"):
                self.assertFalse(payload["no_runtime_guarantees"][field], field)
            for field in ("source_cache_mutated", "candidate_index_mutated", "public_index_mutated", "local_index_mutated", "master_index_mutated"):
                self.assertFalse(payload["no_mutation_guarantees"][field], field)

    def test_absence_example_does_not_claim_global_absence(self) -> None:
        payload = json.loads(ABSENCE.read_text(encoding="utf-8"))
        self.assertEqual(payload["claim"]["claim_type"], "scoped_absence")
        self.assertFalse(payload["claim"]["global_absence_claimed"])

    def test_negative_flags_fail(self) -> None:
        for section, field in (
            ("no_truth_guarantees", "accepted_as_truth"),
            ("no_runtime_guarantees", "evidence_ledger_runtime_implemented"),
            ("no_runtime_guarantees", "ledger_write_performed"),
            ("no_runtime_guarantees", "live_source_called"),
            ("no_mutation_guarantees", "master_index_mutated"),
            ("no_mutation_guarantees", "candidate_index_mutated"),
        ):
            with self.subTest(field=field):
                payload = self._payload()
                payload[section][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_global_absence_claim_fails(self) -> None:
        payload = json.loads(ABSENCE.read_text(encoding="utf-8"))
        payload["claim"]["global_absence_claimed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("global_absence_claimed" in error for error in report["errors"]))

    def test_secret_marker_fails(self) -> None:
        payload = self._payload()
        payload["limitations"].append("secret: not allowed")
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def _payload(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EVIDENCE_LEDGER_RECORD.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run([sys.executable, "scripts/validate_evidence_ledger_record.py", "--record", str(path), "--json"], cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
