from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from runtime.local_foundry.workunit_dry_run import (
    build_workunit_dry_run_result,
    classify_actions_for_dry_run,
    detect_forbidden_runtime_claims,
    detect_truth_boundary_violations,
    evaluate_required_capabilities,
    evaluate_required_node_modes,
    summarize_workunit_dry_run,
    validate_dry_run_result,
)


ROOT = Path(__file__).resolve().parents[2]
WORKUNIT_EXAMPLES = ROOT / "examples" / "work_units"


class WorkUnitDryRunRuntimeTests(unittest.TestCase):
    def test_dry_run_builds_workunit_result_from_search_need_review_example(self) -> None:
        result = build_workunit_dry_run_result(
            _workunit("search_need_review_v0"),
            source_workunit_ref="examples/work_units/search_need_review_v0/work_unit.json",
        )

        self.assertEqual(result["schema_version"], "work_unit_result.v0")
        self.assertEqual(result["workunit_result_status"], "pass")
        self.assertEqual(result["execution_mode"], "dry_run_only")
        self.assertEqual(result["executed_actions"], [])
        self.assertEqual(validate_dry_run_result(result), [])

    def test_dry_run_handles_policy_blocked_workunit(self) -> None:
        result = build_workunit_dry_run_result(
            _workunit("policy_blocked_work_unit_v0"),
            source_workunit_ref="examples/work_units/policy_blocked_work_unit_v0/work_unit.json",
        )

        self.assertEqual(result["workunit_result_status"], "policy_blocked")
        self.assertEqual(result["execution_mode"], "blocked")
        self.assertEqual(result["executed_actions"], [])
        self.assertEqual(validate_dry_run_result(result), [])

    def test_dry_run_can_emit_noop_result_from_already_satisfied_fixture(self) -> None:
        fixture = _workunit("candidate_dedup_v0")
        fixture["dry_run_fixture"] = {"already_satisfied": True}

        result = build_workunit_dry_run_result(
            fixture,
            source_workunit_ref="examples/work_units/candidate_dedup_v0/work_unit.json",
        )

        self.assertEqual(result["workunit_result_status"], "noop")
        self.assertTrue(result["noop_result"]["noop_recorded"])
        self.assertTrue(result["idempotency_result"]["safe_to_rerun"])
        self.assertEqual(validate_dry_run_result(result), [])

    def test_required_node_mode_check_works(self) -> None:
        fixture = _workunit("search_need_review_v0")
        self.assertEqual(evaluate_required_node_modes(fixture)["status"], "pass")

        fixture["required_node_modes"] = ["unknown_mode"]
        result = evaluate_required_node_modes(fixture)

        self.assertEqual(result["status"], "fail")
        self.assertIn("unknown required node mode: unknown_mode", result["errors"])

    def test_required_capability_check_works(self) -> None:
        fixture = _workunit("search_need_review_v0")
        result = evaluate_required_capabilities(fixture)

        self.assertEqual(result["status"], "pass")
        self.assertIn("search_need_analysis", result["required_capabilities"])

    def test_unknown_node_capability_fails(self) -> None:
        fixture = _workunit("search_need_review_v0")
        fixture["required_node_capabilities"] = [{"capability_id": "unknown_capability", "required": True}]

        result = evaluate_required_capabilities(fixture)

        self.assertEqual(result["status"], "fail")
        self.assertIn("unknown required node capability: unknown_capability", result["errors"])

    def test_network_required_current_workunit_is_blocked(self) -> None:
        fixture = _workunit("search_need_review_v0")
        fixture["network_requirements"]["network_required"] = True

        result = build_workunit_dry_run_result(fixture, source_workunit_ref="examples/work_units/search_need_review_v0/work_unit.json")

        self.assertEqual(result["workunit_result_status"], "blocked")
        self.assertEqual(result["executed_actions"], [])

    def test_model_required_current_workunit_is_blocked(self) -> None:
        fixture = _workunit("search_need_review_v0")
        fixture["model_provider_requirements"]["model_provider_required"] = True

        result = build_workunit_dry_run_result(fixture, source_workunit_ref="examples/work_units/search_need_review_v0/work_unit.json")

        self.assertEqual(result["workunit_result_status"], "blocked")
        self.assertFalse(result["execution_summary"]["model_provider_used"])

    def test_credential_required_current_workunit_is_blocked(self) -> None:
        fixture = _workunit("search_need_review_v0")
        fixture["credential_requirements"]["credentials_required"] = True

        result = build_workunit_dry_run_result(fixture, source_workunit_ref="examples/work_units/search_need_review_v0/work_unit.json")

        self.assertEqual(result["workunit_result_status"], "blocked")
        self.assertEqual(result["executed_actions"], [])

    def test_forbidden_action_is_not_executed_and_reported(self) -> None:
        fixture = _workunit("search_need_review_v0")
        fixture["allowed_actions"] = ["mutate_master_index"]

        actions = classify_actions_for_dry_run(fixture)

        self.assertEqual(actions["executed_actions"], [])
        self.assertTrue(any(action["action_type"] == "mutate_master_index" for action in actions["forbidden_actions_checked"]))

    def test_product_boundary_true_claim_fails(self) -> None:
        result = build_workunit_dry_run_result(
            _workunit("search_need_review_v0"),
            source_workunit_ref="examples/work_units/search_need_review_v0/work_unit.json",
        )
        result["product_boundary"]["enabled_telemetry"] = True

        errors = detect_forbidden_runtime_claims(result)

        self.assertTrue(any("enabled_telemetry" in error for error in errors))

    def test_truth_boundary_true_claim_fails(self) -> None:
        result = build_workunit_dry_run_result(
            _workunit("search_need_review_v0"),
            source_workunit_ref="examples/work_units/search_need_review_v0/work_unit.json",
        )
        result["truth_boundary"]["result_mutates_master_index"] = True

        errors = detect_truth_boundary_violations(result)

        self.assertTrue(any("result_mutates_master_index" in error for error in errors))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            result = build_workunit_dry_run_result(
                _workunit("source_lead_inspection_v0"),
                source_workunit_ref="examples/work_units/source_lead_inspection_v0/work_unit.json",
            )
            summary = summarize_workunit_dry_run(result)

        self.assertEqual(summary["executed_action_count"], 0)
        self.assertEqual(validate_dry_run_result(result), [])

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        before = _private_root_state()

        result = build_workunit_dry_run_result(
            _workunit("search_need_review_v0"),
            source_workunit_ref="examples/work_units/search_need_review_v0/work_unit.json",
        )

        self.assertFalse(result["truth_boundary"]["result_mutates_master_index"])
        self.assertFalse(result["product_boundary"]["mutated_master_index"])
        self.assertEqual(before, _private_root_state())


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _workunit(name: str) -> dict:
    return deepcopy(_read_json(WORKUNIT_EXAMPLES / name / "work_unit.json"))


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local": (ROOT / ".aide.local").exists(),
        ".local/eureka": (ROOT / ".local" / "eureka").exists(),
        ".cache/eureka": (ROOT / ".cache" / "eureka").exists(),
    }


if __name__ == "__main__":
    unittest.main()
