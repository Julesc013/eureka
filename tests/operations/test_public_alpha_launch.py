from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.validate_public_alpha_launch import (
    FALSE_BOUNDARY_FIELDS,
    validate_public_alpha_launch,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class PublicAlphaLaunchTests(unittest.TestCase):
    def test_validator_accepts_waiting_for_manual_approval_state(self) -> None:
        report = validate_public_alpha_launch()

        self.assertEqual(report["status"], "waiting_for_manual_launch_approval", report["errors"])
        self.assertFalse(report["manual_approval_verified"])
        self.assertFalse(report["deployment_performed"])
        self.assertFalse(report["public_launch_performed"])

    def test_result_records_no_launch_without_approval(self) -> None:
        result = load_json("control/inventory/public_alpha_launch_result.json")

        self.assertEqual(result["status"], "waiting_for_manual_launch_approval")
        self.assertTrue(result["promotion_05_verified"])
        self.assertFalse(result["manual_approval_verified"])
        self.assertFalse(result["deployment_performed"])
        self.assertFalse(result["public_launch_performed"])
        self.assertFalse(result["production_readiness_claimed"])
        self.assertFalse(result["public_launch_readiness_claimed"])

    def test_branch_state_classifies_dev_ahead_as_waiting_evidence_only(self) -> None:
        branch = load_json("control/inventory/public_alpha_launch_branch_state.json")

        self.assertTrue(branch["launch_baseline_origin_main_equals_origin_dev"])
        self.assertTrue(branch["dev_ahead_of_main_only_by_waiting_evidence"])
        self.assertFalse(branch["deployment_performed"])
        self.assertFalse(branch["public_launch_performed"])

    def test_boundary_report_keeps_forbidden_actions_false(self) -> None:
        boundary = load_json("control/inventory/public_alpha_launch_boundary_report.json")

        for field in FALSE_BOUNDARY_FIELDS:
            self.assertIs(boundary[field], False, field)


if __name__ == "__main__":
    unittest.main()
