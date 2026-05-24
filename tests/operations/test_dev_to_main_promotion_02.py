from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "scripts/validate_dev_to_main_promotion_02.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_dev_to_main_promotion_02", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DevToMainPromotion02Tests(unittest.TestCase):
    def test_scope_matrix_covers_local_loop_baseline(self) -> None:
        payload = json.loads((REPO_ROOT / "control/inventory/dev_to_main_promotion_02_scope_matrix.json").read_text(encoding="utf-8"))
        scope_ids = {item["subsystem_id"] for item in payload["promotion_scope"]}

        expected = set(load_validator().RESULT_FILES)
        self.assertTrue(expected.issubset(scope_ids))

    def test_local_loop_and_apply_prerequisites_are_present(self) -> None:
        apply_result = json.loads((REPO_ROOT / "control/inventory/local_apply_gate_result.json").read_text(encoding="utf-8"))
        loop_result = json.loads((REPO_ROOT / "control/inventory/workbench_local_loop_result.json").read_text(encoding="utf-8"))

        self.assertEqual(apply_result["status"], "pass")
        self.assertEqual(loop_result["status"], "pass")
        self.assertTrue(loop_result["search_after_apply_passed"])
        self.assertTrue(loop_result["search_after_rollback_passed"])
        self.assertFalse(loop_result["operator_instance_mutated"])

    def test_boundary_report_keeps_unsafe_actions_disabled(self) -> None:
        boundary = json.loads((REPO_ROOT / "control/inventory/dev_to_main_promotion_02_boundary_report.json").read_text(encoding="utf-8"))

        for field in load_validator().BOUNDARY_FALSE_FIELDS:
            self.assertFalse(boundary[field], field)

    def test_branch_state_shape_is_fast_forwardable_or_equal(self) -> None:
        branch_state = json.loads((REPO_ROOT / "control/inventory/dev_to_main_promotion_02_branch_state.json").read_text(encoding="utf-8"))

        self.assertEqual(branch_state["branch"], "dev")
        self.assertRegex(branch_state["ahead_behind_origin_main_origin_dev"], r"^0\s+\d+$")
        self.assertTrue(branch_state["working_tree_clean_before"])

    def test_validator_passes(self) -> None:
        result = load_validator().validate(REPO_ROOT)

        self.assertEqual(result["status"], "pass", result["errors"])


if __name__ == "__main__":
    unittest.main()
