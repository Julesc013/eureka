import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SourceSyncWorkerDryRunTests(unittest.TestCase):
    def test_dry_run_json_is_valid_stdout_only(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_source_sync_worker_job.py",
                "--label",
                "IA metadata sync example",
                "--kind",
                "internet_archive_metadata_sync",
                "--source-family",
                "internet_archive",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertTrue(payload["job_kind"]["live_network_required_future"])
        self.assertTrue(payload["job_kind"]["approval_required"])
        self.assertFalse(payload["source_policy"]["live_source_enabled_now"])
        self.assertFalse(payload["no_execution_guarantees"]["job_executed"])
        self.assertFalse(payload["no_execution_guarantees"]["live_source_called"])
        self.assertFalse(payload["no_execution_guarantees"]["external_calls_performed"])
        self.assertFalse(payload["no_mutation_guarantees"]["source_cache_mutated"])
        self._validate_payload(payload)

    def test_private_label_is_redacted_and_blocked(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_source_sync_worker_job.py",
                "--label",
                "sync C:\\Users\\Alice\\private.txt",
                "--kind",
                "internet_archive_metadata_sync",
                "--source-family",
                "internet_archive",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "blocked_by_policy")
        self.assertEqual(payload["job_identity"]["canonical_job_label"], "<redacted-source-sync-label>")
        self.assertFalse(payload["privacy"]["public_aggregate_allowed"])
        self._validate_payload(payload)

    def _validate_payload(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SOURCE_SYNC_WORKER_JOB.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_source_sync_worker_job.py", "--job", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")


if __name__ == "__main__":
    unittest.main()
