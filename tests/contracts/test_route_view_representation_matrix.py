from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_route_view_representation_matrix import (
    EXAMPLE_PATHS,
    validate_payloads,
    validate_route_view_representation_matrix,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict, dict, list[dict]]:
    return (
        load_json(PUBLICATION_DIR / "route_view_representation_matrix.json"),
        load_json(PUBLICATION_DIR / "host_profiles.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        load_json(PUBLICATION_DIR / "semantic_renderer_parity_policy.json"),
        [load_json(REPO_ROOT / relative) for relative in EXAMPLE_PATHS],
    )


class RouteViewRepresentationMatrixContractsTest(unittest.TestCase):
    def test_valid_inventory_passes(self) -> None:
        report = validate_route_view_representation_matrix(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertGreaterEqual(report["route_family_count"], 25)
        self.assertGreaterEqual(report["view_family_count"], 25)

    def test_broken_representation_profile_reference_fails(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        matrix["route_families"][0]["allowed_representation_profiles"].append(
            "missing_profile"
        )
        matrix["representation_bindings"][0]["allowed_representation_profiles"].append(
            "missing_profile"
        )

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("missing_profile" in error for error in errors))

    def test_broken_host_profile_reference_fails(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        matrix["route_families"][0]["allowed_host_profiles"].append("missing_host")
        matrix["host_profile_bindings"][0]["allowed_host_profiles"].append("missing_host")

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("missing_host" in error for error in errors))

    def test_broken_semantic_parity_policy_reference_fails(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        matrix["route_families"][0]["required_semantic_parity_policy"] = "missing_policy"
        matrix["semantic_parity_policy_bindings"][0]["parity_policy_id"] = "missing_policy"

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("missing_policy" in error for error in errors))

    def test_duplicate_route_family_ids_fail(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        matrix["route_families"][1]["route_family_id"] = matrix["route_families"][0][
            "route_family_id"
        ]

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("duplicate route_family_id" in error for error in errors))

    def test_invalid_route_status_fails(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        matrix["route_families"][0]["route_status"] = "live_now"

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("route_status 'live_now' is invalid" in error for error in errors))

    def test_legacy_host_exposing_write_account_admin_route_fails(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        matrix["route_families"][0]["route_safety_class"] = "account_write_admin"

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("legacy/read-only hosts" in error for error in errors))

    def test_static_files_host_exposing_dynamic_search_runtime_fails(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        route = next(route for route in matrix["route_families"] if route["route_family_id"] == "api_search")
        route["allowed_host_profiles"].append("files_static")
        binding = next(
            binding
            for binding in matrix["host_profile_bindings"]
            if binding["route_family_id"] == "api_search"
        )
        binding["allowed_host_profiles"].append("files_static")

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("static files host" in error for error in errors))

    def test_forbidden_route_split_fails(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        matrix["route_families"][1]["canonical_path_pattern"] = "/old/search"

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("forbidden route split" in error for error in errors))

    def test_future_route_claiming_active_hosted_runtime_fails(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()
        matrix = copy.deepcopy(matrix)
        route = next(
            route
            for route in matrix["route_families"]
            if route["route_family_id"] == "object_page_future"
        )
        route["implemented_now"] = True
        route["hosted_runtime_active"] = True

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertTrue(any("future/deferred route" in error for error in errors))
        self.assertTrue(any("hosted_runtime_active must be false" in error for error in errors))

    def test_example_files_validate(self) -> None:
        matrix, hosts, representations, semantic, examples = load_payloads()

        errors = validate_payloads(
            matrix,
            hosts,
            representations,
            semantic,
            examples,
            source_label="unit",
            require_required_route_families=True,
        )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
