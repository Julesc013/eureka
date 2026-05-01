import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunSearchMissLedgerEntryTests(unittest.TestCase):
    def test_dry_run_outputs_valid_shape(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_search_miss_ledger_entry.py",
                "--query",
                "no-such-local-index-hit",
                "--miss-type",
                "no_hits",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertEqual(payload["miss_entry_kind"], "search_miss_ledger_entry")
        self.assertEqual(payload["miss_classification"]["miss_type"], "no_hits")
        self.assertFalse(payload["query_ref"]["raw_query_retained"])
        self.assertFalse(payload["absence_summary"]["global_absence_claimed"])
        self.assertFalse(payload["no_mutation_guarantees"]["search_need_created"])
        self.assertFalse(payload["no_mutation_guarantees"]["probe_enqueued"])

    def test_dry_run_rejects_private_query(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_search_miss_ledger_entry.py",
                "--query",
                "api_key C:\\Users\\Alice\\private.txt",
                "--miss-type",
                "no_hits",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "rejected_by_privacy_filter")
        self.assertEqual(payload["miss_classification"]["miss_type"], "blocked_by_policy")
        self.assertTrue(payload["privacy"]["contains_secret"])
        self.assertTrue(payload["privacy"]["contains_private_path"])
        self.assertFalse(payload["privacy"]["public_aggregate_allowed"])


if __name__ == "__main__":
    unittest.main()
