import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class EvidenceWeightedRankingOperationsTests(unittest.TestCase):
    def test_governance_artifacts_exist_and_parse(self) -> None:
        for rel in (
            "contracts/search/evidence_weighted_ranking_assessment.v0.json",
            "contracts/search/ranking_explanation.v0.json",
            "contracts/search/ranking_factor.v0.json",
            "control/inventory/search/evidence_weighted_ranking_policy.json",
            "control/audits/evidence-weighted-ranking-contract-v0/evidence_weighted_ranking_report.json",
        ):
            path = ROOT / rel
            self.assertTrue(path.exists(), rel)
            json.loads(path.read_text(encoding="utf-8"))

    def test_contract_command_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_evidence_weighted_ranking_contract.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
