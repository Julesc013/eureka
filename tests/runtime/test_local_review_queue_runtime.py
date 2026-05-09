import json
import unittest
from pathlib import Path

from runtime.local_foundry import review_queue


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_example(name: str) -> dict:
    return json.loads((REPO_ROOT / "examples/review_queue_entries" / name).read_text(encoding="utf-8"))


def errors_for(entry: dict) -> list[str]:
    return review_queue.validate_review_queue_entry(entry)


class LocalReviewQueueRuntimeTests(unittest.TestCase):
    def test_build_review_queue_entry_works_on_candidate_needs_review_example(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("candidate_needs_review_v0.json"))
        self.assertEqual(entry["review_subject_type"], "candidate_record")
        self.assertEqual(entry["review_entry_status"], "needs_review")
        self.assertFalse(entry["truth_boundary"]["review_entry_accepts_candidate"])
        self.assertTrue(entry["truth_boundary"]["human_review_required_for_downstream_use"])

    def test_evidence_candidate_review_entry_classifies_correctly(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("evidence_candidate_needs_review_v0.json"))
        self.assertEqual(review_queue.classify_review_subject(entry), "evidence_candidate")

    def test_source_cache_record_review_entry_classifies_correctly(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("source_cache_record_needs_review_v0.json"))
        self.assertEqual(review_queue.classify_review_subject(entry), "source_cache_record")

    def test_source_cache_bridge_review_entry_classifies_correctly(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("source_cache_bridge_needs_review_v0.json"))
        self.assertEqual(review_queue.classify_review_subject(entry), "source_cache_to_evidence_bridge_result")

    def test_workunit_result_review_entry_classifies_correctly(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("workunit_result_review_v0.json"))
        self.assertEqual(review_queue.classify_review_subject(entry), "workunit_result")
        self.assertEqual(review_queue.classify_review_decision(entry), "approve_for_promotion_dry_run")
        self.assertTrue(entry["promotion_readiness"]["ready_for_promotion_dry_run"])
        self.assertFalse(entry["promotion_readiness"]["promotion_is_public_acceptance"])

    def test_duplicate_review_entry_marks_duplicate_without_merging(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("duplicate_review_entry_v0.json"))
        self.assertEqual(entry["review_entry_status"], "duplicate_possible")
        self.assertEqual(entry["review_decision"], "mark_duplicate_possible")
        self.assertFalse(entry["duplicate_summary"]["automatic_merge_allowed"])
        self.assertFalse(entry["duplicate_summary"]["automatic_delete_allowed"])

    def test_reject_review_entry_rejects_only_locally(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("reject_review_entry_v0.json"))
        self.assertEqual(entry["review_decision"], "reject")
        self.assertFalse(entry["truth_boundary"]["review_entry_accepts_candidate"])
        self.assertFalse(entry["truth_boundary"]["review_entry_accepts_evidence"])
        self.assertFalse(entry["truth_boundary"]["review_entry_mutates_master_index"])

    def test_request_more_evidence_entry_requires_missing_evidence_fields(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("request_more_evidence_review_entry_v0.json"))
        self.assertEqual(review_queue.validate_review_queue_entry(entry), [])
        entry["missing_evidence"] = []
        errors = errors_for(entry)
        self.assertTrue(any("missing_evidence" in error for error in errors), errors)

    def test_policy_blocked_review_entry_remains_policy_blocked(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("policy_blocked_review_entry_v0.json"))
        self.assertEqual(entry["review_entry_status"], "policy_blocked")
        self.assertEqual(entry["review_decision"], "policy_block")

    def test_review_queue_truth_boundary_violation_is_rejected(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("minimal_review_queue_entry_v0.json"))
        entry["truth_boundary"]["review_entry_is_public_truth"] = True
        errors = errors_for(entry)
        self.assertTrue(any("public_truth" in error for error in errors), errors)

    def test_accepted_evidence_claim_is_rejected(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("minimal_review_queue_entry_v0.json"))
        entry["truth_boundary"]["review_entry_accepts_evidence"] = True
        errors = errors_for(entry)
        self.assertTrue(any("accepts_evidence" in error for error in errors), errors)

    def test_accepted_candidate_or_public_truth_claim_is_rejected(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("minimal_review_queue_entry_v0.json"))
        entry["truth_boundary"]["review_entry_accepts_candidate"] = True
        entry["truth_boundary"]["review_entry_allows_public_index_mutation"] = True
        errors = errors_for(entry)
        self.assertTrue(any("accepts_candidate" in error for error in errors), errors)
        self.assertTrue(any("public_index_mutation" in error for error in errors), errors)

    def test_master_index_mutation_claim_is_rejected(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("minimal_review_queue_entry_v0.json"))
        entry["truth_boundary"]["review_entry_mutates_master_index"] = True
        errors = errors_for(entry)
        self.assertTrue(any("mutates_master_index" in error for error in errors), errors)

    def test_rights_malware_installability_and_exhaustive_claims_are_rejected(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("minimal_review_queue_entry_v0.json"))
        entry["rights_risk_summary"]["rights_clearance_claimed"] = True
        entry["rights_risk_summary"]["malware_safety_claimed"] = True
        entry["rights_risk_summary"]["verified_installability_claimed"] = True
        entry["truth_boundary"]["review_entry_can_claim_exhaustive_global_search"] = True
        errors = errors_for(entry)
        self.assertTrue(any("rights_clearance_claimed" in error for error in errors), errors)
        self.assertTrue(any("malware_safety_claimed" in error for error in errors), errors)
        self.assertTrue(any("verified_installability_claimed" in error for error in errors), errors)
        self.assertTrue(any("exhaustive_global_search" in error for error in errors), errors)

    def test_hosted_moderation_claim_is_rejected(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("minimal_review_queue_entry_v0.json"))
        entry["product_boundary"]["implemented_hosted_review_runtime"] = True
        errors = errors_for(entry)
        self.assertTrue(any("implemented_hosted_review_runtime" in error for error in errors), errors)

    def test_conflict_is_preserved_without_auto_resolution(self) -> None:
        entry = review_queue.build_review_queue_entry(load_example("minimal_review_queue_entry_v0.json"))
        entry["review_entry_status"] = "conflict_detected"
        entry["review_decision"] = "preserve_conflict"
        entry["conflict_summary"] = {
            "conflict_detected": True,
            "automatic_conflict_resolution_allowed": False,
            "automatic_merge_allowed": False,
        }
        self.assertEqual(review_queue.validate_review_queue_entry(entry), [])
        entry["conflict_summary"]["automatic_conflict_resolution_allowed"] = True
        errors = errors_for(entry)
        self.assertTrue(any("automatic_conflict_resolution_allowed" in error for error in errors), errors)

    def test_snapshot_counts_review_entries(self) -> None:
        entries = [
            review_queue.build_review_queue_entry(load_example("candidate_needs_review_v0.json")),
            review_queue.build_review_queue_entry(load_example("request_more_evidence_review_entry_v0.json")),
            review_queue.build_review_queue_entry(load_example("policy_blocked_review_entry_v0.json")),
        ]
        snapshot = review_queue.build_review_queue_snapshot(entries)
        self.assertEqual(snapshot["review_entry_count"], 3)
        self.assertEqual(snapshot["request_more_evidence_count"], 1)
        self.assertEqual(snapshot["blocked_count"], 1)

    def test_runtime_does_not_import_network_model_or_provider_modules(self) -> None:
        source = (REPO_ROOT / "runtime/local_foundry/review_queue.py").read_text(encoding="utf-8")
        forbidden = ["requests", "urllib", "http.client", "socket", "openai", "anthropic", "selenium", "playwright"]
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)
        entry = review_queue.build_review_queue_entry(load_example("minimal_review_queue_entry_v0.json"))
        self.assertFalse(entry["product_boundary"]["mutated_master_index"])


if __name__ == "__main__":
    unittest.main()
