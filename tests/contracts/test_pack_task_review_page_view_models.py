from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_pack_task_review_page_view_models import (
    PACK_EXAMPLE_PATHS,
    REVIEW_EXAMPLE_PATHS,
    TASK_EXAMPLE_PATHS,
    validate_pack_task_review_page_view_models,
    validate_payloads,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict, dict, dict, dict, list[dict], list[dict], list[dict]]:
    return (
        load_json(PUBLICATION_DIR / "pack_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "task_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "review_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        load_json(PUBLICATION_DIR / "semantic_renderer_parity_policy.json"),
        load_json(PUBLICATION_DIR / "route_view_representation_matrix.json"),
        [load_json(REPO_ROOT / relative) for relative in PACK_EXAMPLE_PATHS],
        [load_json(REPO_ROOT / relative) for relative in TASK_EXAMPLE_PATHS],
        [load_json(REPO_ROOT / relative) for relative in REVIEW_EXAMPLE_PATHS],
    )


def validate_with(
    pack_policy: dict,
    task_policy: dict,
    review_policy: dict,
    representations: dict,
    semantic: dict,
    route_matrix: dict,
    packs: list[dict],
    tasks: list[dict],
    reviews: list[dict],
) -> list[str]:
    return validate_payloads(
        pack_policy,
        task_policy,
        review_policy,
        representations,
        semantic,
        route_matrix,
        packs,
        tasks,
        reviews,
        source_label="unit",
    )


class PackTaskReviewPageViewModelContractsTest(unittest.TestCase):
    def test_valid_pack_examples_pass(self) -> None:
        report = validate_pack_task_review_page_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["pack_example_count"], 4)

    def test_valid_task_examples_pass(self) -> None:
        report = validate_pack_task_review_page_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["task_example_count"], 4)

    def test_valid_review_examples_pass(self) -> None:
        report = validate_pack_task_review_page_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["review_example_count"], 4)

    def test_missing_canonical_pack_identity_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        packs = copy.deepcopy(packs)
        packs[0]["pack_identity"]["pack_id"] = ""

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("canonical pack identity pack_id" in error for error in errors))

    def test_missing_canonical_task_identity_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        tasks = copy.deepcopy(tasks)
        tasks[0]["task_identity"]["task_id"] = ""

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("canonical task identity task_id" in error for error in errors))

    def test_missing_canonical_review_identity_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        reviews = copy.deepcopy(reviews)
        reviews[0]["review_identity"]["review_id"] = ""

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("canonical review identity review_id" in error for error in errors))

    def test_invalid_representation_profile_reference_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        pack_policy = copy.deepcopy(pack_policy)
        pack_policy["allowed_representation_profiles"].append("missing_profile")

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("missing_profile" in error for error in errors))

    def test_invalid_semantic_parity_policy_reference_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        task_policy = copy.deepcopy(task_policy)
        task_policy["required_semantic_parity_policy"] = "missing_parity_policy"

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("required_semantic_parity_policy" in error for error in errors))

    def test_invalid_pack_status_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        packs = copy.deepcopy(packs)
        packs[0]["pack_status"] = "imported"

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("pack_status" in error for error in errors))

    def test_invalid_task_status_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        tasks = copy.deepcopy(tasks)
        tasks[0]["task_status"] = "running"

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("task_status" in error for error in errors))

    def test_invalid_review_status_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        reviews = copy.deepcopy(reviews)
        reviews[0]["review_status"] = "approved_now"

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("review_status" in error for error in errors))

    def test_invalid_review_decision_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        reviews = copy.deepcopy(reviews)
        reviews[0]["review_decision_summary"]["review_decision"] = "approve_now"

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("review_decision" in error for error in errors))

    def test_pack_import_upload_auto_acceptance_claim_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        packs = copy.deepcopy(packs)
        packs[0]["import_summary"]["import_runtime_enabled"] = True
        packs[0]["import_summary"]["uploads_enabled"] = True
        packs[0]["import_summary"]["automatic_acceptance_enabled"] = True
        packs[0]["import_summary"]["master_index_mutation_allowed"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("import_runtime_enabled must be false" in error for error in errors))
        self.assertTrue(any("automatic_acceptance_enabled must be false" in error for error in errors))
        self.assertTrue(any("master_index_mutation_allowed must be false" in error for error in errors))

    def test_task_live_source_model_call_autonomous_runtime_claim_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        tasks = copy.deepcopy(tasks)
        tasks[0]["execution_summary"]["live_source_access_enabled"] = True
        tasks[0]["execution_summary"]["model_calls_enabled"] = True
        tasks[0]["execution_summary"]["autonomous_execution_enabled"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("live_source_access_enabled must be false" in error for error in errors))
        self.assertTrue(any("model_calls_enabled must be false" in error for error in errors))
        self.assertTrue(any("autonomous_execution_enabled must be false" in error for error in errors))

    def test_review_hosted_moderation_master_index_mutation_claim_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        reviews = copy.deepcopy(reviews)
        reviews[0]["queue_entry_summary"]["hosted_moderation_enabled"] = True
        reviews[0]["master_index_summary"]["master_index_mutation_allowed"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("queue_entry_summary.hosted_moderation_enabled must be false" in error for error in errors))
        self.assertTrue(any("master_index_summary.master_index_mutation_allowed must be false" in error for error in errors))

    def test_source_observation_marked_accepted_truth_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        packs = copy.deepcopy(packs)
        packs[0]["provenance_summary"]["source_observation_accepted_as_truth"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("source observation" in error for error in errors))

    def test_evidence_candidate_marked_accepted_truth_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        tasks = copy.deepcopy(tasks)
        tasks[0]["evidence_summary"]["evidence_candidate_accepted_as_truth"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("evidence candidate" in error for error in errors))

    def test_contribution_item_marked_accepted_public_record_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        packs = copy.deepcopy(packs)
        packs[0]["pack_contents_summary"]["contribution_items_accepted_public"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("contribution item" in error for error in errors))

    def test_ai_draft_marked_evidence_truth_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        reviews = copy.deepcopy(reviews)
        reviews[0]["provenance_summary"]["ai_draft_marked_evidence_truth"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("AI draft" in error for error in errors))

    def test_current_example_claiming_runtime_capability_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        tasks = copy.deepcopy(tasks)
        summary = tasks[0]["action_summary"]
        summary["hosted_backend_claimed"] = True
        summary["live_probes_enabled"] = True
        summary["source_sync_runtime_enabled"] = True
        summary["downloads_enabled"] = True
        summary["uploads_enabled"] = True
        summary["accounts_enabled"] = True
        summary["telemetry_enabled"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("hosted_backend_claimed must be false" in error for error in errors))
        self.assertTrue(any("live_probes_enabled must be false" in error for error in errors))
        self.assertTrue(any("source_sync_runtime_enabled must be false" in error for error in errors))
        self.assertTrue(any("downloads_enabled must be false" in error for error in errors))
        self.assertTrue(any("uploads_enabled must be false" in error for error in errors))
        self.assertTrue(any("accounts_enabled must be false" in error for error in errors))
        self.assertTrue(any("telemetry_enabled must be false" in error for error in errors))

    def test_rights_malware_installability_safe_execution_claim_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        reviews = copy.deepcopy(reviews)
        reviews[0]["rights_summary"]["rights_clearance_claimed"] = True
        reviews[0]["risk_summary"]["malware_safety_claimed"] = True
        reviews[0]["risk_summary"]["verified_installability_claimed"] = True
        reviews[0]["risk_summary"]["safe_execution_claimed"] = True

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safety" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))
        self.assertTrue(any("safe execution" in error for error in errors))

    def test_missing_blocked_action_for_unavailable_capability_fails(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()
        reviews = copy.deepcopy(reviews)
        reviews[0]["blocked_actions"] = [
            action
            for action in reviews[0]["blocked_actions"]
            if action["action_id"] != "master_index_mutation_unavailable"
        ]

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertTrue(any("master_index_mutation_unavailable" in error for error in errors))

    def test_policy_inventories_validate(self) -> None:
        pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews = load_payloads()

        errors = validate_with(pack_policy, task_policy, review_policy, representations, semantic, route_matrix, packs, tasks, reviews)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
