import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "result-merge-deduplication-contract-v0"
REPORT = AUDIT_DIR / "result_merge_deduplication_report.json"
DOC = ROOT / "docs" / "reference" / "RESULT_MERGE_DEDUPLICATION_CONTRACT.md"
POLICY = ROOT / "control" / "inventory" / "search" / "result_merge_deduplication_policy.json"


class ResultMergeDeduplicationContractAuditTests(unittest.TestCase):
    def test_audit_pack_and_report_exist(self) -> None:
        required = {
            "README.md",
            "CONTRACT_SUMMARY.md",
            "RESULT_MERGE_GROUP_SCHEMA.md",
            "DEDUPLICATION_ASSESSMENT_SCHEMA.md",
            "MERGE_RELATION_TAXONOMY.md",
            "DUPLICATE_NEAR_DUPLICATE_VARIANT_CONFLICT_MODEL.md",
            "GROUPING_CRITERIA_MODEL.md",
            "CANONICAL_DISPLAY_RECORD_POLICY.md",
            "COLLAPSED_RESULT_TRANSPARENCY_POLICY.md",
            "EXPAND_COLLAPSE_USER_FACING_MODEL.md",
            "SOURCE_EVIDENCE_PROVENANCE_PRESERVATION_MODEL.md",
            "IDENTITY_RESOLUTION_RELATIONSHIP.md",
            "OBJECT_SOURCE_COMPARISON_PAGE_RELATIONSHIP.md",
            "PUBLIC_SEARCH_RESULT_CARD_PROJECTION.md",
            "API_PROJECTION.md",
            "STATIC_DEMO_PROJECTION.md",
            "PRIVACY_AND_REDACTION_POLICY.md",
            "NO_DESTRUCTIVE_MERGE_POLICY.md",
            "NO_RANKING_PROMOTION_OR_MUTATION_POLICY.md",
            "INTEGRATION_BOUNDARIES.md",
            "EXAMPLE_RESULT_MERGE_REVIEW.md",
            "FUTURE_RUNTIME_PATH.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "result_merge_deduplication_report.json",
        }
        self.assertTrue(AUDIT_DIR.exists())
        present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertTrue(required <= present)

    def test_report_hard_booleans_and_blockers(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        guarantees = report["no_runtime_no_mutation_guarantees"]
        for key in (
            "runtime_result_merge_implemented",
            "runtime_deduplication_implemented",
            "persistent_merge_group_store_implemented",
            "public_search_runtime_grouping_enabled",
            "public_search_ranking_changed",
            "deduplication_applied_to_live_search",
            "records_merged",
            "duplicates_deleted",
            "results_suppressed",
            "results_hidden_without_explanation",
            "destructive_merge_performed",
            "destructive_merge_allowed",
            "canonical_record_claimed_as_truth",
            "candidate_promotion_allowed",
            "candidate_promotion_performed",
            "master_index_mutation_allowed",
            "public_index_mutation_allowed",
            "local_index_mutation_allowed",
            "source_cache_mutation_allowed",
            "evidence_ledger_mutation_allowed",
            "candidate_index_mutation_allowed",
            "live_source_called",
            "external_calls_performed",
            "telemetry_implemented",
        ):
            self.assertFalse(guarantees[key], key)
        self.assertIn("Evidence-Weighted Ranking Contract v0", report["next_recommended_branch"])
        self.assertTrue(report["remaining_blockers"])

    def test_policy_and_docs_state_boundaries(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["status"], "contract_only")
        self.assertFalse(policy["runtime_result_merge_implemented"])
        self.assertFalse(policy["runtime_deduplication_implemented"])
        self.assertFalse(policy["public_search_ranking_changed"])
        self.assertFalse(policy["records_merged"])
        self.assertFalse(policy["duplicates_deleted"])
        self.assertFalse(policy["hidden_without_explanation_allowed"])
        self.assertFalse(policy["canonical_display_is_truth"])
        self.assertTrue(policy["exact_duplicate_requires_strong_identifier_or_review"])
        self.assertTrue(policy["weak_name_match_not_sufficient_for_exact_duplicate"])
        text = DOC.read_text(encoding="utf-8").lower()
        for phrase in (
            "contract-only",
            "result merge is not identity truth",
            "result merge is not destructive record merge",
            "result merge is not ranking",
            "canonical display record is not truth",
            "conflicts must not be hidden",
            "no result may be suppressed without user-visible explanation",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
