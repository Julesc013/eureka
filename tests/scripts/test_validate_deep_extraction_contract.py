from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)


class DeepExtractionTestMixin:
    maxDiff = None

    def load(self, rel: str):
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class ValidateDeepExtractionContractTests(DeepExtractionTestMixin, unittest.TestCase):
    def test_contract_validator_passes_and_json_parses(self):
        result = run_cmd("scripts/validate_deep_extraction_contract.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        result_json = run_cmd("scripts/validate_deep_extraction_contract.py", "--json")
        self.assertEqual(result_json.returncode, 0, result_json.stderr)
        payload = json.loads(result_json.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["error_count"], 0)

    def test_contracts_and_inventory_parse(self):
        for rel in [
            "contracts/extraction/deep_extraction_request.v0.json",
            "contracts/extraction/extraction_result_summary.v0.json",
            "contracts/extraction/extraction_policy.v0.json",
            "contracts/extraction/extraction_member.v0.json",
            "control/inventory/extraction/deep_extraction_policy.json",
            "control/audits/deep-extraction-contract-v0/deep_extraction_contract_report.json",
        ]:
            self.assertIsInstance(self.load(rel), dict)


if __name__ == "__main__":
    unittest.main()
