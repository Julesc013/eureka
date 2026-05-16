from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class AideEvalNoProductMutationTests(unittest.TestCase):
    def test_result_records_no_forbidden_execution(self) -> None:
        result = load_json("control/inventory/aide_eval_green_result.json")
        for field in [
            "product_behavior_changed",
            "provider_model_network_calls_used",
            "source_probe_executed",
            "extraction_executed",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ]:
            self.assertFalse(result[field], field)

    def test_repair_plan_forbids_product_behavior_changes(self) -> None:
        plan = load_json("control/inventory/aide_eval_repair_plan.json")
        self.assertFalse(plan["product_behavior_changes_allowed"])
        self.assertFalse(plan["provider_model_network_calls_allowed"])
        self.assertFalse(plan["main_promotion_allowed"])

    def test_large_report_warning_is_resolved(self) -> None:
        warning = load_json("control/inventory/aide_eval_green_large_report_warning.json")
        self.assertEqual(warning["oversized_reports_after"], [])
        self.assertEqual(warning["warnings_remaining"], 0)


if __name__ == "__main__":
    unittest.main()

