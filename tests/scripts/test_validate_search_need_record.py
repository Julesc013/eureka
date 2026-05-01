import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "search_needs" / "minimal_unresolved_software_need_v0" / "SEARCH_NEED_RECORD.json"


class SearchNeedRecordValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_search_need_record.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_search_need_record.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 2)

    def test_private_path_record_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["need_identity"]["canonical_need_label"] = "C:\\Users\\Alice\\private.txt"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_record_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["need_identity"]["canonical_need_label"] = "api_key should not be here"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_ip_address_record_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["need_identity"]["canonical_need_label"] = "192.168.1.10 test"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("ip_address" in error for error in report["errors"]))

    def test_master_index_mutation_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_mutation_guarantees"]["master_index_mutated"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("master_index_mutated" in error for error in report["errors"]))

    def test_probe_enqueue_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_mutation_guarantees"]["probe_enqueued"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("probe_enqueued" in error for error in report["errors"]))

    def test_candidate_index_mutation_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_mutation_guarantees"]["candidate_index_mutated"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("candidate_index_mutated" in error for error in report["errors"]))

    def test_demand_count_claim_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["priority"]["demand_count_claimed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("demand_count_claimed" in error for error in report["errors"]))

    def test_suggested_step_must_be_future_only(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["suggested_next_steps"][0]["future_only"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("future_only" in error for error in report["errors"]))

    def test_non_reversible_fingerprint_required(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["need_identity"]["need_fingerprint"]["reversible"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("reversible" in error for error in report["errors"]))

    def test_absence_overclaim_phrase_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["not_checked_scope"]["limitations"] = ["Scoped check says every source was checked."]
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("absence outside checked scope" in error for error in report["errors"]))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SEARCH_NEED_RECORD.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_search_need_record.py", "--record", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
