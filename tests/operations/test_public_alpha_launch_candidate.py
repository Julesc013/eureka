from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.validate_public_alpha_launch_candidate import (
    BOUNDARY_FALSE_FIELDS,
    validate_public_alpha_launch_candidate,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class PublicAlphaLaunchCandidateTests(unittest.TestCase):
    def test_validator_accepts_launch_candidate_state(self) -> None:
        report = validate_public_alpha_launch_candidate()

        self.assertEqual(report["status"], "pass", report["errors"])
        self.assertTrue(report["external_full_discovery_verified"])
        self.assertEqual(report["external_full_discovery_tests_run"], 5057)
        self.assertEqual(report["hard_blockers_remaining"], 0)
        self.assertEqual(report["launch_warnings_remaining"], 0)
        self.assertTrue(report["launch_candidate_ready"])

    def test_result_is_candidate_without_launch_claim(self) -> None:
        result = load_json("control/inventory/public_alpha_launch_candidate_result.json")

        self.assertTrue(result["launch_candidate_ready"])
        self.assertTrue(result["manual_approval_required_for_launch"])
        self.assertFalse(result["deployment_performed"])
        self.assertFalse(result["production_readiness_claimed"])
        self.assertFalse(result["public_launch_readiness_claimed"])
        self.assertTrue(result["recommended_next_task"].startswith("PUBLIC-ALPHA-DEPLOY-DRY-RUN-00"))

    def test_route_and_api_matrices_are_strictly_read_only(self) -> None:
        routes = load_json("control/inventory/public_alpha_launch_candidate_route_matrix.json")
        api = load_json("control/inventory/public_alpha_launch_candidate_api_matrix.json")

        self.assertGreaterEqual(len(routes["routes"]), 6)
        for route in routes["routes"]:
            self.assertTrue(route["read_only"])
            self.assertTrue(route["snapshot_backed"])
            self.assertTrue(route["relay_backed"])
            self.assertFalse(route["public_mutation_enabled"])
            self.assertFalse(route["live_source_fanout_enabled"])

        self.assertEqual(api["read_only_methods"], ["GET", "HEAD"])
        self.assertTrue(api["public_api_read_only"])
        self.assertFalse(api["public_write_actions_enabled"])
        self.assertFalse(api["public_mutation_enabled"])
        self.assertFalse(api["public_live_source_fanout_enabled"])
        self.assertFalse(api["download_enabled"])
        self.assertFalse(api["extraction_enabled"])
        self.assertFalse(api["model_provider_enabled"])

    def test_blocker_register_has_no_active_hard_blockers(self) -> None:
        blockers = load_json("control/inventory/public_alpha_launch_candidate_blocker_register.json")

        self.assertEqual(blockers["hard_blockers_remaining"], 0)
        self.assertEqual(blockers["launch_warnings_remaining"], 0)
        for item in blockers["register"]:
            if item["classification"] == "hard_blocker":
                self.assertFalse(item["active"], item["id"])

    def test_boundary_report_keeps_unsafe_actions_disabled(self) -> None:
        boundary = load_json("control/inventory/public_alpha_launch_candidate_boundary_report.json")

        for field in BOUNDARY_FALSE_FIELDS:
            self.assertIs(boundary[field], False, field)

    def test_contracts_and_manual_approval_policy_exist(self) -> None:
        candidate = load_json("contracts/publication/public_alpha_launch_candidate.v0.json")
        policy = load_json("control/policies/public_alpha_manual_approval_policy.json")

        self.assertIn("launch_candidate_ready", candidate["required"])
        self.assertTrue(policy["manual_approval_required_for_launch"])
        self.assertFalse(policy["implicit_launch_approval_allowed"])


if __name__ == "__main__":
    unittest.main()
