from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_need_candidate_page_view_models import (
    CANDIDATE_EXAMPLE_PATHS,
    NEED_EXAMPLE_PATHS,
    validate_need_candidate_page_view_models,
    validate_payloads,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict, dict, dict, list[dict], list[dict]]:
    return (
        load_json(PUBLICATION_DIR / "need_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "candidate_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        load_json(PUBLICATION_DIR / "semantic_renderer_parity_policy.json"),
        load_json(PUBLICATION_DIR / "route_view_representation_matrix.json"),
        [load_json(REPO_ROOT / relative) for relative in NEED_EXAMPLE_PATHS],
        [load_json(REPO_ROOT / relative) for relative in CANDIDATE_EXAMPLE_PATHS],
    )


class NeedCandidatePageViewModelContractsTest(unittest.TestCase):
    def test_valid_need_examples_pass(self) -> None:
        report = validate_need_candidate_page_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["need_example_count"], 4)

    def test_valid_candidate_examples_pass(self) -> None:
        report = validate_need_candidate_page_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["candidate_example_count"], 4)

    def test_missing_canonical_need_identity_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        needs = copy.deepcopy(needs)
        needs[0]["need_identity"]["need_id"] = ""

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("canonical need identity need_id" in error for error in errors))

    def test_missing_canonical_candidate_identity_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["candidate_identity"]["candidate_id"] = ""

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("canonical candidate identity candidate_id" in error for error in errors))

    def test_invalid_representation_profile_reference_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        need_policy = copy.deepcopy(need_policy)
        need_policy["allowed_representation_profiles"].append("missing_profile")

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("missing_profile" in error for error in errors))

    def test_invalid_semantic_parity_policy_reference_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidate_policy = copy.deepcopy(candidate_policy)
        candidate_policy["required_semantic_parity_policy"] = "missing_parity_policy"

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("required_semantic_parity_policy" in error for error in errors))

    def test_invalid_need_status_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        needs = copy.deepcopy(needs)
        needs[0]["need_status"] = "verified_result"

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("need_status" in error for error in errors))

    def test_invalid_candidate_status_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["candidate_status"] = "verified"

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("candidate_status" in error for error in errors))

    def test_invalid_candidate_origin_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["candidate_identity"]["candidate_origin"] = "rumor"

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("candidate_origin" in error for error in errors))

    def test_demand_telemetry_user_tracking_claim_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        needs = copy.deepcopy(needs)
        needs[0]["demand_summary"]["raw_user_tracking_claimed"] = True
        needs[0]["demand_summary"]["public_raw_query_storage"] = True

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("raw_user_tracking_claimed" in error for error in errors))
        self.assertTrue(any("public_raw_query_storage" in error for error in errors))

    def test_absence_claiming_exhaustive_global_search_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        needs = copy.deepcopy(needs)
        needs[0]["absence_summary"]["exhaustive_global_search_claimed"] = True

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("exhaustive global search" in error for error in errors))

    def test_candidate_marked_accepted_public_truth_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["review_summary"]["accepted_public_status"] = True

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("accepted public truth" in error for error in errors))

    def test_source_observation_marked_accepted_truth_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["source_summary"]["source_observation_accepted_as_truth"] = True

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("source observation" in error for error in errors))

    def test_evidence_candidate_marked_accepted_truth_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["evidence_summary"]["evidence_candidate_accepted_as_truth"] = True

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("evidence candidate" in error for error in errors))

    def test_ai_draft_marked_evidence_truth_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["evidence_summary"]["ai_draft_marked_evidence_truth"] = True

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("AI draft" in error for error in errors))

    def test_current_example_claiming_runtime_capability_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        needs = copy.deepcopy(needs)
        summary = needs[0]["action_summary"]
        summary["hosted_backend_claimed"] = True
        summary["live_probes_enabled"] = True
        summary["source_sync_runtime_enabled"] = True
        summary["downloads_enabled"] = True
        summary["uploads_enabled"] = True
        summary["accounts_enabled"] = True
        summary["telemetry_enabled"] = True

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("hosted_backend_claimed must be false" in error for error in errors))
        self.assertTrue(any("live_probes_enabled must be false" in error for error in errors))
        self.assertTrue(any("source_sync_runtime_enabled must be false" in error for error in errors))
        self.assertTrue(any("downloads_enabled must be false" in error for error in errors))
        self.assertTrue(any("uploads_enabled must be false" in error for error in errors))
        self.assertTrue(any("accounts_enabled must be false" in error for error in errors))
        self.assertTrue(any("telemetry_enabled must be false" in error for error in errors))

    def test_rights_malware_installability_safe_execution_claim_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["rights_summary"]["rights_clearance_claimed"] = True
        candidates[0]["risk_summary"]["malware_safety_claimed"] = True
        candidates[0]["risk_summary"]["verified_installability_claimed"] = True
        candidates[0]["risk_summary"]["safe_execution_claimed"] = True

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safety" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))
        self.assertTrue(any("safe execution" in error for error in errors))

    def test_missing_blocked_action_for_unavailable_capability_fails(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()
        candidates = copy.deepcopy(candidates)
        candidates[0]["blocked_actions"] = [
            action
            for action in candidates[0]["blocked_actions"]
            if action["action_id"] != "accept_public_unavailable"
        ]

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertTrue(any("accept_public_unavailable" in error for error in errors))

    def test_policy_inventories_validate(self) -> None:
        need_policy, candidate_policy, representations, semantic, route_matrix, needs, candidates = load_payloads()

        errors = validate_payloads(
            need_policy,
            candidate_policy,
            representations,
            semantic,
            route_matrix,
            needs,
            candidates,
            source_label="unit",
        )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
