from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from runtime.local.foundry.node_policy_evaluator import (
    build_node_policy_evaluation_result,
    detect_policy_boundary_violations,
    detect_truth_boundary_violations,
    summarize_node_policy_evaluation,
    validate_node_policy_evaluation_result,
)


ROOT = Path(__file__).resolve().parents[2]


class NodePolicyEvaluatorRuntimeTests(unittest.TestCase):
    def test_evaluator_allows_local_private_search_need_review_for_dry_run(self) -> None:
        result = _evaluate(
            "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
            "examples/nodes/policies/local_private_node_policy_v0.json",
            "examples/work_units/search_need_review_v0/work_unit.json",
        )

        self.assertEqual(result["decision"], "allowed_for_dry_run")
        self.assertTrue(result["allowed_for_dry_run"])
        self.assertFalse(result["allowed_for_execution"])
        self.assertEqual(validate_node_policy_evaluation_result(result), [])

    def test_evaluator_blocks_network_required_workunit_for_current_local_node(self) -> None:
        workunit = _json("examples/work_units/search_need_review_v0/work_unit.json")
        workunit["network_requirements"]["network_required"] = True

        result = _evaluate_inline(workunit=workunit)

        self.assertEqual(result["decision"], "blocked_by_network_requirement")
        self.assertFalse(result["allowed_for_dry_run"])
        self.assertFalse(result["product_boundary"]["enabled_network_access"])

    def test_evaluator_blocks_unknown_capability(self) -> None:
        workunit = _json("examples/work_units/search_need_review_v0/work_unit.json")
        workunit["required_node_capabilities"] = [{"capability_id": "unknown_capability", "required": True}]

        result = _evaluate_inline(workunit=workunit)

        self.assertEqual(result["decision"], "blocked_by_unknown_capability")
        self.assertTrue(any("unknown capability" in error for error in result["errors"]))

    def test_evaluator_blocks_forbidden_input(self) -> None:
        workunit = _json("examples/work_units/search_need_review_v0/work_unit.json")
        workunit["input_refs"].append({"input_type": "secret_or_credential", "input_ref": "fixture_only"})

        result = _evaluate_inline(workunit=workunit)

        self.assertEqual(result["decision"], "blocked_by_forbidden_input")

    def test_evaluator_blocks_forbidden_output(self) -> None:
        workunit = _json("examples/work_units/search_need_review_v0/work_unit.json")
        workunit["expected_outputs"].append({"output_type": "master_index_mutation", "output_requires_review": True})

        result = _evaluate_inline(workunit=workunit)

        self.assertEqual(result["decision"], "blocked_by_forbidden_output")

    def test_evaluator_blocks_forbidden_action(self) -> None:
        workunit = _json("examples/work_units/search_need_review_v0/work_unit.json")
        workunit["allowed_actions"].append("mutate_master_index")

        result = _evaluate_inline(workunit=workunit)

        self.assertEqual(result["decision"], "blocked_by_forbidden_action")
        self.assertIn("mutate_master_index", result["blocked_actions"])

    def test_evaluator_marks_future_metadata_probe_as_gated(self) -> None:
        result = _evaluate(
            "examples/nodes/institution_node_future_v0/eureka_node_manifest.json",
            "examples/nodes/policies/institution_node_future_policy_v0.json",
            "examples/work_units/approved_metadata_probe_future_v0/work_unit.json",
        )

        self.assertEqual(result["decision"], "approval_gated")
        self.assertFalse(result["allowed_for_dry_run"])
        self.assertFalse(result["product_boundary"]["enabled_network_access"])

    def test_evaluator_marks_policy_blocked_workunit_as_blocked(self) -> None:
        result = _evaluate(
            "examples/nodes/local_autonomous_dry_run_node_v0/eureka_node_manifest.json",
            "examples/nodes/policies/local_autonomous_dry_run_node_policy_v0.json",
            "examples/work_units/policy_blocked_work_unit_v0/work_unit.json",
        )

        self.assertEqual(result["decision"], "blocked_by_policy")
        self.assertFalse(result["allowed_for_dry_run"])

    def test_evaluator_can_report_noop_repeated_workunit_posture(self) -> None:
        workunit = _json("examples/work_units/search_need_review_v0/work_unit.json")
        workunit["dry_run_fixture"] = {"already_satisfied": True}

        result = _evaluate_inline(workunit=workunit)

        self.assertEqual(result["decision"], "allowed_as_noop")
        self.assertEqual(result["evaluation_status"], "noop")
        self.assertTrue(result["allowed_for_dry_run"])

    def test_product_boundary_true_claim_fails(self) -> None:
        result = _evaluate(
            "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
            "examples/nodes/policies/local_private_node_policy_v0.json",
            "examples/work_units/search_need_review_v0/work_unit.json",
        )
        result["product_boundary"]["enabled_telemetry"] = True

        errors = detect_policy_boundary_violations(result)

        self.assertTrue(any("enabled_telemetry" in error for error in errors))

    def test_truth_boundary_true_claim_fails(self) -> None:
        result = _evaluate(
            "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
            "examples/nodes/policies/local_private_node_policy_v0.json",
            "examples/work_units/search_need_review_v0/work_unit.json",
        )
        result["truth_boundary"]["evaluation_result_can_mutate_master_index"] = True

        errors = detect_truth_boundary_violations(result)

        self.assertTrue(any("evaluation_result_can_mutate_master_index" in error for error in errors))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            result = _evaluate(
                "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
                "examples/nodes/policies/local_private_node_policy_v0.json",
                "examples/work_units/search_need_review_v0/work_unit.json",
            )
            summary = summarize_node_policy_evaluation(result)

        self.assertIn("Allowed for execution: false", summary)
        self.assertFalse(result["product_boundary"]["enabled_model_provider_calls"])

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        before = _private_root_state()

        result = _evaluate(
            "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
            "examples/nodes/policies/local_private_node_policy_v0.json",
            "examples/work_units/search_need_review_v0/work_unit.json",
        )

        self.assertFalse(result["allowed_for_master_index_mutation"])
        self.assertFalse(result["product_boundary"]["mutated_master_index"])
        self.assertEqual(before, _private_root_state())


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _evaluate(node_manifest: str, node_policy: str, workunit: str) -> dict:
    return build_node_policy_evaluation_result(
        {
            "node_manifest": _json(node_manifest),
            "node_policy": _json(node_policy),
            "workunit": _json(workunit),
            "capability_matrix": _json("control/inventory/nodes/node_capability_matrix.json"),
            "node_manifest_path": node_manifest,
            "node_policy_path": node_policy,
            "workunit_path": workunit,
        }
    )


def _evaluate_inline(workunit: dict) -> dict:
    return build_node_policy_evaluation_result(
        {
            "node_manifest": _json("examples/nodes/local_private_node_v0/eureka_node_manifest.json"),
            "node_policy": _json("examples/nodes/policies/local_private_node_policy_v0.json"),
            "workunit": deepcopy(workunit),
            "capability_matrix": _json("control/inventory/nodes/node_capability_matrix.json"),
            "node_manifest_path": "examples/nodes/local_private_node_v0/eureka_node_manifest.json",
            "node_policy_path": "examples/nodes/policies/local_private_node_policy_v0.json",
            "workunit_path": "inline_workunit_fixture",
        }
    )


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local": (ROOT / ".aide.local").exists(),
        ".local/eureka": (ROOT / ".local" / "eureka").exists(),
        ".cache/eureka": (ROOT / ".cache" / "eureka").exists(),
    }


if __name__ == "__main__":
    unittest.main()

