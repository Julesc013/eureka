from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.validate_public_alpha_readonly_closeout import (
    BOUNDARY_FALSE_FIELDS,
    validate_public_alpha_readonly_closeout,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class PublicAlphaReadOnlyCloseoutTests(unittest.TestCase):
    def test_validator_accepts_passing_closeout_state(self) -> None:
        report = validate_public_alpha_readonly_closeout()

        self.assertEqual(report["status"], "pass", report["errors"])
        self.assertTrue(report["external_full_discovery_summary_received"])
        self.assertTrue(report["full_unittest_discovery_passed"])
        self.assertEqual(report["full_unittest_discovery_count"], 5050)
        self.assertTrue(report["public_alpha_ready_for_main_promotion"])

    def test_scope_matrix_records_current_result_file_mapping(self) -> None:
        scope = load_json("control/inventory/public_alpha_readonly_closeout_scope_matrix.json")
        mappings = {item["expected"]: item["actual"] for item in scope["result_file_mappings"]}

        self.assertEqual(
            mappings["control/inventory/public_alpha_readonly_result.json"],
            "control/inventory/public_alpha_readonly_00_result.json",
        )
        self.assertEqual(
            mappings["control/inventory/public_alpha_hosting_result.json"],
            "control/inventory/public_alpha_hosting_result.json",
        )

    def test_route_and_api_matrices_are_read_only(self) -> None:
        route_matrix = load_json("control/inventory/public_alpha_readonly_closeout_route_matrix.json")
        api_matrix = load_json("control/inventory/public_alpha_readonly_closeout_api_matrix.json")

        self.assertGreaterEqual(len(route_matrix["routes"]), 6)
        for route in route_matrix["routes"]:
            self.assertIs(route["read_only"], True)
            self.assertIs(route["snapshot_backed"], True)
            self.assertIs(route["relay_backed"], True)
            self.assertIs(route["public_mutation_enabled"], False)

        self.assertEqual(api_matrix["read_only_methods"], ["GET", "HEAD"])
        self.assertIs(api_matrix["public_write_actions_enabled"], False)
        self.assertIs(api_matrix["public_live_source_fanout_enabled"], False)
        self.assertIs(api_matrix["download_enabled"], False)
        self.assertIs(api_matrix["extraction_enabled"], False)
        self.assertIs(api_matrix["model_provider_enabled"], False)

    def test_hosting_and_security_closeout_are_present(self) -> None:
        hosting = load_json("control/inventory/public_alpha_readonly_closeout_hosting_matrix.json")
        security = load_json("control/inventory/public_alpha_readonly_closeout_security_matrix.json")

        self.assertIn("static_snapshot_site", hosting["hosting_modes_verified"])
        self.assertIn("read_only_relay_service", hosting["preferred_initial_modes"])
        self.assertIs(hosting["external_full_discovery_required_before_promotion"], True)
        self.assertIs(security["security_model_exists"], True)
        self.assertIs(security["rate_limit_model_exists"], True)
        self.assertIs(security["rollback_plan_exists"], True)
        self.assertIs(security["public_mutation_enabled"], False)

    def test_boundary_report_keeps_unsafe_actions_disabled(self) -> None:
        boundary = load_json("control/inventory/public_alpha_readonly_closeout_boundary_report.json")

        for field in BOUNDARY_FALSE_FIELDS:
            self.assertIs(boundary[field], False, field)

    def test_external_full_discovery_handoff_is_repo_external(self) -> None:
        handoff = load_json("control/inventory/public_alpha_readonly_closeout_full_discovery_handoff.json")
        result = load_json("control/inventory/public_alpha_readonly_closeout_result.json")

        self.assertEqual(handoff["status"], "WAITING_FOR_EXTERNAL_FULL_DISCOVERY")
        self.assertIn("../eureka-test-runs/public_alpha_readonly_closeout", handoff["command"])
        self.assertIs(handoff["full_discovery_run_inside_ai"], False)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["external_full_discovery_summary_received"])
        self.assertTrue(result["full_unittest_discovery_passed"])
        self.assertTrue(result["public_alpha_ready_for_main_promotion"])


if __name__ == "__main__":
    unittest.main()
