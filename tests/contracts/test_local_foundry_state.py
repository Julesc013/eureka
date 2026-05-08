from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from scripts.validate_local_foundry_state import (
    EXPORT_POLICY_PATH,
    KIND_REGISTRY_PATH,
    PATH_POLICY_PATH,
    PRIVACY_POLICY_PATH,
    RESET_POLICY_PATH,
    STATE_POLICY_PATH,
    validate_export_policy,
    validate_kind_registry,
    validate_local_foundry_state,
    validate_local_foundry_state_record,
    validate_path_policy,
    validate_privacy_policy,
    validate_reset_policy,
    validate_state_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class LocalFoundryStateContractTest(unittest.TestCase):
    def test_valid_local_foundry_state_examples_pass(self) -> None:
        for path in _example_paths():
            with self.subTest(path=path):
                self.assertEqual(
                    validate_local_foundry_state_record(
                        _read_json(path),
                        path.relative_to(REPO_ROOT).as_posix(),
                        repo_root=REPO_ROOT,
                    ),
                    [],
                )

    def test_current_local_foundry_state_pack_validates(self) -> None:
        report = validate_local_foundry_state(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_invalid_state_status_fails(self) -> None:
        state = _state()
        state["state_status"] = "active_runtime"

        errors = _validate(state)

        self.assertTrue(any("state_status" in error for error in errors))

    def test_invalid_state_scope_fails(self) -> None:
        state = _state()
        state["state_scope"] = "cloud_shared"

        errors = _validate(state)

        self.assertTrue(any("state_scope" in error for error in errors))

    def test_invalid_state_kind_fails(self) -> None:
        state = _state()
        state["state_kinds"].append("mystery_state")

        errors = _validate(state)

        self.assertTrue(any("unknown state_kinds" in error for error in errors))

    def test_forbidden_state_kind_fails(self) -> None:
        state = _state()
        state["state_kinds"].append("master_index_record")

        errors = _validate(state)

        self.assertTrue(any("forbidden state_kinds" in error for error in errors))

    def test_current_example_creating_local_state_fails(self) -> None:
        state = _state()
        state["state_root_policy"]["state_root_created"] = True

        errors = _validate(state)

        self.assertTrue(any("state_root_created" in error for error in errors))

    def test_forbidden_path_reference_fails(self) -> None:
        state = _state()
        state["allowed_paths"] = ["contracts/private-foundry/"]

        errors = _validate(state)

        self.assertTrue(any("forbidden root" in error for error in errors))

    def test_private_path_outside_allowed_future_roots_fails(self) -> None:
        state = _state()
        state["allowed_paths"] = ["C:\\Users\\example\\foundry"]

        errors = _validate(state)

        self.assertTrue(any("private/local user path" in error for error in errors))

    def test_secret_credential_api_key_fixture_fails(self) -> None:
        state = _state()
        state["api_key"] = "not-real"

        errors = _validate(state)

        self.assertTrue(any("sensitive key" in error for error in errors))

    def test_automatic_public_export_allowed_fails(self) -> None:
        state = _state()
        state["export_policy"]["automatic_public_export_allowed"] = True

        errors = _validate(state)

        self.assertTrue(any("automatic_public_export_allowed" in error for error in errors))

    def test_automatic_master_index_import_allowed_fails(self) -> None:
        state = _state()
        state["export_policy"]["automatic_master_index_import_allowed"] = True

        errors = _validate(state)

        self.assertTrue(any("automatic_master_index_import_allowed" in error for error in errors))

    def test_local_state_marked_public_truth_fails(self) -> None:
        state = _state()
        state["truth_boundary"]["local_state_is_public_truth"] = True

        errors = _validate(state)

        self.assertTrue(any("local_state_is_public_truth" in error for error in errors))

    def test_local_state_marked_accepted_evidence_fails(self) -> None:
        state = _state()
        state["truth_boundary"]["local_state_is_accepted_evidence"] = True

        errors = _validate(state)

        self.assertTrue(any("local_state_is_accepted_evidence" in error for error in errors))

    def test_local_state_marked_master_index_fails(self) -> None:
        state = _state()
        state["truth_boundary"]["local_state_is_master_index"] = True

        errors = _validate(state)

        self.assertTrue(any("local_state_is_master_index" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        state = _state()
        state["product_boundary"]["enabled_network_access"] = True

        errors = _validate(state)

        self.assertTrue(any("enabled_network_access" in error for error in errors))

    def test_rights_malware_installability_exhaustive_claim_fails(self) -> None:
        state = _state()
        state["notes"] = [
            "rights clearance confirmed; malware safe; verified installability; exhaustive global search proof"
        ]

        errors = _validate(state)

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safe" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))
        self.assertTrue(any("exhaustive global search" in error for error in errors))

    def test_policy_inventories_validate(self) -> None:
        self.assertEqual(validate_state_policy(_read_json(REPO_ROOT / STATE_POLICY_PATH), STATE_POLICY_PATH), [])
        self.assertEqual(validate_kind_registry(_read_json(REPO_ROOT / KIND_REGISTRY_PATH), KIND_REGISTRY_PATH), [])
        self.assertEqual(validate_path_policy(_read_json(REPO_ROOT / PATH_POLICY_PATH), PATH_POLICY_PATH), [])
        self.assertEqual(validate_privacy_policy(_read_json(REPO_ROOT / PRIVACY_POLICY_PATH), PRIVACY_POLICY_PATH), [])
        self.assertEqual(validate_export_policy(_read_json(REPO_ROOT / EXPORT_POLICY_PATH), EXPORT_POLICY_PATH), [])
        self.assertEqual(validate_reset_policy(_read_json(REPO_ROOT / RESET_POLICY_PATH), RESET_POLICY_PATH), [])

    def test_validator_does_not_create_local_state(self) -> None:
        before = _repo_private_root_state()

        report = validate_local_foundry_state(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(before, _repo_private_root_state())

    def test_validator_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            report = validate_local_foundry_state(REPO_ROOT)

        self.assertEqual(report["status"], "valid")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _example_paths() -> list[Path]:
    return sorted((REPO_ROOT / "examples/local_foundry_state").glob("*.json"))


def _state(name: str = "local_private_foundry_state_v0.json") -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/local_foundry_state" / name))


def _validate(state: dict) -> list[str]:
    return validate_local_foundry_state_record(state, "broken", repo_root=REPO_ROOT)


def _repo_private_root_state() -> dict[str, bool]:
    return {
        ".aide.local": (REPO_ROOT / ".aide.local").exists(),
        ".local/eureka": (REPO_ROOT / ".local" / "eureka").exists(),
        ".cache/eureka": (REPO_ROOT / ".cache" / "eureka").exists(),
        ".tmp/eureka": (REPO_ROOT / ".tmp" / "eureka").exists(),
        ".demo-index": (REPO_ROOT / ".demo-index").exists(),
    }


if __name__ == "__main__":
    unittest.main()
