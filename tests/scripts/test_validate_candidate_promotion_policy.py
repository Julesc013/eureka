import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CandidatePromotionPolicyValidatorTests(unittest.TestCase):
    def test_policy_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_candidate_promotion_policy.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_policy_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_candidate_promotion_policy.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 4)
        self.assertEqual(report["report_id"], "candidate_promotion_policy_v0")


if __name__ == "__main__":
    unittest.main()
