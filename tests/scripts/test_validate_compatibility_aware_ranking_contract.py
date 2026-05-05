import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CompatibilityAwareRankingContractValidatorTests(unittest.TestCase):
    def test_contract_validator_passes(self):
        completed = subprocess.run([sys.executable, "scripts/validate_compatibility_aware_ranking_contract.py"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("status: valid", completed.stdout)

    def test_contract_validator_json_parses(self):
        completed = subprocess.run([sys.executable, "scripts/validate_compatibility_aware_ranking_contract.py", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["profile_example_count"], 6)
        self.assertEqual(report["assessment_example_count"], 6)
        self.assertEqual(report["explanation_example_count"], 6)

    def test_docs_and_policy_are_cautious(self):
        doc = (ROOT / "docs" / "reference" / "COMPATIBILITY_AWARE_RANKING_CONTRACT.md").read_text(encoding="utf-8").lower()
        for phrase in ("contract-only", "not installability proof", "not dependency safety proof", "no runtime ranking", "no public search order change", "no hidden suppression", "no mutation"):
            self.assertIn(phrase, doc)
        policy = json.loads((ROOT / "control" / "inventory" / "search" / "compatibility_aware_ranking_policy.json").read_text(encoding="utf-8"))
        self.assertFalse(policy["runtime_compatibility_ranking_implemented"])
        self.assertFalse(policy["public_search_order_changed"])
        self.assertFalse(policy["package_manager_invocation_allowed"])
        self.assertFalse(policy["emulator_vm_launch_allowed"])
        self.assertTrue(policy["compatibility_evidence_required"])


if __name__ == "__main__":
    unittest.main()
