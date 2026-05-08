from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from scripts.validate_eureka_node_manifest import (
    CAPABILITY_REGISTRY_PATH,
    MODE_REGISTRY_PATH,
    POLICY_PATH,
    validate_capability_registry,
    validate_eureka_node_manifests,
    validate_mode_registry,
    validate_node_manifest,
    validate_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class EurekaNodeManifestContractTest(unittest.TestCase):
    def test_valid_node_examples_pass(self) -> None:
        for path in sorted((REPO_ROOT / "examples/nodes").glob("*/eureka_node_manifest.json")):
            with self.subTest(path=path):
                errors = validate_node_manifest(
                    _read_json(path),
                    path.relative_to(REPO_ROOT).as_posix(),
                    _policy(),
                    _mode_registry(),
                    _capability_registry(),
                )
                self.assertEqual(errors, [])

    def test_current_repo_node_manifest_pack_validates(self) -> None:
        report = validate_eureka_node_manifests(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_invalid_node_mode_fails(self) -> None:
        manifest = _manifest()
        manifest["node_mode"] = "floating_public_truth_node"

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("node_mode" in error for error in errors))

    def test_invalid_node_status_fails(self) -> None:
        manifest = _manifest()
        manifest["node_status"] = "active_runtime"

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("node_status" in error for error in errors))

    def test_unknown_capability_fails(self) -> None:
        manifest = _manifest()
        manifest["node_capabilities"].append(
            {"capability_id": "unreviewed_magic_runtime", "capability_status": "current_contract_allowed"}
        )

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("unknown capability" in error for error in errors))

    def test_current_manifest_enabling_network_fails(self) -> None:
        manifest = _manifest()
        manifest["network_access"]["enabled"] = True

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("network_access.enabled" in error for error in errors))

    def test_current_manifest_enabling_live_probes_fails(self) -> None:
        manifest = _manifest()
        manifest["product_boundary"]["enabled_live_probes"] = True

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("enabled_live_probes" in error for error in errors))

    def test_current_manifest_allowing_master_index_mutation_fails(self) -> None:
        manifest = _manifest()
        manifest["allowed_outputs"]["can_mutate_master_index"] = True

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("can_mutate_master_index" in error for error in errors))

    def test_current_manifest_allowing_automatic_pack_acceptance_fails(self) -> None:
        manifest = _manifest()
        manifest["pack_policy"]["automatic_acceptance_allowed"] = True

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("automatic_acceptance_allowed" in error for error in errors))

    def test_missing_forbidden_action_fails(self) -> None:
        manifest = _manifest()
        manifest["forbidden_actions"].remove("mutate_master_index")

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("forbidden_actions missing mutate_master_index" in error for error in errors))

    def test_rights_malware_installability_claim_fails(self) -> None:
        manifest = _manifest()
        manifest["notes"] = ["rights clearance confirmed; malware safe; verified installability"]

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safe" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))

    def test_production_readiness_claim_fails(self) -> None:
        manifest = _manifest()
        manifest["notes"] = ["production ready node"]

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("production ready" in error for error in errors))

    def test_private_path_credential_api_key_fixture_fails(self) -> None:
        manifest = _manifest()
        manifest["node_limits"]["api_key"] = "not-real"
        manifest["notes"] = ["C:\\Users\\example\\private-node"]

        errors = validate_node_manifest(manifest, "broken")

        self.assertTrue(any("sensitive key" in error for error in errors))
        self.assertTrue(any("private/local user path" in error for error in errors))

    def test_policy_inventories_validate(self) -> None:
        policy = _policy()
        mode_registry = _mode_registry()
        capability_registry = _capability_registry()

        self.assertEqual(validate_policy(policy, POLICY_PATH), [])
        self.assertEqual(validate_mode_registry(mode_registry, MODE_REGISTRY_PATH, policy), [])
        self.assertEqual(validate_capability_registry(capability_registry, CAPABILITY_REGISTRY_PATH, policy), [])

    def test_validator_does_not_create_local_state(self) -> None:
        before = _example_tree()

        report = validate_eureka_node_manifests(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _example_tree())

    def test_validator_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            report = validate_eureka_node_manifests(REPO_ROOT)

        self.assertEqual(report["status"], "valid")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/nodes/local_private_node_v0/eureka_node_manifest.json"))


def _policy() -> dict:
    return _read_json(REPO_ROOT / POLICY_PATH)


def _mode_registry() -> dict:
    return _read_json(REPO_ROOT / MODE_REGISTRY_PATH)


def _capability_registry() -> dict:
    return _read_json(REPO_ROOT / CAPABILITY_REGISTRY_PATH)


def _example_tree() -> list[str]:
    root = REPO_ROOT / "examples/nodes"
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))


if __name__ == "__main__":
    unittest.main()
