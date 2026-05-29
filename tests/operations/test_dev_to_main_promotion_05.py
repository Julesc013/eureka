from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.validate_dev_to_main_promotion_05 import (
    BOUNDARY_FALSE_FIELDS,
    validate_dev_to_main_promotion_05,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class DevToMainPromotion05Tests(unittest.TestCase):
    def test_validator_accepts_current_promotion_state(self) -> None:
        report = validate_dev_to_main_promotion_05()

        self.assertIn(report["status"], {"waiting_for_external_full_discovery", "pass"}, report["errors"])
        if report["status"] == "waiting_for_external_full_discovery":
            self.assertFalse(report["external_full_discovery_summary_received"])
            self.assertFalse(report["promotion_performed"])
        else:
            self.assertTrue(report["external_full_discovery_summary_received"])
            self.assertTrue(report["full_unittest_discovery_passed"])
            self.assertTrue(report["promotion_ready"])
        self.assertTrue(report["public_alpha_deploy_dry_run_verified"])
        self.assertTrue(report["public_alpha_launch_candidate_verified"])

    def test_deploy_dry_run_and_launch_candidate_are_safe(self) -> None:
        dry_run = load_json("control/inventory/public_alpha_deploy_dry_run_result.json")
        launch = load_json("control/inventory/public_alpha_launch_candidate_result.json")

        self.assertTrue(dry_run["deploy_dry_run_rehearsal_passed"])
        self.assertTrue(dry_run["deploy_smoke_passed"])
        self.assertTrue(dry_run["rollback_rehearsal_passed"])
        self.assertTrue(launch["launch_candidate_ready"])
        self.assertEqual(launch["hard_blockers_remaining"], 0)
        self.assertFalse(dry_run["deployment_performed"])
        self.assertFalse(dry_run["public_launch_performed"])
        self.assertFalse(launch["public_mutation_enabled"])

    def test_external_full_discovery_handoff_uses_repo_external_gate(self) -> None:
        handoff = load_json("control/inventory/dev_to_main_promotion_05_full_discovery_handoff.json")
        result = load_json("control/inventory/dev_to_main_promotion_05_result.json")

        self.assertIn("--gate promotion_gate", handoff["preferred_command"])
        self.assertIn("../eureka-test-runs/dev_to_main_promotion_05", handoff["alternate_command"])
        self.assertFalse(handoff["full_discovery_run_inside_ai"])
        if result["status"] == "waiting_for_external_full_discovery":
            self.assertEqual(handoff["status"], "WAITING_FOR_EXTERNAL_FULL_DISCOVERY")
            self.assertFalse(result["promotion_performed"])
        else:
            full = load_json("control/inventory/dev_to_main_promotion_05_full_discovery_result.json")
            self.assertEqual(result["status"], "pass")
            self.assertTrue(full["external_summary_received"])
            self.assertTrue(full["full_unittest_discovery_passed"])
            self.assertEqual(full["full_discovery_failures_remaining"], 0)
            self.assertEqual(full["full_discovery_errors_remaining"], 0)

    def test_boundary_report_keeps_forbidden_actions_false(self) -> None:
        boundary = load_json("control/inventory/dev_to_main_promotion_05_boundary_report.json")

        for field in BOUNDARY_FALSE_FIELDS:
            self.assertIs(boundary[field], False, field)


if __name__ == "__main__":
    unittest.main()
