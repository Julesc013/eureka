from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_dev_to_main_promotion_03.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_dev_to_main_promotion_03", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DevToMainPromotion03Tests(unittest.TestCase):
    def test_scope_matrix_covers_source_snapshot_baseline(self) -> None:
        payload = json.loads((REPO_ROOT / "control/inventory/dev_to_main_promotion_03_scope_matrix.json").read_text(encoding="utf-8"))
        scope_ids = {item["subsystem_id"] for item in payload["promotion_scope"]}

        self.assertEqual(scope_ids, set(load_validator().RESULT_FILES))

    def test_external_full_discovery_evidence_is_green(self) -> None:
        result = json.loads((REPO_ROOT / "control/inventory/dev_to_main_promotion_03_result.json").read_text(encoding="utf-8"))

        self.assertTrue(result["full_unittest_discovery_passed"])
        self.assertEqual(result["full_unittest_discovery_count"], 5008)
        self.assertEqual(result["full_unittest_discovery_failures"], 0)
        self.assertEqual(result["full_unittest_discovery_errors"], 0)
        self.assertEqual(result["full_unittest_discovery_exit_code"], 0)
        self.assertTrue(result["expected_refusal_trace_nonblocking"])

    def test_boundary_report_keeps_unsafe_actions_disabled(self) -> None:
        boundary = json.loads((REPO_ROOT / "control/inventory/dev_to_main_promotion_03_boundary_report.json").read_text(encoding="utf-8"))

        for field in load_validator().BOUNDARY_FALSE_FIELDS:
            self.assertFalse(boundary[field], field)

    def test_branch_state_shape_is_fast_forwardable_or_equal(self) -> None:
        branch_state = json.loads((REPO_ROOT / "control/inventory/dev_to_main_promotion_03_branch_state.json").read_text(encoding="utf-8"))

        self.assertEqual(branch_state["branch"], "dev")
        self.assertRegex(branch_state["ahead_behind_origin_main_origin_dev_before"], r"^0\s+\d+$")
        self.assertTrue(branch_state["origin_main_can_fast_forward_to_origin_dev"])
        self.assertTrue(branch_state["working_tree_clean_before"])

    def test_validator_passes(self) -> None:
        result = load_validator().validate(REPO_ROOT)

        self.assertEqual(result["status"], "pass", result["errors"])


if __name__ == "__main__":
    unittest.main()
