import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class EvidenceWeightedRankingContractValidatorTests(unittest.TestCase):
    def test_contract_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_evidence_weighted_ranking_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_contract_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_evidence_weighted_ranking_contract.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["assessment_example_count"], 5)
        self.assertEqual(report["explanation_example_count"], 5)

    def test_docs_state_contract_boundaries(self) -> None:
        text = (ROOT / "docs" / "reference" / "EVIDENCE_WEIGHTED_RANKING_CONTRACT.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "contract-only",
            "ranking is not runtime yet",
            "ranking is not truth",
            "no hidden suppression",
            "public search ordering",
            "popularity/telemetry/ad/user-profile ranking",
            "no mutation",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
