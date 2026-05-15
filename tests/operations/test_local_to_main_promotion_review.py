from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LocalToMainPromotionReviewTests(unittest.TestCase):
    def test_promotion_review_is_plan_only(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/prepare_local_to_main_promotion_review.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["branch_mutation_performed"])
        self.assertFalse(payload["merge_performed"])
        self.assertFalse(payload["push_performed"])
        self.assertFalse(payload["promotion_recommended"])

    def test_promotion_review_rejects_public_claims(self) -> None:
        payload = json.loads((ROOT / "control/inventory/local_appliance_promotion_review.json").read_text())
        self.assertTrue(payload["promotion_review_required"])
        self.assertTrue(payload["no_deployment"])
        self.assertTrue(payload["no_production_readiness_claim"])
        self.assertTrue(payload["no_public_launch_readiness_claim"])


if __name__ == "__main__":
    unittest.main()
