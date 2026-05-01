import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class QueryGuardDryRunTests(unittest.TestCase):
    def test_safe_query_json_is_valid_stdout_only(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_query_guard.py", "--query", "windows 7 apps", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertFalse(payload["no_runtime_guarantees"]["runtime_guard_implemented"])
        self.assertFalse(payload["no_runtime_guarantees"]["telemetry_exported"])
        self.assertFalse(payload["no_runtime_guarantees"]["account_tracking_performed"])
        self.assertFalse(payload["no_runtime_guarantees"]["ip_tracking_performed"])
        self.assertTrue(payload["aggregate_eligibility"]["public_aggregate_allowed"])
        self._validate_payload(payload)

    def test_private_path_is_redacted_and_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_query_guard.py", "--query", "find C:\\Users\\Alice\\private.txt", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "rejected_sensitive")
        self.assertIn("<redacted-private-path>", payload["input_context"]["normalized_query"])
        self.assertFalse(payload["aggregate_eligibility"]["public_aggregate_allowed"])
        self._validate_payload(payload)

    def test_secret_is_redacted_and_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_query_guard.py", "--query", "api_key should not be here", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "rejected_sensitive")
        self.assertIn("<redacted-secret>", payload["input_context"]["normalized_query"])
        self.assertFalse(payload["aggregate_eligibility"]["public_aggregate_allowed"])
        self._validate_payload(payload)

    def test_live_probe_forcing_is_quarantined(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_query_guard.py", "--query", "force live probe wayback now", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "quarantined_poisoning_risk")
        self.assertFalse(payload["aggregate_eligibility"]["public_aggregate_allowed"])
        self.assertFalse(payload["no_mutation_guarantees"]["probe_queue_mutated"])
        self._validate_payload(payload)

    def _validate_payload(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "QUERY_GUARD_DECISION.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_query_guard_decision.py", "--decision", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")


if __name__ == "__main__":
    unittest.main()
