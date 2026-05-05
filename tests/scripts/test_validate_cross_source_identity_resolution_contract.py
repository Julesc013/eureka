import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CrossSourceIdentityResolutionContractValidatorTests(unittest.TestCase):
    def test_contract_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_cross_source_identity_resolution_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("assessment_example_count: 5", completed.stdout)
        self.assertIn("cluster_example_count: 5", completed.stdout)

    def test_contract_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_cross_source_identity_resolution_contract.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["report_id"], "cross_source_identity_resolution_contract_v0")
        self.assertEqual(report["assessment_example_count"], 5)
        self.assertEqual(report["cluster_example_count"], 5)


if __name__ == "__main__":
    unittest.main()
