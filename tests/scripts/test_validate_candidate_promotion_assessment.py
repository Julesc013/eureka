import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "candidate_promotion" / "minimal_promotion_review_required_v0" / "CANDIDATE_PROMOTION_ASSESSMENT.json"


class CandidatePromotionAssessmentValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_candidate_promotion_assessment.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_candidate_promotion_assessment.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 4)

    def test_private_path_assessment_fails(self) -> None:
        payload = self._example_payload()
        payload["candidate_summary"]["label"] = "C:\\Users\\Alice\\private.txt"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_assessment_fails(self) -> None:
        payload = self._example_payload()
        payload["candidate_summary"]["label"] = "api_key should not be here"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_no_auto_promotion_flags_fail(self) -> None:
        for field in ("promotion_performed", "accepted_as_truth", "promoted_to_master_index"):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload["no_auto_promotion_guarantees"][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_decision_automatic_fails(self) -> None:
        payload = self._example_payload()
        payload["recommended_decision"]["automatic"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("automatic" in error for error in report["errors"]))

    def test_review_promotion_allowed_now_fails(self) -> None:
        payload = self._example_payload()
        payload["review_requirements"]["promotion_allowed_now"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("promotion_allowed_now" in error for error in report["errors"]))

    def test_confidence_not_truth_and_promotion_sufficiency_required(self) -> None:
        payload = self._example_payload()
        payload["confidence_assessment"]["confidence_not_truth"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("confidence_not_truth" in error for error in report["errors"]))

        payload = self._example_payload()
        payload["confidence_assessment"]["confidence_sufficient_for_promotion"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("confidence_sufficient_for_promotion" in error for error in report["errors"]))

    def test_live_source_and_probe_flags_fail(self) -> None:
        payload = self._example_payload()
        payload["source_policy_assessment"]["live_source_called"] = True
        payload["source_policy_assessment"]["live_probe_enabled"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("live_source_called" in error for error in report["errors"]))
        self.assertTrue(any("live_probe_enabled" in error for error in report["errors"]))

    def test_rights_risk_and_action_flags_fail(self) -> None:
        for field in ("downloads_enabled", "installs_enabled", "execution_enabled", "rights_clearance_claimed", "malware_safety_claimed"):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload["rights_and_risk_assessment"][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_mutation_flags_fail(self) -> None:
        for field in ("master_index_mutated", "source_cache_mutated", "evidence_ledger_mutated"):
            with self.subTest(field=field):
                payload = self._example_payload()
                payload["no_mutation_guarantees"][field] = True
                report = self._validate_temp(payload)
                self.assertEqual(report["status"], "invalid")
                self.assertTrue(any(field in error for error in report["errors"]))

    def test_future_outputs_are_not_implemented(self) -> None:
        payload = self._example_payload()
        payload["future_outputs"][0]["output_runtime_implemented"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("output_runtime_implemented" in error for error in report["errors"]))

    def _example_payload(self) -> dict:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CANDIDATE_PROMOTION_ASSESSMENT.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_candidate_promotion_assessment.py", "--assessment", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
