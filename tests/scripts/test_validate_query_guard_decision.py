import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "query_guard" / "minimal_public_safe_query_v0" / "QUERY_GUARD_DECISION.json"
PRIVATE_PATH_EXAMPLE = ROOT / "examples" / "query_guard" / "minimal_private_path_rejected_v0" / "QUERY_GUARD_DECISION.json"
SECRET_EXAMPLE = ROOT / "examples" / "query_guard" / "minimal_secret_rejected_v0" / "QUERY_GUARD_DECISION.json"
SOURCE_STUFFING_EXAMPLE = ROOT / "examples" / "query_guard" / "minimal_source_stuffing_quarantined_v0" / "QUERY_GUARD_DECISION.json"
FAKE_DEMAND_EXAMPLE = ROOT / "examples" / "query_guard" / "minimal_fake_demand_throttled_v0" / "QUERY_GUARD_DECISION.json"


class QueryGuardDecisionValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_query_guard_decision.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_query_guard_decision.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 5)

    def test_examples_encode_expected_privacy_and_poisoning_actions(self) -> None:
        private_path = json.loads(PRIVATE_PATH_EXAMPLE.read_text(encoding="utf-8"))
        self.assertIn("<redacted-private-path>", private_path["input_context"]["normalized_query"])
        self.assertFalse(private_path["aggregate_eligibility"]["public_aggregate_allowed"])
        self.assertIn("reject_sensitive", self._actions(private_path))

        secret = json.loads(SECRET_EXAMPLE.read_text(encoding="utf-8"))
        self.assertIn("<redacted-secret>", secret["input_context"]["normalized_query"])
        self.assertFalse(secret["aggregate_eligibility"]["public_aggregate_allowed"])
        self.assertIn("reject_sensitive", self._actions(secret))

        source_stuffing = json.loads(SOURCE_STUFFING_EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(source_stuffing["status"], "quarantined_poisoning_risk")
        self.assertFalse(source_stuffing["aggregate_eligibility"]["public_aggregate_allowed"])
        self.assertIn("quarantine_for_review", self._actions(source_stuffing))

        fake_demand = json.loads(FAKE_DEMAND_EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(fake_demand["status"], "throttled_future")
        self.assertFalse(fake_demand["aggregate_eligibility"]["public_aggregate_allowed"])
        self.assertIn("throttle_future", self._actions(fake_demand))

    def test_hard_no_runtime_and_no_mutation_flags_fail(self) -> None:
        for section, field in (
            ("no_runtime_guarantees", "runtime_guard_implemented"),
            ("no_runtime_guarantees", "telemetry_exported"),
            ("no_runtime_guarantees", "account_tracking_performed"),
            ("no_runtime_guarantees", "ip_tracking_performed"),
            ("no_runtime_guarantees", "public_query_logging_enabled"),
            ("no_mutation_guarantees", "master_index_mutated"),
            ("no_mutation_guarantees", "query_observation_mutated"),
            ("no_mutation_guarantees", "candidate_index_mutated"),
        ):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload[section][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_private_path_decision_fails(self) -> None:
        payload = self._example_payload()
        payload["input_context"]["normalized_query"] = "C:\\Users\\Alice\\private.txt"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_decision_fails(self) -> None:
        payload = self._example_payload()
        payload["input_context"]["normalized_query"] = "api_key should not be here"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_high_privacy_risk_cannot_be_public_aggregate(self) -> None:
        payload = self._example_payload()
        payload["privacy_risks"] = [
            {
                "risk_type": "raw_query_retention_risk",
                "severity": "high",
                "detected": True,
                "redaction_required": True,
                "rejection_required": False,
                "reason": "Synthetic high privacy risk.",
                "field_refs": ["input_context.normalized_query"],
                "limitations": [],
            }
        ]
        payload["aggregate_eligibility"]["public_aggregate_allowed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("privacy risk" in error for error in report["errors"]))

    def test_high_poisoning_risk_cannot_be_public_aggregate(self) -> None:
        payload = self._example_payload()
        payload["poisoning_risks"] = [
            {
                "risk_type": "source_stuffing",
                "severity": "high",
                "detected": True,
                "quarantine_required": True,
                "throttling_required_future": False,
                "aggregate_exclusion_required": True,
                "reason": "Synthetic source stuffing.",
                "limitations": [],
            }
        ]
        payload["aggregate_eligibility"]["public_aggregate_allowed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("poisoning risk" in error for error in report["errors"]))

    def test_automatic_acceptance_false(self) -> None:
        payload = self._example_payload()
        payload["review_requirements"]["automatic_acceptance_allowed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("automatic_acceptance_allowed" in error for error in report["errors"]))

    def _example_payload(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def _actions(self, payload: dict) -> set[str]:
        return {item["action_type"] for item in payload["policy_actions"]}

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "QUERY_GUARD_DECISION.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_query_guard_decision.py", "--decision", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
