import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CombinedSourceCacheEvidenceLedgerContractTests(unittest.TestCase):
    def test_combined_validator_passes(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/validate_source_cache_evidence_ledger_contract.py"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("status: valid", completed.stdout)

    def test_combined_validator_json_parses(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/validate_source_cache_evidence_ledger_contract.py", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["report_id"], "source_cache_evidence_ledger_v0")


if __name__ == "__main__":
    unittest.main()
