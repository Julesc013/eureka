from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_search_page_view_model import (
    EXAMPLE_PATHS,
    validate_payloads,
    validate_search_page_view_model,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict, dict, list[dict]]:
    return (
        load_json(PUBLICATION_DIR / "search_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        load_json(PUBLICATION_DIR / "semantic_renderer_parity_policy.json"),
        load_json(PUBLICATION_DIR / "route_view_representation_matrix.json"),
        [load_json(REPO_ROOT / relative) for relative in EXAMPLE_PATHS],
    )


class SearchPageViewModelContractsTest(unittest.TestCase):
    def test_valid_examples_pass(self) -> None:
        report = validate_search_page_view_model(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["example_count"], 4)

    def test_missing_required_semantic_field_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["semantic_requirements"] = []

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("semantic_requirements" in error for error in errors))

    def test_invalid_search_mode_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["search_mode"] = "live_web_now"

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("search_mode" in error and "live_web_now" in error for error in errors))

    def test_invalid_representation_profile_reference_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        policy = copy.deepcopy(policy)
        policy["allowed_representation_profiles"].append("missing_profile")

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("missing_profile" in error for error in errors))

    def test_invalid_semantic_parity_policy_reference_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        policy = copy.deepcopy(policy)
        policy["required_semantic_parity_policy"] = "missing_parity_policy"

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("missing_parity_policy" in error for error in errors))

    def test_candidate_marked_as_verified_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        result_example = next(
            example
            for example in examples
            if example["view_model_id"] == "result_card_search_page_v0"
        )
        result_example["results"][0]["result_state"] = "verified"

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("candidate/provisional record" in error for error in errors))

    def test_absence_claiming_exhaustive_global_search_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        absence_example = next(
            example for example in examples if example["view_model_id"] == "absence_search_page_v0"
        )
        absence_example["absence"]["exhaustive_global_search"] = True

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("exhaustive global search" in error for error in errors))

    def test_current_example_claiming_runtime_capability_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["public_runtime_posture"]["hosted_backend_claimed"] = True
        examples[0]["public_runtime_posture"]["live_probes_enabled"] = True
        examples[0]["public_runtime_posture"]["downloads_enabled"] = True
        examples[0]["public_runtime_posture"]["uploads_enabled"] = True
        examples[0]["public_runtime_posture"]["accounts_enabled"] = True
        examples[0]["public_runtime_posture"]["telemetry_enabled"] = True

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("hosted_backend_claimed must be false" in error for error in errors))
        self.assertTrue(any("live_probes_enabled must be false" in error for error in errors))
        self.assertTrue(any("downloads_enabled must be false" in error for error in errors))
        self.assertTrue(any("uploads_enabled must be false" in error for error in errors))
        self.assertTrue(any("accounts_enabled must be false" in error for error in errors))
        self.assertTrue(any("telemetry_enabled must be false" in error for error in errors))

    def test_missing_blocked_action_for_unavailable_capability_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["blocked_actions"] = [
            action
            for action in examples[0]["blocked_actions"]
            if action["action_id"] != "hosted_backend_unavailable"
        ]

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("hosted_backend_unavailable" in error for error in errors))

    def test_policy_inventory_validates(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
