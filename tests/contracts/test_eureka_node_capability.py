from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from scripts.validate_eureka_node_capability import (
    CAPABILITY_MATRIX_PATH,
    CAPABILITY_POLICY_PATH,
    DEPENDENCY_POLICY_PATH,
    NODE_CAPABILITY_REGISTRY_PATH,
    NODE_MODE_REGISTRY_PATH,
    SIDE_EFFECT_POLICY_PATH,
    validate_capability_matrix,
    validate_capability_policy,
    validate_dependency_policy,
    validate_eureka_node_capability,
    validate_manifest_capability_refs,
    validate_node_capability_record,
    validate_side_effect_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class EurekaNodeCapabilityContractTest(unittest.TestCase):
    def test_valid_capability_examples_pass(self) -> None:
        matrix_ids = _matrix_ids()
        for path in _example_paths():
            with self.subTest(path=path):
                self.assertEqual(
                    validate_node_capability_record(
                        _read_json(path),
                        path.relative_to(REPO_ROOT).as_posix(),
                        matrix_ids=matrix_ids,
                    ),
                    [],
                )

    def test_current_repo_capability_pack_validates(self) -> None:
        report = validate_eureka_node_capability(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_invalid_capability_status_fails(self) -> None:
        capability = _capability()
        capability["capability_status"] = "active_runtime"

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("capability_status" in error for error in errors))

    def test_invalid_capability_family_fails(self) -> None:
        capability = _capability()
        capability["capability_family"] = "truth_mutation"

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("capability_family" in error for error in errors))

    def test_invalid_side_effect_class_fails(self) -> None:
        capability = _capability()
        capability["side_effect_class"] = "mutate_everything"

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("side_effect_class" in error for error in errors))

    def test_current_capability_requiring_network_fails(self) -> None:
        capability = _capability()
        capability["network_requirement"]["network_required"] = True

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("network_requirement" in error or "current capability" in error for error in errors))

    def test_current_capability_requiring_model_provider_fails(self) -> None:
        capability = _capability()
        capability["model_provider_requirement"]["model_provider_required"] = True

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("model_provider_requirement" in error or "current capability" in error for error in errors))

    def test_current_capability_requiring_credentials_fails(self) -> None:
        capability = _capability()
        capability["credential_requirement"]["credentials_required"] = True

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("credential_requirement" in error or "current capability" in error for error in errors))

    def test_current_capability_requiring_local_state_fails(self) -> None:
        capability = _capability()
        capability["local_state_requirement"]["local_state_required"] = True

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("local_state_requirement" in error or "current capability" in error for error in errors))

    def test_future_network_capability_without_approval_gate_fails(self) -> None:
        capability = _future_network_capability()
        capability["network_requirement"]["operator_approval_required"] = False
        capability["required_review_gates"].remove("operator_approval_required_for_network")

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("operator_approval" in error for error in errors))

    def test_unknown_node_mode_reference_fails(self) -> None:
        capability = _capability()
        capability["allowed_node_modes"].append("portable_truth_engine")

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("allowed_node_modes unknown" in error for error in errors))

    def test_unknown_capability_referenced_by_node_manifest_fails(self) -> None:
        known = _matrix_ids()
        known.remove("repo_local_inspection")

        errors = validate_manifest_capability_refs(REPO_ROOT, known)

        self.assertTrue(any("repo_local_inspection" in error for error in errors))

    def test_missing_forbidden_inputs_fails(self) -> None:
        capability = _capability()
        capability["input_categories"]["forbidden"] = []

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("input_categories.forbidden missing" in error for error in errors))

    def test_missing_forbidden_outputs_fails(self) -> None:
        capability = _capability()
        capability["output_categories"]["forbidden"] = []

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("output_categories.forbidden missing" in error for error in errors))

    def test_truth_boundary_true_claim_fails(self) -> None:
        capability = _capability()
        capability["truth_boundary"]["can_mutate_master_index"] = True

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("can_mutate_master_index" in error for error in errors))

    def test_rights_malware_installability_exhaustive_claim_fails(self) -> None:
        capability = _capability()
        capability["notes"] = [
            "rights clearance confirmed; malware safe; verified installability; exhaustive global search proof"
        ]

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safe" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))
        self.assertTrue(any("exhaustive global search" in error for error in errors))

    def test_private_path_credential_api_key_fixture_fails(self) -> None:
        capability = _capability()
        capability["api_key"] = "not-real"
        capability["notes"] = ["C:\\Users\\example\\node-capability"]

        errors = validate_node_capability_record(capability, "broken")

        self.assertTrue(any("sensitive key" in error for error in errors))
        self.assertTrue(any("private/local user path" in error for error in errors))

    def test_policy_inventories_validate(self) -> None:
        self.assertEqual(validate_capability_policy(_read_json(REPO_ROOT / CAPABILITY_POLICY_PATH), CAPABILITY_POLICY_PATH), [])
        self.assertEqual(validate_dependency_policy(_read_json(REPO_ROOT / DEPENDENCY_POLICY_PATH), DEPENDENCY_POLICY_PATH), [])
        self.assertEqual(validate_side_effect_policy(_read_json(REPO_ROOT / SIDE_EFFECT_POLICY_PATH), SIDE_EFFECT_POLICY_PATH), [])

    def test_capability_matrix_validates(self) -> None:
        errors, matrix_ids = validate_capability_matrix(
            _read_json(REPO_ROOT / CAPABILITY_MATRIX_PATH),
            CAPABILITY_MATRIX_PATH,
            _read_json(REPO_ROOT / NODE_CAPABILITY_REGISTRY_PATH),
            _read_json(REPO_ROOT / NODE_MODE_REGISTRY_PATH),
        )

        self.assertEqual(errors, [])
        self.assertIn("repo_local_inspection", matrix_ids)
        self.assertIn("approved_metadata_probe_future", matrix_ids)

    def test_validator_does_not_create_local_state(self) -> None:
        before = _example_tree()

        report = validate_eureka_node_capability(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _example_tree())

    def test_validator_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            report = validate_eureka_node_capability(REPO_ROOT)

        self.assertEqual(report["status"], "valid")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _example_paths() -> list[Path]:
    return sorted((REPO_ROOT / "examples/nodes/capabilities").glob("*.json"))


def _capability() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/nodes/capabilities/repo_local_inspection_capability_v0.json"))


def _future_network_capability() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/nodes/capabilities/approved_metadata_probe_future_capability_v0.json"))


def _matrix_ids() -> set[str]:
    payload = _read_json(REPO_ROOT / CAPABILITY_MATRIX_PATH)
    return {record["capability_id"] for record in payload["capabilities"]}


def _example_tree() -> list[str]:
    root = REPO_ROOT / "examples/nodes"
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


if __name__ == "__main__":
    unittest.main()
