from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.validate_public_alpha_hosting_readiness import validate_public_alpha_hosting_readiness


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class PublicAlphaHostingReadinessTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        report = validate_public_alpha_hosting_readiness()
        self.assertEqual(report["status"], "valid", report["errors"])

    def test_hosting_modes_are_defined(self) -> None:
        result = load_json("control/inventory/public_alpha_hosting_result.json")
        self.assertEqual(
            set(result["hosting_modes_defined"]),
            {
                "static_snapshot_site",
                "read_only_relay_service",
                "local_preview_server",
                "future_dynamic_gateway",
            },
        )
        self.assertIn("static_snapshot_site", result["preferred_initial_modes"])
        self.assertIn("read_only_relay_service", result["preferred_initial_modes"])

    def test_no_deploy_and_non_claim_policies_hold(self) -> None:
        no_deploy = load_json("control/policies/public_alpha_no_deploy_policy.json")
        non_claim = load_json("control/policies/public_alpha_non_claim_policy.json")
        self.assertIs(no_deploy["deployment_allowed_current"], False)
        self.assertIs(no_deploy["deployment_performed"], False)
        self.assertIs(no_deploy["requires_future_operator_approval"], True)
        self.assertIs(non_claim["production_readiness_claimed"], False)
        self.assertIs(non_claim["public_launch_readiness_claimed"], False)

    def test_launch_gates_require_future_approval(self) -> None:
        launch_gate = load_json("contracts/publication/public_alpha_launch_gate.v0.json")
        props = launch_gate["properties"]
        self.assertIs(props["launch_allowed_current"]["const"], False)
        self.assertIs(props["deployment_approval_required"]["const"], True)
        self.assertIs(props["external_full_discovery_required"]["const"], True)

    def test_public_mutation_and_live_source_fanout_disabled(self) -> None:
        api_matrix = load_json("control/inventory/public_alpha_hosting_api_matrix.json")
        boundary = load_json("control/inventory/public_alpha_hosting_boundary_report.json")
        self.assertIs(api_matrix["public_write_actions_enabled"], False)
        self.assertIs(api_matrix["live_source_fanout_enabled"], False)
        self.assertIs(boundary["public_mutation_enabled"], False)
        self.assertIs(boundary["live_source_call_performed"], False)
        self.assertIs(boundary["download_performed"], False)
        self.assertIs(boundary["extraction_executed"], False)
        self.assertIs(boundary["model_provider_used"], False)

    def test_rollback_docs_present(self) -> None:
        rollback_doc = (REPO_ROOT / "docs/operations/PUBLIC_ALPHA_ROLLBACK_RUNBOOK.md").read_text(encoding="utf-8")
        rollback_matrix = load_json("control/inventory/public_alpha_hosting_rollback_matrix.json")
        self.assertIn("Static Snapshot Site", rollback_doc)
        self.assertIn("Read-Only Relay Service", rollback_doc)
        self.assertIs(rollback_matrix["rollback_plan_required"], True)


if __name__ == "__main__":
    unittest.main()
