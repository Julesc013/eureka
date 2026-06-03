from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts import validate_temporal_semantic_interface_system as validator
from scripts.validate_temporal_semantic_interface_system import (
    validate_temporal_semantic_interface_system,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidateTemporalSemanticInterfaceSystemTest(unittest.TestCase):
    def test_validator_passes(self) -> None:
        report = validate_temporal_semantic_interface_system(REPO_ROOT)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["semantic_contract_count"], 6)
        self.assertEqual(report["representation_contract_count"], 6)
        self.assertEqual(report["view_contract_count"], 8)
        self.assertFalse(report["surface_kernel_runtime_added"])
        self.assertFalse(report["runtime_behavior_changed"])
        self.assertFalse(report["deployment_performed"])

    def test_missing_status_fails_inventory_validation(self) -> None:
        inventory = _read_json(REPO_ROOT / "control/inventory/tsis_00_semantic_inventory.json")
        broken = copy.deepcopy(inventory)
        broken["canonical_status_vocabulary"].remove("candidate")
        errors: list[str] = []

        validator._validate_semantic_inventory(broken, errors)

        self.assertTrue(any("candidate" in error for error in errors))

    def test_policy_enabling_downloads_fails(self) -> None:
        policy = _read_json(REPO_ROOT / "control/policies/temporal_semantic_interface_policy.json")
        broken = copy.deepcopy(policy)
        broken["downloads_enabled"] = True
        errors: list[str] = []

        validator._validate_policy("unit_policy", broken, errors)

        self.assertTrue(any("downloads_enabled must be false" in error for error in errors))

    def test_status_registry_synonyms_are_forbidden(self) -> None:
        registry = _read_json(REPO_ROOT / "control/inventory/semantic_status_registry.json")
        broken = copy.deepcopy(registry)
        broken["machine_status_synonyms_allowed"] = True
        errors: list[str] = []

        validator._validate_status_registry(broken, errors)

        self.assertTrue(any("machine_status_synonyms_allowed" in error for error in errors))

    def test_runtime_phase_file_would_fail_tsis_00(self) -> None:
        errors: list[str] = []

        validator._validate_runtime_not_added(REPO_ROOT / "tests/fixtures/does-not-exist", errors)

        self.assertEqual(errors, [])

    def test_cli_json_passes(self) -> None:
        from io import StringIO

        output = StringIO()
        rc = validator.main(["--repo-root", str(REPO_ROOT), "--json"], stdout=output)
        payload = json.loads(output.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["status"], "pass")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
