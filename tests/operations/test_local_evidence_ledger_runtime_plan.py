from __future__ import annotations

import json
from pathlib import Path
import socket
from unittest import mock
import unittest

from scripts.validate_local_evidence_ledger_runtime_plan import (
    output_path_allowed,
    validate_bridge_plan,
    validate_local_evidence_ledger_runtime_plan,
    validate_plan_record,
)


ROOT = Path(__file__).resolve().parents[2]
PLAN_EXAMPLE = ROOT / "examples/evidence_ledger_plans/minimal_local_evidence_ledger_plan_v0.json"
BRIDGE_PLAN = ROOT / "control/inventory/evidence_ledger/source_cache_to_evidence_bridge_plan.json"


class LocalEvidenceLedgerRuntimePlanTests(unittest.TestCase):
    def test_valid_evidence_ledger_plans_pass(self) -> None:
        report = validate_local_evidence_ledger_runtime_plan(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_current_plan_enabling_runtime_fails(self) -> None:
        plan = _plan()
        plan["runtime_status"] = "implemented"
        plan["product_boundary"]["implemented_evidence_ledger_runtime"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "runtime_status"))
        self.assertTrue(_has_error(errors, "implemented_evidence_ledger_runtime"))

    def test_current_plan_enabling_source_cache_bridge_runtime_fails(self) -> None:
        plan = _plan()
        plan["source_cache_bridge_status"] = "implemented"
        plan["product_boundary"]["implemented_source_cache_bridge"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "source_cache_bridge_status"))
        self.assertTrue(_has_error(errors, "implemented_source_cache_bridge"))

    def test_current_plan_accepting_evidence_truth_fails(self) -> None:
        plan = _plan()
        plan["evidence_acceptance_status"] = "accepted"
        plan["truth_boundary"]["evidence_record_is_accepted_evidence"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "evidence_acceptance_status"))
        self.assertTrue(_has_error(errors, "evidence_record_is_accepted_evidence"))

    def test_current_plan_enabling_master_index_mutation_fails(self) -> None:
        plan = _plan()
        plan["truth_boundary"]["evidence_record_can_mutate_master_index"] = True
        plan["product_boundary"]["mutated_master_index"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "evidence_record_can_mutate_master_index"))
        self.assertTrue(_has_error(errors, "mutated_master_index"))

    def test_source_cache_bridge_without_review_gate_fails(self) -> None:
        bridge = _bridge()
        bridge["review_required_before_bridge"] = False

        errors = validate_bridge_plan(bridge, "synthetic")

        self.assertTrue(_has_error(errors, "review_required_before_bridge"))

    def test_source_observation_converted_to_accepted_truth_fails(self) -> None:
        from scripts.validate_local_evidence_ledger_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content({"notes": ["converted source observation to accepted truth"]}, "synthetic")

        self.assertTrue(_has_error(errors, "forbidden claim"))

    def test_evidence_candidate_converted_to_verified_fact_fails(self) -> None:
        from scripts.validate_local_evidence_ledger_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content({"notes": ["evidence candidate converted to verified fact"]}, "synthetic")

        self.assertTrue(_has_error(errors, "forbidden claim"))

    def test_ai_draft_marked_evidence_truth_fails(self) -> None:
        from scripts.validate_local_evidence_ledger_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content({"notes": ["AI draft is evidence truth"]}, "synthetic")

        self.assertTrue(_has_error(errors, "forbidden claim"))

    def test_automatic_public_index_use_fails(self) -> None:
        plan = _plan()
        plan["review_gates"]["automatic_public_index_use_allowed"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "automatic_public_index_use_allowed"))

    def test_automatic_master_index_mutation_fails(self) -> None:
        plan = _plan()
        plan["review_gates"]["automatic_master_index_mutation_allowed"] = True

        errors = validate_plan_record(plan, "synthetic")

        self.assertTrue(_has_error(errors, "automatic_master_index_mutation_allowed"))

    def test_forbidden_output_root_fails(self) -> None:
        self.assertFalse(output_path_allowed(ROOT / "site/dist/evidence.json", ROOT))
        self.assertFalse(output_path_allowed(ROOT / "runtime/evidence.json", ROOT))
        self.assertFalse(output_path_allowed(ROOT / "contracts/evidence.json", ROOT))

    def test_private_path_outside_documented_future_roots_fails(self) -> None:
        from scripts.validate_local_evidence_ledger_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content({"notes": ["C:\\Users\\Example\\private-evidence-ledger"]}, "synthetic")

        self.assertTrue(_has_error(errors, "private path"))

    def test_rights_malware_installability_exhaustive_claim_fails(self) -> None:
        from scripts.validate_local_evidence_ledger_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content(
            {
                "notes": [
                    "rights clearance confirmed",
                    "malware safety confirmed",
                    "verified installability",
                    "exhaustive global search complete",
                ]
            },
            "synthetic",
        )

        self.assertGreaterEqual(len(errors), 4)

    def test_credential_api_key_fixture_fails(self) -> None:
        from scripts.validate_local_evidence_ledger_runtime_plan import _scan_payload_for_forbidden_content

        errors = _scan_payload_for_forbidden_content({"notes": ["api_key=abcdef1234567890"]}, "synthetic")

        self.assertTrue(_has_error(errors, "credential/API-key"))

    def test_validator_does_not_create_local_state(self) -> None:
        before = _private_root_state()

        report = validate_local_evidence_ledger_runtime_plan(ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _private_root_state())

    def test_validator_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch.object(socket, "create_connection", side_effect=AssertionError("network call blocked")):
            report = validate_local_evidence_ledger_runtime_plan(ROOT)

        self.assertEqual(report["status"], "valid")


def _plan() -> dict[str, object]:
    return json.loads(PLAN_EXAMPLE.read_text(encoding="utf-8"))


def _bridge() -> dict[str, object]:
    return json.loads(BRIDGE_PLAN.read_text(encoding="utf-8"))


def _has_error(errors: list[str], needle: str) -> bool:
    return any(needle in error for error in errors)


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local/eureka/evidence_ledger": (ROOT / ".aide.local" / "eureka" / "evidence_ledger").exists(),
        ".local/eureka/evidence_ledger": (ROOT / ".local" / "eureka" / "evidence_ledger").exists(),
        ".cache/eureka/evidence_ledger": (ROOT / ".cache" / "eureka" / "evidence_ledger").exists(),
    }


if __name__ == "__main__":
    unittest.main()
