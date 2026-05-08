from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from scripts.validate_eureka_workunit import (
    ACTION_POLICY_PATH,
    IDEMPOTENCY_POLICY_PATH,
    INPUT_OUTPUT_POLICY_PATH,
    NODE_CAPABILITY_MATRIX_PATH,
    NODE_CAPABILITY_REGISTRY_PATH,
    NODE_MODE_REGISTRY_PATH,
    REVIEW_GATE_POLICY_PATH,
    TYPE_REGISTRY_PATH,
    WORKUNIT_POLICY_PATH,
    validate_eureka_workunit,
    validate_workunit_action_policy,
    validate_workunit_idempotency_policy,
    validate_workunit_input_output_policy,
    validate_workunit_policy,
    validate_workunit_record,
    validate_workunit_review_gate_policy,
    validate_workunit_type_registry,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class EurekaWorkUnitContractTest(unittest.TestCase):
    def test_valid_workunit_examples_pass(self) -> None:
        capability_ids, capability_statuses = _capabilities()
        mode_ids = _modes()
        for path in _example_paths():
            with self.subTest(path=path):
                self.assertEqual(
                    validate_workunit_record(
                        _read_json(path),
                        path.relative_to(REPO_ROOT).as_posix(),
                        repo_root=REPO_ROOT,
                        mode_ids=mode_ids,
                        capability_ids=capability_ids,
                        capability_statuses=capability_statuses,
                    ),
                    [],
                )

    def test_current_workunit_pack_validates(self) -> None:
        report = validate_eureka_workunit(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_invalid_workunit_status_fails(self) -> None:
        workunit = _workunit()
        workunit["workunit_status"] = "running_now"

        errors = _validate(workunit)

        self.assertTrue(any("workunit_status" in error for error in errors))

    def test_invalid_workunit_type_fails(self) -> None:
        workunit = _workunit()
        workunit["workunit_type"] = "truth_promotion"

        errors = _validate(workunit)

        self.assertTrue(any("workunit_type" in error for error in errors))

    def test_invalid_scope_fails(self) -> None:
        workunit = _workunit()
        workunit["workunit_scope"] = "public_runtime"

        errors = _validate(workunit)

        self.assertTrue(any("workunit_scope" in error for error in errors))

    def test_unknown_node_capability_fails(self) -> None:
        workunit = _workunit()
        workunit["required_node_capabilities"].append({"capability_id": "magic_runtime", "required": True})

        errors = _validate(workunit)

        self.assertTrue(any("required_node_capabilities unknown" in error for error in errors))

    def test_unknown_node_mode_fails(self) -> None:
        workunit = _workunit()
        workunit["required_node_modes"].append("remote_truth_worker")

        errors = _validate(workunit)

        self.assertTrue(any("required_node_modes unknown" in error for error in errors))

    def test_current_workunit_requiring_network_fails(self) -> None:
        workunit = _workunit()
        workunit["network_requirements"]["network_required"] = True

        errors = _validate(workunit)

        self.assertTrue(any("network_requirements" in error or "future/deferred/gated" in error for error in errors))

    def test_current_workunit_requiring_model_provider_fails(self) -> None:
        workunit = _workunit()
        workunit["model_provider_requirements"]["model_provider_required"] = True

        errors = _validate(workunit)

        self.assertTrue(any("model_provider_requirements" in error or "future/deferred/gated" in error for error in errors))

    def test_current_workunit_requiring_credentials_fails(self) -> None:
        workunit = _workunit()
        workunit["credential_requirements"]["credentials_required"] = True

        errors = _validate(workunit)

        self.assertTrue(any("credential_requirements" in error or "future/deferred/gated" in error for error in errors))

    def test_current_workunit_requiring_local_state_fails(self) -> None:
        workunit = _workunit()
        workunit["local_state_requirements"]["local_state_required"] = True

        errors = _validate(workunit)

        self.assertTrue(any("local_state_requirements" in error or "future/deferred/gated" in error for error in errors))

    def test_future_network_workunit_without_approval_gate_fails(self) -> None:
        workunit = _future_network_workunit()
        workunit["network_requirements"]["operator_approval_required"] = False
        workunit["review_gates"]["operator_approval_required_for_network"] = False

        errors = _validate(workunit)

        self.assertTrue(any("operator_approval" in error for error in errors))

    def test_missing_idempotency_policy_fails(self) -> None:
        workunit = _workunit()
        workunit["idempotency"]["safe_to_rerun"] = False

        errors = _validate(workunit)

        self.assertTrue(any("safe_to_rerun" in error for error in errors))

    def test_missing_recovery_policy_fails(self) -> None:
        workunit = _workunit()
        workunit["recovery_policy"].pop("dirty_tree")

        errors = _validate(workunit)

        self.assertTrue(any("recovery_policy.dirty_tree" in error for error in errors))

    def test_missing_stop_conditions_fail(self) -> None:
        workunit = _workunit()
        workunit["recovery_policy"]["stop_conditions"] = []

        errors = _validate(workunit)

        self.assertTrue(any("stop_conditions missing" in error for error in errors))

    def test_missing_forbidden_actions_fail(self) -> None:
        workunit = _workunit()
        workunit["forbidden_actions"] = []

        errors = _validate(workunit)

        self.assertTrue(any("forbidden_actions missing" in error for error in errors))

    def test_missing_forbidden_outputs_fail(self) -> None:
        workunit = _workunit()
        workunit["forbidden_outputs"] = []

        errors = _validate(workunit)

        self.assertTrue(any("forbidden_outputs missing" in error for error in errors))

    def test_truth_boundary_true_claim_fails(self) -> None:
        workunit = _workunit()
        workunit["truth_boundary"]["can_mutate_master_index"] = True

        errors = _validate(workunit)

        self.assertTrue(any("can_mutate_master_index" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        workunit = _workunit()
        workunit["product_boundary"]["enabled_network_access"] = True

        errors = _validate(workunit)

        self.assertTrue(any("enabled_network_access" in error for error in errors))

    def test_rights_malware_installability_exhaustive_claim_fails(self) -> None:
        workunit = _workunit()
        workunit["notes"] = [
            "rights clearance confirmed; malware safe; verified installability; exhaustive global search proof"
        ]

        errors = _validate(workunit)

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safe" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))
        self.assertTrue(any("exhaustive global search" in error for error in errors))

    def test_private_path_credential_api_key_fixture_fails(self) -> None:
        workunit = _workunit()
        workunit["api_key"] = "not-real"
        workunit["notes"] = ["C:\\Users\\example\\work-unit"]

        errors = _validate(workunit)

        self.assertTrue(any("sensitive key" in error for error in errors))
        self.assertTrue(any("private/local user path" in error for error in errors))

    def test_policy_inventories_validate(self) -> None:
        self.assertEqual(validate_workunit_type_registry(_read_json(REPO_ROOT / TYPE_REGISTRY_PATH), TYPE_REGISTRY_PATH), [])
        self.assertEqual(validate_workunit_policy(_read_json(REPO_ROOT / WORKUNIT_POLICY_PATH), WORKUNIT_POLICY_PATH), [])
        self.assertEqual(validate_workunit_idempotency_policy(_read_json(REPO_ROOT / IDEMPOTENCY_POLICY_PATH), IDEMPOTENCY_POLICY_PATH), [])
        self.assertEqual(validate_workunit_action_policy(_read_json(REPO_ROOT / ACTION_POLICY_PATH), ACTION_POLICY_PATH), [])
        self.assertEqual(validate_workunit_input_output_policy(_read_json(REPO_ROOT / INPUT_OUTPUT_POLICY_PATH), INPUT_OUTPUT_POLICY_PATH), [])
        self.assertEqual(validate_workunit_review_gate_policy(_read_json(REPO_ROOT / REVIEW_GATE_POLICY_PATH), REVIEW_GATE_POLICY_PATH), [])

    def test_validator_does_not_create_local_state(self) -> None:
        before = _example_tree()

        report = validate_eureka_workunit(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _example_tree())

    def test_validator_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            report = validate_eureka_workunit(REPO_ROOT)

        self.assertEqual(report["status"], "valid")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _example_paths() -> list[Path]:
    return sorted((REPO_ROOT / "examples/work_units").glob("*/work_unit.json"))


def _workunit() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/work_units/search_need_review_v0/work_unit.json"))


def _future_network_workunit() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/work_units/approved_metadata_probe_future_v0/work_unit.json"))


def _modes() -> set[str]:
    payload = _read_json(REPO_ROOT / NODE_MODE_REGISTRY_PATH)
    return {record["mode_id"] for record in payload["modes"]}


def _capabilities() -> tuple[set[str], dict[str, str]]:
    matrix = _read_json(REPO_ROOT / NODE_CAPABILITY_MATRIX_PATH)
    registry = _read_json(REPO_ROOT / NODE_CAPABILITY_REGISTRY_PATH)
    statuses = {record["capability_id"]: record["capability_status"] for record in matrix["capabilities"]}
    capability_ids = set(statuses) | {record["capability_id"] for record in registry["capabilities"]}
    return capability_ids, statuses


def _validate(workunit: dict) -> list[str]:
    capability_ids, capability_statuses = _capabilities()
    return validate_workunit_record(
        workunit,
        "broken",
        repo_root=REPO_ROOT,
        mode_ids=_modes(),
        capability_ids=capability_ids,
        capability_statuses=capability_statuses,
    )


def _example_tree() -> list[str]:
    root = REPO_ROOT / "examples/work_units"
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


if __name__ == "__main__":
    unittest.main()
