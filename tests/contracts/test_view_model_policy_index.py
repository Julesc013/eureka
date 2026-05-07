from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_view_model_policy_index import (
    EXAMPLE_INDEX_PATH,
    POLICY_INDEX_PATH,
    REPRESENTATION_INVENTORY,
    ROUTE_MATRIX_INVENTORY,
    SEMANTIC_PARITY_INVENTORY,
    validate_payloads,
    validate_view_model_policy_index,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict, dict, dict]:
    return (
        load_json(POLICY_INDEX_PATH),
        load_json(EXAMPLE_INDEX_PATH),
        load_json(REPRESENTATION_INVENTORY),
        load_json(SEMANTIC_PARITY_INVENTORY),
        load_json(ROUTE_MATRIX_INVENTORY),
    )


def validate_index(index: dict, representations: dict, semantic: dict, route_matrix: dict) -> list[str]:
    return validate_payloads(
        index,
        representations,
        semantic,
        route_matrix,
        REPO_ROOT,
        source_label="unit",
        require_full=True,
    )


class ViewModelPolicyIndexContractsTest(unittest.TestCase):
    def test_valid_view_model_policy_index_passes(self) -> None:
        report = validate_view_model_policy_index(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["view_model_family_count"], 12)

    def test_missing_schema_path_fails(self) -> None:
        index, _example, representations, semantic, route_matrix = load_payloads()
        index = copy.deepcopy(index)
        index["view_model_families"][0]["schema_path"] = "contracts/views/missing_schema.json"

        errors = validate_index(index, representations, semantic, route_matrix)

        self.assertTrue(any("schema_path" in error and "missing_schema" in error for error in errors))

    def test_missing_policy_path_fails(self) -> None:
        index, _example, representations, semantic, route_matrix = load_payloads()
        index = copy.deepcopy(index)
        index["view_model_families"][0]["policy_inventory_path"] = "control/inventory/publication/missing_policy.json"

        errors = validate_index(index, representations, semantic, route_matrix)

        self.assertTrue(any("policy_inventory_path" in error and "missing_policy" in error for error in errors))

    def test_missing_documentation_path_fails(self) -> None:
        index, _example, representations, semantic, route_matrix = load_payloads()
        index = copy.deepcopy(index)
        index["view_model_families"][0]["documentation_path"] = "docs/reference/MISSING_CONTRACT.md"

        errors = validate_index(index, representations, semantic, route_matrix)

        self.assertTrue(any("documentation_path" in error and "MISSING_CONTRACT" in error for error in errors))

    def test_missing_validator_path_fails(self) -> None:
        index, _example, representations, semantic, route_matrix = load_payloads()
        index = copy.deepcopy(index)
        index["view_model_families"][0]["validator_path"] = "scripts/missing_validator.py"

        errors = validate_index(index, representations, semantic, route_matrix)

        self.assertTrue(any("validator_path" in error and "missing_validator" in error for error in errors))

    def test_missing_representation_profile_reference_fails(self) -> None:
        index, _example, representations, semantic, route_matrix = load_payloads()
        index = copy.deepcopy(index)
        index["view_model_families"][0]["allowed_representation_profiles"].append("missing_profile")

        errors = validate_index(index, representations, semantic, route_matrix)

        self.assertTrue(any("missing_profile" in error for error in errors))

    def test_missing_semantic_parity_policy_reference_fails(self) -> None:
        index, _example, representations, semantic, route_matrix = load_payloads()
        index = copy.deepcopy(index)
        index["view_model_families"][0]["semantic_parity_policy_ids"] = ["missing_parity_policy"]

        errors = validate_index(index, representations, semantic, route_matrix)

        self.assertTrue(any("missing_parity_policy" in error for error in errors))

    def test_duplicate_view_family_fails(self) -> None:
        index, _example, representations, semantic, route_matrix = load_payloads()
        index = copy.deepcopy(index)
        index["view_model_families"][1]["view_family"] = index["view_model_families"][0]["view_family"]

        errors = validate_index(index, representations, semantic, route_matrix)

        self.assertTrue(any("duplicate view families" in error for error in errors))

    def test_product_boundary_true_claim_fails(self) -> None:
        index, _example, representations, semantic, route_matrix = load_payloads()
        index = copy.deepcopy(index)
        index["product_boundary"]["enabled_downloads"] = True

        errors = validate_index(index, representations, semantic, route_matrix)

        self.assertTrue(any("product_boundary.enabled_downloads" in error for error in errors))

    def test_example_index_validates(self) -> None:
        _index, example, representations, semantic, route_matrix = load_payloads()

        errors = validate_payloads(
            example,
            representations,
            semantic,
            route_matrix,
            REPO_ROOT,
            source_label="example_unit",
            require_full=False,
        )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
