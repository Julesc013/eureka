from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_object_page_view_model import (
    EXAMPLE_PATHS,
    validate_object_page_view_model,
    validate_payloads,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict, dict, list[dict]]:
    return (
        load_json(PUBLICATION_DIR / "object_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        load_json(PUBLICATION_DIR / "semantic_renderer_parity_policy.json"),
        load_json(PUBLICATION_DIR / "route_view_representation_matrix.json"),
        [load_json(REPO_ROOT / relative) for relative in EXAMPLE_PATHS],
    )


class ObjectPageViewModelContractsTest(unittest.TestCase):
    def test_valid_examples_pass(self) -> None:
        report = validate_object_page_view_model(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["example_count"], 4)

    def test_missing_canonical_object_identity_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["object_identity"]["object_id"] = ""

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("canonical object identity object_id" in error for error in errors))

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
        candidate = next(
            example
            for example in examples
            if example["view_model_id"] == "candidate_object_page_v0"
        )
        candidate["candidate_review_state"]["review_status"] = "verified"

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("candidate/provisional object" in error for error in errors))

    def test_source_observation_marked_accepted_truth_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["source_summary"]["source_observation_accepted_as_truth"] = True

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("source observation" in error for error in errors))

    def test_evidence_candidate_marked_accepted_truth_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["evidence_summary"]["evidence_candidate_accepted_as_truth"] = True

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("evidence candidate" in error for error in errors))

    def test_member_object_without_parent_lineage_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        member = next(
            example for example in examples if example["view_model_id"] == "member_object_page_v0"
        )
        member["file_and_member_summary"]["parent_object_ref"] = None
        member["file_and_member_summary"]["containment_path"] = []
        member["provenance_summary"]["parent_lineage_visible"] = False

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("parent_object_ref" in error for error in errors))
        self.assertTrue(any("containment_path" in error for error in errors))
        self.assertTrue(any("parent lineage" in error for error in errors))

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

    def test_rights_malware_installability_claim_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["rights_summary"]["rights_clearance_claimed"] = True
        examples[0]["risk_summary"]["malware_safety_claimed"] = True
        examples[0]["compatibility_summary"]["verified_installability_claimed"] = True

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safety" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))

    def test_missing_blocked_action_for_unavailable_capability_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["blocked_actions"] = [
            action
            for action in examples[0]["blocked_actions"]
            if action["action_id"] != "download_unavailable"
        ]

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("download_unavailable" in error for error in errors))

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
