from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_semantic_renderer_parity import (
    EXAMPLE_PATHS,
    validate_payloads,
    validate_semantic_renderer_parity,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, list[dict]]:
    return (
        load_json(PUBLICATION_DIR / "semantic_renderer_parity_policy.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        [load_json(REPO_ROOT / relative) for relative in EXAMPLE_PATHS],
    )


class SemanticRendererParityContractsTest(unittest.TestCase):
    def test_valid_inventory_passes(self) -> None:
        report = validate_semantic_renderer_parity(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertGreaterEqual(report["policy_count"], 11)
        self.assertEqual(report["example_count"], 3)

    def test_missing_representation_profile_reference_fails(self) -> None:
        policy_inventory, representation_inventory, examples = load_payloads()
        policy_inventory = copy.deepcopy(policy_inventory)
        policy_inventory["policies"][0]["allowed_representation_profiles"].append(
            "missing_profile"
        )

        errors = validate_payloads(
            policy_inventory,
            representation_inventory,
            examples,
            source_label="unit",
            require_required_view_families=True,
        )

        self.assertTrue(any("missing_profile" in error for error in errors))

    def test_missing_required_semantic_fields_fails(self) -> None:
        policy_inventory, representation_inventory, examples = load_payloads()
        policy_inventory = copy.deepcopy(policy_inventory)
        policy_inventory["policies"][0]["required_semantic_fields"] = []

        errors = validate_payloads(
            policy_inventory,
            representation_inventory,
            examples,
            source_label="unit",
            require_required_view_families=True,
        )

        self.assertTrue(any("required_semantic_fields" in error for error in errors))

    def test_missing_forbidden_omissions_fails(self) -> None:
        policy_inventory, representation_inventory, examples = load_payloads()
        policy_inventory = copy.deepcopy(policy_inventory)
        policy_inventory["policies"][0]["forbidden_omissions"] = []

        errors = validate_payloads(
            policy_inventory,
            representation_inventory,
            examples,
            source_label="unit",
            require_required_view_families=True,
        )

        self.assertTrue(any("forbidden_omissions" in error for error in errors))

    def test_duplicate_policy_ids_fail(self) -> None:
        policy_inventory, representation_inventory, examples = load_payloads()
        policy_inventory = copy.deepcopy(policy_inventory)
        policy_inventory["policies"][1]["parity_policy_id"] = policy_inventory["policies"][0][
            "parity_policy_id"
        ]

        errors = validate_payloads(
            policy_inventory,
            representation_inventory,
            examples,
            source_label="unit",
            require_required_view_families=True,
        )

        self.assertTrue(any("duplicate parity_policy_id" in error for error in errors))

    def test_example_files_validate(self) -> None:
        policy_inventory, representation_inventory, examples = load_payloads()

        errors = validate_payloads(
            policy_inventory,
            representation_inventory,
            examples,
            source_label="unit",
            require_required_view_families=True,
        )

        self.assertEqual(errors, [])

    def test_policy_that_implies_forbidden_behavior_fails(self) -> None:
        policy_inventory, representation_inventory, examples = load_payloads()
        policy_inventory = copy.deepcopy(policy_inventory)
        policy = policy_inventory["policies"][0]
        policy["no_hosting_enabled"] = False
        policy["no_live_probes_enabled"] = False
        policy["no_downloads_enabled"] = False

        errors = validate_payloads(
            policy_inventory,
            representation_inventory,
            examples,
            source_label="unit",
            require_required_view_families=True,
        )

        self.assertTrue(any("no_hosting_enabled must be true" in error for error in errors))
        self.assertTrue(any("no_live_probes_enabled must be true" in error for error in errors))
        self.assertTrue(any("no_downloads_enabled must be true" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
