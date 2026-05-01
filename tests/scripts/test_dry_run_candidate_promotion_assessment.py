import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunCandidatePromotionAssessmentTests(unittest.TestCase):
    def test_dry_run_json_is_validated_shape(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_candidate_promotion_assessment.py",
                "--candidate-label",
                "Firefox ESR Windows XP compatibility candidate",
                "--candidate-type",
                "compatibility_claim_candidate",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertFalse(payload["no_auto_promotion_guarantees"]["promotion_performed"])
        self.assertFalse(payload["no_auto_promotion_guarantees"]["accepted_as_truth"])
        self.assertFalse(payload["no_auto_promotion_guarantees"]["promoted_to_master_index"])
        self.assertFalse(payload["recommended_decision"]["automatic"])
        self.assertTrue(payload["confidence_assessment"]["confidence_not_truth"])

    def test_unsafe_label_is_redacted_and_blocked(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_candidate_promotion_assessment.py",
                "--candidate-label",
                "api_key C:\\Users\\Alice\\secret.txt",
                "--candidate-type",
                "compatibility_claim_candidate",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "promotion_blocked")
        self.assertEqual(payload["candidate_summary"]["label"], "[redacted candidate label]")
        self.assertEqual(payload["privacy_assessment"]["privacy_status"], "rejected_sensitive")
        self.assertFalse(payload["privacy_assessment"]["public_aggregate_allowed"])


if __name__ == "__main__":
    unittest.main()
