import json
import unittest
from pathlib import Path

from runtime.local.foundry import candidate_promotion_dry_run as promotion


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def build_from_candidate(candidate_name: str = "search_need_candidate_v0.json", *, evidence: list[dict] | None = None, review: list[dict] | None = None) -> dict:
    return promotion.build_candidate_promotion_dry_run(
        {
            "candidate": load_json(f"examples/index/candidates/{candidate_name}"),
            "evidence_records": evidence or [],
            "review_entries": review or [],
        }
    )


class CandidatePromotionDryRunRuntimeTests(unittest.TestCase):
    def test_build_promotion_dry_run_works_on_candidate_example(self) -> None:
        record = build_from_candidate(review=[load_json("examples/review/queue_entries/candidate_needs_review_v0.json")])
        self.assertEqual(record["candidate_ref"], "candidate.search_need.software_version.v0")
        self.assertEqual(record["promotion_readiness"], "not_ready_missing_evidence")
        self.assertFalse(record["truth_boundary"]["promotion_dry_run_accepts_candidate"])

    def test_candidate_with_review_and_fixture_evidence_can_be_ready(self) -> None:
        record = build_from_candidate(
            evidence=[load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")],
            review=[load_json("examples/review/queue_entries/workunit_result_review_v0.json")],
        )
        self.assertEqual(record["promotion_readiness"], "ready_for_future_reviewed_record_proposal")
        self.assertEqual(record["promotion_dry_run_status"], "ready_for_promotion_dry_run")
        self.assertEqual(record["blockers"], [])

    def test_candidate_missing_evidence_is_blocked(self) -> None:
        record = build_from_candidate(review=[load_json("examples/review/queue_entries/workunit_result_review_v0.json")])
        self.assertEqual(record["promotion_readiness"], "not_ready_missing_evidence")
        self.assertIn("missing_evidence", {blocker["blocker_category"] for blocker in record["blockers"]})

    def test_candidate_missing_review_is_blocked(self) -> None:
        record = build_from_candidate(evidence=[load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")])
        self.assertEqual(record["promotion_readiness"], "not_ready_missing_review")
        self.assertIn("missing_review", {blocker["blocker_category"] for blocker in record["blockers"]})

    def test_conflict_detected_candidate_is_blocked(self) -> None:
        candidate = load_json("examples/index/candidates/search_need_candidate_v0.json")
        candidate["candidate_status"] = "conflict_detected"
        record = promotion.build_candidate_promotion_dry_run(
            {
                "candidate": candidate,
                "evidence_records": [load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")],
                "review_entries": [load_json("examples/review/queue_entries/workunit_result_review_v0.json")],
            }
        )
        self.assertEqual(record["promotion_readiness"], "not_ready_conflict_unresolved")

    def test_duplicate_uncertain_candidate_is_blocked(self) -> None:
        record = build_from_candidate(
            "duplicate_possible_candidate_v0.json",
            evidence=[load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")],
            review=[load_json("examples/review/queue_entries/workunit_result_review_v0.json")],
        )
        self.assertEqual(record["promotion_readiness"], "not_ready_duplicate_uncertain")

    def test_policy_blocked_candidate_is_blocked(self) -> None:
        record = build_from_candidate(
            "policy_blocked_candidate_v0.json",
            evidence=[load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")],
            review=[load_json("examples/review/queue_entries/workunit_result_review_v0.json")],
        )
        self.assertEqual(record["promotion_readiness"], "not_ready_policy_blocked")

    def test_rights_risk_blocked_candidate_is_blocked(self) -> None:
        candidate = load_json("examples/index/candidates/search_need_candidate_v0.json")
        candidate["candidate_status"] = "rights_blocked"
        record = promotion.build_candidate_promotion_dry_run(
            {
                "candidate": candidate,
                "evidence_records": [load_json("examples/evidence/ledger/records/metadata_claim_record_v0.json")],
                "review_entries": [load_json("examples/review/queue_entries/workunit_result_review_v0.json")],
            }
        )
        self.assertEqual(record["promotion_readiness"], "not_ready_rights_blocked")

    def test_ready_for_promotion_dry_run_does_not_accept_candidate_or_evidence(self) -> None:
        record = promotion.build_candidate_promotion_dry_run(load_json("examples/review/candidate_promotion_dry_runs/ready_for_promotion_dry_run_v0.json"))
        truth = record["truth_boundary"]
        self.assertFalse(truth["promotion_dry_run_accepts_candidate"])
        self.assertFalse(truth["promotion_dry_run_accepts_evidence"])
        self.assertFalse(truth["promotion_dry_run_creates_public_record"])

    def test_promotion_dry_run_does_not_mutate_indexes(self) -> None:
        record = promotion.build_candidate_promotion_dry_run(load_json("examples/review/candidate_promotion_dry_runs/ready_for_promotion_dry_run_v0.json"))
        truth = record["truth_boundary"]
        product = record["product_boundary"]
        self.assertFalse(truth["promotion_dry_run_mutates_public_index"])
        self.assertFalse(truth["promotion_dry_run_mutates_master_index"])
        self.assertFalse(product["mutated_public_index"])
        self.assertFalse(product["mutated_master_index"])

    def test_rights_malware_installability_and_exhaustive_claims_are_rejected(self) -> None:
        record = promotion.build_candidate_promotion_dry_run(load_json("examples/review/candidate_promotion_dry_runs/minimal_promotion_dry_run_v0.json"))
        record["truth_boundary"]["promotion_dry_run_can_claim_rights_clearance"] = True
        record["truth_boundary"]["promotion_dry_run_can_claim_malware_safety"] = True
        record["truth_boundary"]["promotion_dry_run_can_claim_verified_installability"] = True
        record["truth_boundary"]["promotion_dry_run_can_claim_exhaustive_global_search"] = True
        errors = promotion.validate_candidate_promotion_dry_run(record)
        self.assertTrue(any("rights_clearance" in error for error in errors), errors)
        self.assertTrue(any("malware_safety" in error for error in errors), errors)
        self.assertTrue(any("verified_installability" in error for error in errors), errors)
        self.assertTrue(any("exhaustive_global_search" in error for error in errors), errors)

    def test_hosted_moderation_claim_is_rejected(self) -> None:
        record = promotion.build_candidate_promotion_dry_run(load_json("examples/review/candidate_promotion_dry_runs/minimal_promotion_dry_run_v0.json"))
        record["product_boundary"]["implemented_hosted_review_runtime"] = True
        errors = promotion.validate_candidate_promotion_dry_run(record)
        self.assertTrue(any("implemented_hosted_review_runtime" in error for error in errors), errors)

    def test_duplicate_and_conflict_are_not_auto_resolved(self) -> None:
        record = promotion.build_candidate_promotion_dry_run(load_json("examples/review/candidate_promotion_dry_runs/duplicate_blocked_promotion_dry_run_v0.json"))
        record["blockers"][0]["automatic_merge_allowed"] = True
        errors = promotion.validate_candidate_promotion_dry_run(record)
        self.assertTrue(any("automatic_merge_allowed" in error for error in errors), errors)

    def test_product_boundary_true_claim_fails(self) -> None:
        record = promotion.build_candidate_promotion_dry_run(load_json("examples/review/candidate_promotion_dry_runs/minimal_promotion_dry_run_v0.json"))
        record["product_boundary"]["enabled_telemetry"] = True
        self.assertTrue(promotion.detect_promotion_product_boundary_violations(record))

    def test_runtime_does_not_import_network_model_or_provider_modules(self) -> None:
        source = (REPO_ROOT / "runtime/local/foundry/candidate_promotion_dry_run.py").read_text(encoding="utf-8")
        for token in ["requests", "urllib", "http.client", "socket", "openai", "anthropic", "selenium", "playwright"]:
            self.assertNotIn(token, source)

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)
        record = promotion.build_candidate_promotion_dry_run(load_json("examples/review/candidate_promotion_dry_runs/ready_for_promotion_dry_run_v0.json"))
        self.assertFalse(record["product_boundary"]["mutated_master_index"])


if __name__ == "__main__":
    unittest.main()
