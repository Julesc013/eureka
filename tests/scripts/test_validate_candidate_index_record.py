import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "candidate_index" / "minimal_object_candidate_v0" / "CANDIDATE_INDEX_RECORD.json"


class CandidateIndexRecordValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_candidate_index_record.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_candidate_index_record.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 4)

    def test_private_path_record_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["candidate_identity"]["canonical_candidate_label"] = "C:\\Users\\Alice\\private.txt"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_record_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["candidate_identity"]["canonical_candidate_label"] = "api_key should not be here"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_accepted_as_truth_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_truth_guarantees"]["accepted_as_truth"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("accepted_as_truth" in error for error in report["errors"]))

    def test_promoted_to_master_index_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_truth_guarantees"]["promoted_to_master_index"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("promoted_to_master_index" in error for error in report["errors"]))

    def test_promotion_allowed_now_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["review"]["promotion_allowed_now"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("promotion_allowed_now" in error for error in report["errors"]))

    def test_promotion_policy_required_fails_when_false(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["review"]["promotion_policy_required"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("promotion_policy_required" in error for error in report["errors"]))

    def test_confidence_not_truth_required(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["confidence"]["confidence_not_truth"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("confidence_not_truth" in error for error in report["errors"]))

    def test_live_source_and_probe_flags_fail(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["source_policy"]["live_source_called"] = True
        payload["source_policy"]["live_probe_enabled"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("live_source_called" in error for error in report["errors"]))
        self.assertTrue(any("live_probe_enabled" in error for error in report["errors"]))

    def test_rights_and_payload_action_flags_fail(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["rights_and_risk"]["downloads_enabled"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("downloads_enabled" in error for error in report["errors"]))

    def test_mutation_flags_fail(self) -> None:
        for field in ("master_index_mutated", "source_cache_mutated", "evidence_ledger_mutated"):
            with self.subTest(field=field):
                payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
                payload["no_mutation_guarantees"][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_non_reversible_fingerprint_required(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["candidate_identity"]["candidate_fingerprint"]["reversible"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("reversible" in error for error in report["errors"]))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CANDIDATE_INDEX_RECORD.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_candidate_index_record.py", "--record", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
