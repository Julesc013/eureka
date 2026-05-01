import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunSearchResultCacheEntryTests(unittest.TestCase):
    def _run(self, query: str) -> dict:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_search_result_cache_entry.py", "--query", query, "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)

    def test_public_safe_dry_run(self) -> None:
        entry = self._run("windows 7 apps")
        self.assertEqual(entry["status"], "dry_run_validated")
        self.assertFalse(entry["query_ref"]["raw_query_retained"])
        self.assertFalse(entry["no_mutation_guarantees"]["master_index_mutated"])
        self.assertEqual(entry["request_summary"]["mode"], "local_index_only")

    def test_dry_run_output_validates(self) -> None:
        entry = self._run("windows 7 apps")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SEARCH_RESULT_CACHE_ENTRY.json"
            path.write_text(json.dumps(entry, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_search_result_cache_entry.py", "--entry", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")

    def test_no_such_query_is_scoped_absence(self) -> None:
        entry = self._run("no-such-local-index-hit")
        self.assertEqual(entry["status"], "dry_run_validated")
        self.assertEqual(entry["absence_summary"]["absence_status"], "scoped_absence")
        self.assertEqual(entry["response_summary"]["hit_state"], "no_hits")

    def test_private_path_rejected_by_privacy_filter(self) -> None:
        entry = self._run("C:\\Users\\Alice\\private.txt")
        self.assertEqual(entry["status"], "rejected_by_privacy_filter")
        self.assertTrue(entry["privacy"]["contains_private_path"])
        self.assertFalse(entry["privacy"]["public_aggregate_allowed"])
        self.assertEqual(entry["query_ref"]["normalized_query"]["text"], "<redacted>")


if __name__ == "__main__":
    unittest.main()
