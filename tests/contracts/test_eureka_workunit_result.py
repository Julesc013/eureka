from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from scripts.validate_eureka_workunit_result import (
    OUTPUT_POLICY_PATH,
    RECOVERY_POLICY_PATH,
    RESULT_POLICY_PATH,
    REVIEW_POLICY_PATH,
    STATUS_REGISTRY_PATH,
    validate_eureka_workunit_result,
    validate_output_policy,
    validate_recovery_policy,
    validate_review_policy,
    validate_status_registry,
    validate_workunit_result_policy,
    validate_workunit_result_record,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class EurekaWorkUnitResultContractTest(unittest.TestCase):
    def test_valid_workunit_result_examples_pass(self) -> None:
        for path in _example_paths():
            with self.subTest(path=path):
                self.assertEqual(
                    validate_workunit_result_record(
                        _read_json(path),
                        path.relative_to(REPO_ROOT).as_posix(),
                        repo_root=REPO_ROOT,
                    ),
                    [],
                )

    def test_current_workunit_result_pack_validates(self) -> None:
        report = validate_eureka_workunit_result(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_invalid_result_status_fails(self) -> None:
        result = _result()
        result["workunit_result_status"] = "green"

        errors = _validate(result)

        self.assertTrue(any("workunit_result_status" in error for error in errors))

    def test_invalid_execution_mode_fails(self) -> None:
        result = _result()
        result["execution_mode"] = "active_runtime"

        errors = _validate(result)

        self.assertTrue(any("execution_mode" in error for error in errors))

    def test_invalid_output_type_fails(self) -> None:
        result = _result()
        result["outputs_proposed"][0]["output_type"] = "mystery_output"

        errors = _validate(result)

        self.assertTrue(any("output_type" in error for error in errors))

    def test_forbidden_output_type_fails(self) -> None:
        result = _result()
        result["outputs_proposed"][0]["output_type"] = "accepted_public_record"

        errors = _validate(result)

        self.assertTrue(any("forbidden" in error for error in errors))

    def test_pass_with_warnings_with_errors_fails(self) -> None:
        result = _result()
        result["validation_summary"]["validation_status"] = "pass_with_warnings"
        result["validation_summary"]["warnings_count"] = 1
        result["validation_summary"]["errors_count"] = 1

        errors = _validate(result)

        self.assertTrue(any("pass_with_warnings" in error for error in errors))

    def test_missing_idempotency_result_fails(self) -> None:
        result = _result()
        result["idempotency_result"].pop("safe_to_rerun")

        errors = _validate(result)

        self.assertTrue(any("idempotency_result" in error for error in errors))

    def test_missing_recovery_result_fails(self) -> None:
        result = _result()
        result["recovery_result"].pop("dirty_tree_handled")

        errors = _validate(result)

        self.assertTrue(any("recovery_result" in error for error in errors))

    def test_missing_review_gates_fail(self) -> None:
        result = _result()
        result["review_gates"] = {}

        errors = _validate(result)

        self.assertTrue(any("review_gates missing" in error for error in errors))

    def test_candidate_output_without_review_gate_fails(self) -> None:
        result = _result("observation_candidate_review_partial_v0")
        result["review_gates"]["candidate_review_required"] = False

        errors = _validate(result)

        self.assertTrue(any("candidate output requires candidate_review_required" in error for error in errors))

    def test_evidence_output_without_review_gate_fails(self) -> None:
        result = _result()
        result["outputs_proposed"][0]["output_type"] = "evidence_draft_future"
        result["outputs_proposed"][0]["output_requires_review"] = True
        result["review_gates"]["evidence_review_required"] = False

        errors = _validate(result)

        self.assertTrue(any("evidence output requires evidence_review_required" in error for error in errors))

    def test_source_lead_output_without_review_gate_fails(self) -> None:
        result = _result("source_lead_inspection_warn_v0")
        result["review_gates"]["source_policy_review_required"] = False

        errors = _validate(result)

        self.assertTrue(any("source lead output requires source_policy_review_required" in error for error in errors))

    def test_truth_boundary_true_claim_fails(self) -> None:
        result = _result()
        result["truth_boundary"]["result_mutates_master_index"] = True

        errors = _validate(result)

        self.assertTrue(any("result_mutates_master_index" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        result = _result()
        result["product_boundary"]["enabled_network_access"] = True

        errors = _validate(result)

        self.assertTrue(any("enabled_network_access" in error for error in errors))

    def test_rights_malware_installability_exhaustive_claim_fails(self) -> None:
        result = _result()
        result["notes"] = [
            "rights clearance confirmed; malware safe; verified installability; exhaustive global search proof"
        ]

        errors = _validate(result)

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safe" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))
        self.assertTrue(any("exhaustive global search" in error for error in errors))

    def test_private_path_credential_api_key_fixture_fails(self) -> None:
        result = _result()
        result["api_key"] = "not-real"
        result["notes"] = ["C:\\Users\\example\\work-unit-result"]

        errors = _validate(result)

        self.assertTrue(any("sensitive key" in error for error in errors))
        self.assertTrue(any("private/local user path" in error for error in errors))

    def test_policy_inventories_validate(self) -> None:
        self.assertEqual(validate_workunit_result_policy(_read_json(REPO_ROOT / RESULT_POLICY_PATH), RESULT_POLICY_PATH), [])
        self.assertEqual(validate_status_registry(_read_json(REPO_ROOT / STATUS_REGISTRY_PATH), STATUS_REGISTRY_PATH), [])
        self.assertEqual(validate_output_policy(_read_json(REPO_ROOT / OUTPUT_POLICY_PATH), OUTPUT_POLICY_PATH), [])
        self.assertEqual(validate_review_policy(_read_json(REPO_ROOT / REVIEW_POLICY_PATH), REVIEW_POLICY_PATH), [])
        self.assertEqual(validate_recovery_policy(_read_json(REPO_ROOT / RECOVERY_POLICY_PATH), RECOVERY_POLICY_PATH), [])

    def test_validator_does_not_create_local_state(self) -> None:
        before = _example_tree()

        report = validate_eureka_workunit_result(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _example_tree())

    def test_validator_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            report = validate_eureka_workunit_result(REPO_ROOT)

        self.assertEqual(report["status"], "valid")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _example_paths() -> list[Path]:
    return sorted((REPO_ROOT / "examples/work_unit_results").glob("*/work_unit_result.json"))


def _result(name: str = "search_need_review_pass_v0") -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/work_unit_results" / name / "work_unit_result.json"))


def _validate(result: dict) -> list[str]:
    return validate_workunit_result_record(result, "broken", repo_root=REPO_ROOT)


def _example_tree() -> list[str]:
    root = REPO_ROOT / "examples/work_unit_results"
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


if __name__ == "__main__":
    unittest.main()
