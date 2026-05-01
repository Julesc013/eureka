import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SearchNeedRecordContractValidatorTests(unittest.TestCase):
    def test_contract_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_search_need_record_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_contract_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_search_need_record_contract.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["contract_file"], "contracts/query/search_need_record.v0.json")
        self.assertEqual(report["example_count"], 2)


if __name__ == "__main__":
    unittest.main()
