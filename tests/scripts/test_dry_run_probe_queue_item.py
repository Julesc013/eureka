import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunProbeQueueItemTests(unittest.TestCase):
    def test_dry_run_stdout_only_public_safe(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_probe_queue_item.py",
                "--label",
                "Check IA metadata for Windows 7 app query",
                "--kind",
                "source_metadata_probe",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertEqual(payload["probe_item_kind"], "probe_queue_item")
        self.assertTrue(payload["probe_kind"]["live_network_required_future"])
        self.assertTrue(payload["probe_kind"]["approval_required"])
        self.assertFalse(payload["source_policy"]["live_probe_enabled"])
        self.assertFalse(payload["privacy"]["contains_raw_query"])
        self.assertFalse(payload["priority"]["demand_count_claimed"])
        self.assertFalse(payload["no_execution_guarantees"]["probe_executed"])
        self.assertFalse(payload["no_execution_guarantees"]["live_source_called"])
        self.assertFalse(payload["no_mutation_guarantees"]["source_cache_mutated"])
        self.assertFalse(payload["no_mutation_guarantees"]["candidate_index_mutated"])
        self.assertFalse(payload["no_mutation_guarantees"]["master_index_mutated"])

    def test_dry_run_rejects_sensitive_label(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_probe_queue_item.py",
                "--label",
                "C:\\Users\\Alice\\private.txt api_key=abc",
                "--kind",
                "source_metadata_probe",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "rejected_by_privacy_filter")
        self.assertEqual(payload["probe_identity"]["canonical_probe_label"], "<redacted>")
        self.assertTrue(payload["privacy"]["contains_private_path"])
        self.assertTrue(payload["privacy"]["contains_secret"])
        self.assertFalse(payload["privacy"]["public_aggregate_allowed"])


if __name__ == "__main__":
    unittest.main()
