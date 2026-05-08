from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from scripts.validate_eureka_node_policy import (
    ACTION_POLICY_PATH,
    OUTPUT_POLICY_PATH,
    POLICY_REGISTRY_PATH,
    REVIEW_GATE_POLICY_PATH,
    SOURCE_ACCESS_POLICY_PATH,
    validate_action_policy,
    validate_eureka_node_policy,
    validate_node_policy_record,
    validate_output_policy,
    validate_policy_registry,
    validate_review_gate_policy,
    validate_source_access_registry,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class EurekaNodePolicyContractTest(unittest.TestCase):
    def test_valid_node_policy_examples_pass(self) -> None:
        for path in _example_paths():
            with self.subTest(path=path):
                self.assertEqual(validate_node_policy_record(_read_json(path), path.relative_to(REPO_ROOT).as_posix()), [])

    def test_current_repo_node_policy_pack_validates(self) -> None:
        report = validate_eureka_node_policy(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_invalid_policy_status_fails(self) -> None:
        policy = _policy()
        policy["policy_status"] = "active_runtime"

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("policy_status" in error for error in errors))

    def test_unknown_action_fails(self) -> None:
        policy = _policy()
        policy["allowed_actions"].append("perform_unbounded_runtime_magic")

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("allowed_actions unknown" in error for error in errors))

    def test_unknown_source_access_mode_fails(self) -> None:
        policy = _policy()
        policy["source_access_policy"]["allowed_mode"] = "arbitrary_url_fetch"

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("allowed_mode" in error for error in errors))

    def test_current_policy_enabling_network_fails(self) -> None:
        policy = _policy()
        policy["network_policy"]["network_enabled"] = True

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("network_enabled" in error for error in errors))

    def test_current_policy_enabling_local_state_fails(self) -> None:
        policy = _policy()
        policy["local_state_policy"]["local_state_enabled"] = True

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("local_state_enabled" in error for error in errors))

    def test_current_policy_enabling_live_probes_fails(self) -> None:
        policy = _policy()
        policy["product_boundary"]["enabled_live_probes"] = True

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("enabled_live_probes" in error for error in errors))

    def test_current_policy_allowing_master_index_mutation_fails(self) -> None:
        policy = _policy()
        policy["allowed_outputs"]["outputs_may_mutate_master_index"] = True

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("outputs_may_mutate_master_index" in error for error in errors))

    def test_current_policy_allowing_evidence_truth_fails(self) -> None:
        policy = _policy()
        policy["evidence_policy"]["evidence_truth_allowed"] = True

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("evidence_truth_allowed" in error for error in errors))

    def test_current_policy_allowing_candidate_truth_fails(self) -> None:
        policy = _policy()
        policy["candidate_policy"]["candidate_truth_allowed"] = True

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("candidate_truth_allowed" in error for error in errors))

    def test_current_policy_allowing_automatic_pack_acceptance_fails(self) -> None:
        policy = _policy()
        policy["pack_policy"]["automatic_acceptance_allowed"] = True

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("automatic_acceptance_allowed" in error for error in errors))

    def test_missing_forbidden_action_list_fails(self) -> None:
        policy = _policy()
        policy["forbidden_actions"] = []

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("forbidden_actions missing mutate_master_index" in error for error in errors))

    def test_missing_review_gate_fails(self) -> None:
        policy = _policy()
        policy["review_gate_policy"].pop("human_review_required")

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("human_review_required" in error for error in errors))

    def test_rights_malware_installability_exhaustive_claim_fails(self) -> None:
        policy = _policy()
        policy["notes"] = [
            "rights clearance confirmed; malware safe; verified installability; exhaustive global search proof"
        ]

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safe" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))
        self.assertTrue(any("exhaustive global search" in error for error in errors))

    def test_private_path_credential_api_key_fixture_fails(self) -> None:
        policy = _policy()
        policy["api_key"] = "not-real"
        policy["notes"] = ["C:\\Users\\example\\node-policy"]

        errors = validate_node_policy_record(policy, "broken")

        self.assertTrue(any("sensitive key" in error for error in errors))
        self.assertTrue(any("private/local user path" in error for error in errors))

    def test_policy_registries_validate(self) -> None:
        self.assertEqual(validate_policy_registry(_read_json(REPO_ROOT / POLICY_REGISTRY_PATH), POLICY_REGISTRY_PATH), [])
        self.assertEqual(validate_action_policy(_read_json(REPO_ROOT / ACTION_POLICY_PATH), ACTION_POLICY_PATH), [])
        self.assertEqual(validate_source_access_registry(_read_json(REPO_ROOT / SOURCE_ACCESS_POLICY_PATH), SOURCE_ACCESS_POLICY_PATH), [])
        self.assertEqual(validate_output_policy(_read_json(REPO_ROOT / OUTPUT_POLICY_PATH), OUTPUT_POLICY_PATH), [])
        self.assertEqual(validate_review_gate_policy(_read_json(REPO_ROOT / REVIEW_GATE_POLICY_PATH), REVIEW_GATE_POLICY_PATH), [])

    def test_validator_does_not_create_local_state(self) -> None:
        before = _example_tree()

        report = validate_eureka_node_policy(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _example_tree())

    def test_validator_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            report = validate_eureka_node_policy(REPO_ROOT)

        self.assertEqual(report["status"], "valid")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _example_paths() -> list[Path]:
    return sorted((REPO_ROOT / "examples/nodes/policies").glob("*.json"))


def _policy() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/nodes/policies/local_private_node_policy_v0.json"))


def _example_tree() -> list[str]:
    root = REPO_ROOT / "examples/nodes"
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


if __name__ == "__main__":
    unittest.main()
