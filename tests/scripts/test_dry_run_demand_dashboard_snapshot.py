import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DemandDashboardDryRunTests(unittest.TestCase):
    def test_dry_run_json_is_valid_stdout_only(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_demand_dashboard_snapshot.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertFalse(payload["no_runtime_guarantees"]["runtime_dashboard_implemented"])
        self.assertFalse(payload["no_runtime_guarantees"]["telemetry_exported"])
        self.assertFalse(payload["no_runtime_guarantees"]["account_tracking_performed"])
        self.assertFalse(payload["no_runtime_guarantees"]["ip_tracking_performed"])
        self.assertFalse(payload["no_runtime_guarantees"]["real_user_demand_claimed"])
        self.assertTrue(payload["privacy_guard_summary"]["privacy_filter_required"])
        self.assertTrue(payload["poisoning_guard_summary"]["fake_demand_excluded"])
        self._validate_payload(payload)

    def _validate_payload(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DEMAND_DASHBOARD_SNAPSHOT.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_demand_dashboard_snapshot.py", "--snapshot", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")


if __name__ == "__main__":
    unittest.main()
