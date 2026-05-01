import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunSearchNeedRecordTests(unittest.TestCase):
    def test_dry_run_stdout_only_public_safe(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_search_need_record.py",
                "--label",
                "Windows 7 compatible application",
                "--object-kind",
                "software_version",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertEqual(payload["search_need_kind"], "search_need_record")
        self.assertFalse(payload["privacy"]["contains_raw_query"])
        self.assertFalse(payload["priority"]["demand_count_claimed"])
        self.assertFalse(payload["no_mutation_guarantees"]["probe_enqueued"])
        self.assertFalse(payload["no_mutation_guarantees"]["candidate_index_mutated"])
        self.assertFalse(payload["no_mutation_guarantees"]["master_index_mutated"])

    def test_dry_run_rejects_sensitive_label(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_search_need_record.py",
                "--label",
                "C:\\Users\\Alice\\private.txt api_key=abc",
                "--object-kind",
                "software_version",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "rejected_by_privacy_filter")
        self.assertEqual(payload["need_identity"]["canonical_need_label"], "<redacted>")
        self.assertTrue(payload["privacy"]["contains_private_path"])
        self.assertTrue(payload["privacy"]["contains_secret"])
        self.assertFalse(payload["privacy"]["public_aggregate_allowed"])


if __name__ == "__main__":
    unittest.main()
