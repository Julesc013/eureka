import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "source_cache" / "minimal_ia_metadata_cache_record_v0" / "SOURCE_CACHE_RECORD.json"


class SourceCacheRecordValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/validate_source_cache_record.py", "--all-examples"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/validate_source_cache_record.py", "--all-examples", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 3)

    def test_examples_encode_hard_boundaries(self) -> None:
        for path in sorted((ROOT / "examples" / "source_cache").glob("*/SOURCE_CACHE_RECORD.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(payload["cache_kind"]["raw_payload_allowed"])
            self.assertFalse(payload["source_policy"]["live_source_enabled_now"])
            for field in ("source_cache_runtime_implemented", "cache_write_performed", "live_source_called", "external_calls_performed", "arbitrary_url_fetched", "raw_payload_stored", "private_data_stored", "executable_payload_stored", "telemetry_exported", "credentials_used"):
                self.assertFalse(payload["no_runtime_guarantees"][field], field)
            for field in ("evidence_ledger_mutated", "candidate_index_mutated", "public_index_mutated", "local_index_mutated", "master_index_mutated"):
                self.assertFalse(payload["no_mutation_guarantees"][field], field)
            self.assertFalse(payload["rights_and_risk"]["rights_clearance_claimed"])
            self.assertFalse(payload["rights_and_risk"]["malware_safety_claimed"])

    def test_negative_flags_fail(self) -> None:
        for section, field in (
            ("no_runtime_guarantees", "source_cache_runtime_implemented"),
            ("no_runtime_guarantees", "cache_write_performed"),
            ("no_runtime_guarantees", "live_source_called"),
            ("no_runtime_guarantees", "external_calls_performed"),
            ("no_runtime_guarantees", "arbitrary_url_fetched"),
            ("no_runtime_guarantees", "raw_payload_stored"),
            ("no_runtime_guarantees", "private_data_stored"),
            ("no_runtime_guarantees", "executable_payload_stored"),
            ("no_mutation_guarantees", "master_index_mutated"),
            ("no_mutation_guarantees", "evidence_ledger_mutated"),
        ):
            with self.subTest(field=field):
                payload = self._payload()
                payload[section][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_secret_marker_fails(self) -> None:
        payload = self._payload()
        payload["limitations"].append("api_key should not appear")
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_private_path_fails(self) -> None:
        payload = self._payload()
        payload["limitations"].append("C:\\Users\\Alice\\private.txt")
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def _payload(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SOURCE_CACHE_RECORD.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run([sys.executable, "scripts/validate_source_cache_record.py", "--record", str(path), "--json"], cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
