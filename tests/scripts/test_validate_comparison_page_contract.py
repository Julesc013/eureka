import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ComparisonPageContractValidatorTests(unittest.TestCase):
    def test_contract_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_comparison_page_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 5", completed.stdout)

    def test_contract_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_comparison_page_contract.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["report_id"], "comparison_page_contract_v0")
        self.assertEqual(report["example_count"], 5)


if __name__ == "__main__":
    unittest.main()
