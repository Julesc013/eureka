import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DevAndIAToMainPromotionTests(unittest.TestCase):
    def test_decision_blocks_combined_baseline_until_full_discovery_is_green(self):
        decision = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_decision.json").read_text(encoding="utf-8")
        )
        self.assertEqual("blocked", decision["decision"])
        self.assertEqual("ia_metadata_pilot_plus_repo_layout_canon", decision["promotion_scope"])
        self.assertTrue(decision["main_can_fast_forward_to_dev"])
        self.assertFalse(decision["safe_to_push_main"])
        self.assertGreater(decision["hard_blockers_remaining"], 0)
        self.assertFalse(decision["force_push_required"])

    def test_boundary_matrix_preserves_non_claims(self):
        boundary = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_boundary_matrix.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(boundary["ia_metadata_pilot_closeout_passed"])
        self.assertTrue(boundary["repo_layout_canon_present"])
        self.assertFalse(boundary["full_archive_org_integration_claimed"])
        self.assertFalse(boundary["production_readiness_claimed"])
        self.assertFalse(boundary["marketplace_or_app_store_claimed"])
        self.assertFalse(boundary["repo_layout_moves_performed"])

    def test_validator_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_dev_and_ia_to_main_promotion.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_next_task_is_promotion_blocker_before_workbench_foundation(self):
        next_task = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_next_task_decision.json").read_text(encoding="utf-8")
        )
        self.assertIn("PROMOTION-BLOCKER", next_task["decision"])


if __name__ == "__main__":
    unittest.main()
