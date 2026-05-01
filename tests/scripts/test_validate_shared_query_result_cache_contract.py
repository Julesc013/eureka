import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SharedQueryResultCacheContractValidatorTests(unittest.TestCase):
    def test_contract_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_shared_query_result_cache_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("shared_query_result_cache_v0", completed.stdout)

    def test_contract_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_shared_query_result_cache_contract.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["contract_file"], "contracts/query/search_result_cache_entry.v0.json")
        self.assertEqual(report["example_count"], 2)


if __name__ == "__main__":
    unittest.main()
