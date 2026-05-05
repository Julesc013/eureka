from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)


class ValidateSearchResultExplanationContractTests(unittest.TestCase):
    def test_contract_validator_passes_and_json_parses(self):
        result = run_cmd("scripts/validate_search_result_explanation_contract.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        result_json = run_cmd("scripts/validate_search_result_explanation_contract.py", "--json")
        self.assertEqual(result_json.returncode, 0, result_json.stderr)
        payload = json.loads(result_json.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["error_count"], 0)

    def test_contracts_inventory_report_parse(self):
        for rel in [
            "contracts/search/search_result_explanation.v0.json",
            "contracts/search/search_result_explanation_component.v0.json",
            "contracts/search/search_result_explanation_policy.v0.json",
            "control/inventory/search/search_result_explanation_policy.json",
            "control/audits/search-result-explanation-contract-v0/search_result_explanation_contract_report.json",
        ]:
            self.assertIsInstance(json.loads((ROOT / rel).read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
