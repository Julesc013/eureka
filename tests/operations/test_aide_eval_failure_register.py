from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class AideEvalFailureRegisterTests(unittest.TestCase):
    def test_failure_register_parses_latest_golden_failures(self) -> None:
        register = json.loads((REPO_ROOT / "control/inventory/aide_eval_failure_register.json").read_text(encoding="utf-8"))
        self.assertEqual(register["failure_count_before"], 9)
        self.assertEqual(len(register["failures"]), 9)
        for failure in register["failures"]:
            for field in [
                "failure_id",
                "golden_task_id",
                "related_paths",
                "checks_run",
                "passed_checks",
                "failed_checks",
                "error_messages",
                "failure_class",
                "safe_to_fix_now",
                "product_behavior_change_required",
                "proposed_repair",
            ]:
                self.assertIn(field, failure)

    def test_safe_repairs_do_not_require_product_behavior_changes(self) -> None:
        register = json.loads((REPO_ROOT / "control/inventory/aide_eval_failure_register.json").read_text(encoding="utf-8"))
        for failure in register["failures"]:
            self.assertTrue(failure["safe_to_fix_now"], failure["failure_id"])
            self.assertFalse(failure["product_behavior_change_required"], failure["failure_id"])


if __name__ == "__main__":
    unittest.main()

