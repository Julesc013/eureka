import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "query_result_cache" / "minimal_cache_entry_v0" / "SEARCH_RESULT_CACHE_ENTRY.json"


class SearchResultCacheEntryValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_search_result_cache_entry.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_search_result_cache_entry.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 2)

    def test_private_path_entry_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["query_ref"]["normalized_query"]["text"] = "C:\\Users\\Alice\\private.txt"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_entry_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["query_ref"]["normalized_query"]["text"] = "api_key should not be here"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_ip_address_entry_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["query_ref"]["normalized_query"]["text"] = "192.168.1.10 test"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("ip_address" in error for error in report["errors"]))

    def test_master_index_mutation_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_mutation_guarantees"]["master_index_mutated"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("master_index_mutated" in error for error in report["errors"]))

    def test_global_absence_claim_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["absence_summary"]["absence_status"] = "scoped_absence"
        payload["absence_summary"]["limitations"] = ["Scoped review covered every source."]
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("global absence" in error for error in report["errors"]))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SEARCH_RESULT_CACHE_ENTRY.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_search_result_cache_entry.py", "--entry", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
