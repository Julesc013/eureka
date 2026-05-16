from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class AideEvalGreenTests(unittest.TestCase):
    def test_green_result_requires_zero_eval_failures(self) -> None:
        result = load_json("control/inventory/aide_eval_green_result.json")
        self.assertEqual(result["task"], "AIDE-EVAL-GREEN-01")
        self.assertTrue(result["aide_eval_green"])
        self.assertEqual(result["eval_fail_count_after"], 0)
        self.assertEqual(result["eval_task_count_after"], result["eval_pass_count_after"])

    def test_next_task_decision_is_explicit(self) -> None:
        decision = load_json("control/inventory/aide_eval_green_next_task_decision.json")
        self.assertEqual(decision["recommended_next_task"], "HUNT-TO-MAIN-PROMOTION-REVIEW")
        self.assertTrue(decision["main_promotion_review_required"])
        self.assertTrue(decision["syn_can_start"])
        self.assertFalse(decision["f0_recommended_now"])

    def test_warning_and_blocker_registers_are_clear(self) -> None:
        warnings = load_json("control/inventory/aide_eval_green_warning_disposition.json")
        blockers = load_json("control/inventory/aide_eval_green_blocker_register.json")
        self.assertEqual(warnings["warnings_remaining"], 0)
        self.assertEqual(blockers["hard_blockers_remaining"], 0)
        self.assertEqual(blockers["blockers"], [])


if __name__ == "__main__":
    unittest.main()

