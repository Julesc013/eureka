import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "demand_dashboard" / "minimal_dashboard_snapshot_v0" / "DEMAND_DASHBOARD_SNAPSHOT.json"
SOURCE_GAP_EXAMPLE = ROOT / "examples" / "demand_dashboard" / "minimal_source_gap_dashboard_v0" / "DEMAND_DASHBOARD_SNAPSHOT.json"


class DemandDashboardSnapshotValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_demand_dashboard_snapshot.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_demand_dashboard_snapshot.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 2)

    def test_examples_encode_synthetic_privacy_and_poisoning_boundaries(self) -> None:
        for path in (EXAMPLE, SOURCE_GAP_EXAMPLE):
            with self.subTest(path=path):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(payload["input_summary"]["real_user_data_included"])
                self.assertFalse(payload["input_summary"]["raw_queries_included"])
                self.assertFalse(payload["input_summary"]["protected_data_included"])
                self.assertTrue(payload["privacy_guard_summary"]["privacy_filter_required"])
                self.assertTrue(payload["poisoning_guard_summary"]["poisoning_filter_required"])
                self.assertTrue(payload["poisoning_guard_summary"]["fake_demand_excluded"])
                self.assertFalse(payload["priority_summary"]["real_user_demand_claimed"])
                self.assertFalse(payload["public_visibility"]["raw_queries_visible"])
                self.assertFalse(payload["public_visibility"]["private_data_visible"])
                self.assertFalse(payload["public_visibility"]["demand_counts_claimed_as_real"])

    def test_hard_no_runtime_and_no_mutation_flags_fail(self) -> None:
        for section, field in (
            ("no_runtime_guarantees", "runtime_dashboard_implemented"),
            ("no_runtime_guarantees", "telemetry_exported"),
            ("no_runtime_guarantees", "account_tracking_performed"),
            ("no_runtime_guarantees", "ip_tracking_performed"),
            ("no_runtime_guarantees", "raw_query_retained"),
            ("no_runtime_guarantees", "real_user_demand_claimed"),
            ("no_mutation_guarantees", "master_index_mutated"),
            ("no_mutation_guarantees", "public_index_mutated"),
            ("no_mutation_guarantees", "query_observation_mutated"),
            ("no_mutation_guarantees", "candidate_index_mutated"),
        ):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload[section][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_real_demand_claim_fails(self) -> None:
        payload = self._example_payload()
        payload["priority_summary"]["real_user_demand_claimed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("real_user_demand_claimed" in error for error in report["errors"]))

    def test_raw_query_retained_fails(self) -> None:
        payload = self._example_payload()
        payload["no_runtime_guarantees"]["raw_query_retained"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("raw_query_retained" in error for error in report["errors"]))

    def test_high_privacy_risk_aggregate_allowed_fails(self) -> None:
        payload = self._example_payload()
        payload["privacy_guard_summary"]["high_privacy_risk_excluded"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("high_privacy_risk_excluded" in error for error in report["errors"]))

    def test_high_poisoning_risk_aggregate_allowed_fails(self) -> None:
        payload = self._example_payload()
        payload["poisoning_guard_summary"]["high_poisoning_risk_excluded"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("high_poisoning_risk_excluded" in error for error in report["errors"]))

    def test_private_path_snapshot_fails(self) -> None:
        payload = self._example_payload()
        payload["limitations"].append("C:\\Users\\Alice\\private.txt")
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_snapshot_fails(self) -> None:
        payload = self._example_payload()
        payload["limitations"].append("api_key should not be here")
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def _example_payload(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DEMAND_DASHBOARD_SNAPSHOT.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_demand_dashboard_snapshot.py", "--snapshot", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
