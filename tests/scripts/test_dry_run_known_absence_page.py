import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class KnownAbsencePageDryRunTests(unittest.TestCase):
    def test_dry_run_json_stdout_only(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_known_absence_page.py",
                "--query",
                "no-such-local-index-hit",
                "--absence-status",
                "scoped_absence",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        page = json.loads(completed.stdout)
        self.assertEqual(page["status"], "dry_run_validated")
        self.assertEqual(page["absence_page_kind"], "known_absence_page")
        self.assertFalse(page["absence_summary"]["global_absence_claimed"])
        self.assertFalse(page["absence_summary"]["exhaustive_search_claimed"])
        self.assertFalse(page["query_context"]["raw_query_retained"])
        self.assertFalse(page["no_global_absence_guarantees"]["live_probes_performed"])
        self.assertFalse(page["no_global_absence_guarantees"]["external_calls_performed"])
        self.assertFalse(page["no_mutation_guarantees"]["master_index_mutated"])

    def test_dry_run_redacts_sensitive_query(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_known_absence_page.py",
                "--query",
                "api_key C:\\Users\\Alice\\private.txt",
                "--absence-status",
                "scoped_absence",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        page = json.loads(completed.stdout)
        self.assertEqual(page["status"], "rejected_by_privacy_filter")
        self.assertEqual(page["query_context"]["normalized_query"], "[redacted]")
        self.assertFalse(page["query_context"]["raw_query_retained"])
        self.assertFalse(page["privacy"]["publishable"])
        self.assertFalse(page["privacy"]["public_aggregate_allowed"])


if __name__ == "__main__":
    unittest.main()
