from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_source_page_view_model import (
    EXAMPLE_PATHS,
    validate_payloads,
    validate_source_page_view_model,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict, dict, list[dict]]:
    return (
        load_json(PUBLICATION_DIR / "source_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        load_json(PUBLICATION_DIR / "semantic_renderer_parity_policy.json"),
        load_json(PUBLICATION_DIR / "route_view_representation_matrix.json"),
        [load_json(REPO_ROOT / relative) for relative in EXAMPLE_PATHS],
    )


class SourcePageViewModelContractsTest(unittest.TestCase):
    def test_valid_examples_pass(self) -> None:
        report = validate_source_page_view_model(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["example_count"], 4)

    def test_missing_canonical_source_identity_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["source_identity"]["source_id"] = ""

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("canonical source identity source_id" in error for error in errors))

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

    def test_placeholder_source_marked_live_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        placeholder = next(
            example
            for example in examples
            if example["view_model_id"] == "placeholder_source_page_v0"
        )
        placeholder["connector_summary"]["connector_status"] = "live_connector"

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("placeholder/future/manual-only source" in error for error in errors))

    def test_recorded_fixture_marked_live_connector_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        recorded = next(
            example
            for example in examples
            if example["view_model_id"] == "recorded_fixture_source_page_v0"
        )
        recorded["connector_summary"]["connector_status"] = "live_connector"

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("recorded fixture source" in error for error in errors))

    def test_source_observation_marked_accepted_truth_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["source_cache_summary"]["source_observation_accepted_as_truth"] = True

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
        examples[0]["evidence_ledger_summary"]["evidence_candidate_accepted_as_truth"] = True

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("evidence candidate" in error for error in errors))

    def test_manual_observation_placeholder_marked_completed_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        gap = next(example for example in examples if example["view_model_id"] == "source_gap_page_v0")
        gap["observed_records_summary"]["manual_observation_completed"] = True
        gap["observed_records_summary"]["completed_external_baseline_claimed"] = True

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("manual observation placeholder" in error for error in errors))
        self.assertTrue(any("completed external baseline" in error for error in errors))

    def test_current_example_claiming_runtime_capability_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["connector_summary"]["hosted_backend_claimed"] = True
        examples[0]["connector_summary"]["hosted_connector_enabled"] = True
        examples[0]["connector_summary"]["live_probes_enabled"] = True
        examples[0]["connector_summary"]["source_sync_runtime_enabled"] = True
        examples[0]["connector_summary"]["downloads_enabled"] = True
        examples[0]["connector_summary"]["uploads_enabled"] = True
        examples[0]["connector_summary"]["accounts_enabled"] = True
        examples[0]["connector_summary"]["telemetry_enabled"] = True

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("hosted_backend_claimed must be false" in error for error in errors))
        self.assertTrue(any("hosted_connector_enabled must be false" in error for error in errors))
        self.assertTrue(any("live_probes_enabled must be false" in error for error in errors))
        self.assertTrue(any("source_sync_runtime_enabled must be false" in error for error in errors))
        self.assertTrue(any("downloads_enabled must be false" in error for error in errors))
        self.assertTrue(any("uploads_enabled must be false" in error for error in errors))
        self.assertTrue(any("accounts_enabled must be false" in error for error in errors))
        self.assertTrue(any("telemetry_enabled must be false" in error for error in errors))

    def test_rights_malware_bulk_crawl_claim_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["rights_summary"]["rights_clearance_claimed"] = True
        examples[0]["risk_summary"]["malware_safety_claimed"] = True
        examples[0]["source_access_policy"]["authorized_bulk_access_claimed"] = True
        examples[0]["source_access_policy"]["unrestricted_crawling_claimed"] = True

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
        self.assertTrue(any("authorized bulk access" in error for error in errors))
        self.assertTrue(any("unrestricted crawling" in error for error in errors))

    def test_missing_blocked_action_for_unavailable_capability_fails(self) -> None:
        policy, representations, semantic, route_matrix, examples = load_payloads()
        examples = copy.deepcopy(examples)
        examples[0]["blocked_actions"] = [
            action
            for action in examples[0]["blocked_actions"]
            if action["action_id"] != "source_sync_unavailable"
        ]

        errors = validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            examples,
            source_label="unit",
        )

        self.assertTrue(any("source_sync_unavailable" in error for error in errors))

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
