import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunEvidenceWeightedRankingTests(unittest.TestCase):
    def test_dry_run_json_is_valid_assessment(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_evidence_weighted_ranking.py",
                "--left-title",
                "Strong evidence result",
                "--right-title",
                "Weak evidence result",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertFalse(payload["runtime_ranking_implemented"])
        self.assertFalse(payload["ranking_applied_to_live_search"])
        self.assertFalse(payload["public_search_order_changed"])
        self.assertFalse(payload["live_source_called"])
        self.assertFalse(payload["external_calls_performed"])


if __name__ == "__main__":
    unittest.main()
