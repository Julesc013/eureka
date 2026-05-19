import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from scripts.validate_dev_and_ia_to_main_promotion import (  # noqa: E402
    validate_boundary_matrix,
    validate_branch_matrix,
    validate_decision,
    validate_input_state,
    validate_next_task,
    validate_validation_matrix,
)


class DevAndIAToMainPromotionGateTests(unittest.TestCase):
    def test_blocks_if_ia_closeout_missing(self):
        state = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_input_state.json").read_text(encoding="utf-8")
        )
        mutated = copy.deepcopy(state)
        mutated["ia_pilot_closeout_found"] = False
        self.assertIn("input_expected_true:ia_pilot_closeout_found", validate_input_state(mutated))

    def test_blocks_if_layout_canon_missing(self):
        state = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_input_state.json").read_text(encoding="utf-8")
        )
        mutated = copy.deepcopy(state)
        mutated["repo_layout_canon_found"] = False
        self.assertIn("input_expected_true:repo_layout_canon_found", validate_input_state(mutated))

    def test_blocks_if_promotion_blocker_repair_missing(self):
        state = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_input_state.json").read_text(encoding="utf-8")
        )
        mutated = copy.deepcopy(state)
        mutated["promotion_blocker_repair_found"] = False
        self.assertIn("input_expected_true:promotion_blocker_repair_found", validate_input_state(mutated))

    def test_blocks_if_main_cannot_fast_forward(self):
        matrix = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_branch_matrix.json").read_text(encoding="utf-8")
        )
        mutated = copy.deepcopy(matrix)
        mutated["main_can_fast_forward_to_dev"] = False
        self.assertIn("branch_expected_true:main_can_fast_forward_to_dev", validate_branch_matrix(mutated))

    def test_blocks_if_raw_response_committed(self):
        matrix = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_boundary_matrix.json").read_text(
                encoding="utf-8"
            )
        )
        mutated = copy.deepcopy(matrix)
        mutated["raw_response_committed"] = True
        self.assertIn("boundary_expected_false:raw_response_committed", validate_boundary_matrix(mutated))

    def test_blocks_if_production_or_public_launch_claimed(self):
        matrix = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_boundary_matrix.json").read_text(
                encoding="utf-8"
            )
        )
        mutated = copy.deepcopy(matrix)
        mutated["production_readiness_claimed"] = True
        mutated["public_launch_readiness_claimed"] = True
        errors = validate_boundary_matrix(mutated)
        self.assertIn("boundary_expected_false:production_readiness_claimed", errors)
        self.assertIn("boundary_expected_false:public_launch_readiness_claimed", errors)

    def test_blocks_if_full_archive_or_marketplace_claimed(self):
        matrix = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_boundary_matrix.json").read_text(
                encoding="utf-8"
            )
        )
        mutated = copy.deepcopy(matrix)
        mutated["full_archive_org_integration_claimed"] = True
        mutated["marketplace_or_app_store_readiness_claimed"] = True
        errors = validate_boundary_matrix(mutated)
        self.assertIn("boundary_expected_false:full_archive_org_integration_claimed", errors)
        self.assertIn("boundary_expected_false:marketplace_or_app_store_readiness_claimed", errors)

    def test_blocks_if_repo_layout_moves_occurred(self):
        matrix = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_boundary_matrix.json").read_text(
                encoding="utf-8"
            )
        )
        mutated = copy.deepcopy(matrix)
        mutated["repo_layout_moves_performed"] = True
        self.assertIn("boundary_expected_false:repo_layout_moves_performed", validate_boundary_matrix(mutated))

    def test_accepts_promotion_decision_and_repo_layout_next(self):
        decision = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_decision.json").read_text(encoding="utf-8")
        )
        next_task = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_next_task_decision.json").read_text(encoding="utf-8")
        )
        self.assertEqual([], validate_decision(decision))
        self.assertEqual([], validate_next_task(next_task))

    def test_promotion_passes_with_ia_closeout_layout_canon_and_green_discovery(self):
        decision = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_decision.json").read_text(encoding="utf-8")
        )
        matrix = json.loads(
            (ROOT / "control/inventory/dev_and_ia_to_main_promotion_validation_matrix.json").read_text(
                encoding="utf-8"
            )
        )
        promoted_decision = copy.deepcopy(decision)
        promoted_decision["decision"] = "promote_dev_to_main"
        promoted_decision["safe_to_push_main"] = True
        promoted_decision["hard_blockers_remaining"] = 0
        promoted_decision[
            "recommended_next_task"
        ] = "REPO-LAYOUT-CANON-01 \u2014 Verify repository root and naming canon before Workbench Foundation"
        green_matrix = copy.deepcopy(matrix)
        for row in green_matrix["rows"]:
            row["status"] = "pass"
        self.assertEqual([], validate_decision(promoted_decision))
        self.assertEqual([], validate_validation_matrix(green_matrix, promoted_decision))


if __name__ == "__main__":
    unittest.main()
