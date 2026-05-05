import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "cross-source-identity-resolution-contract-v0"
REPORT = AUDIT_DIR / "cross_source_identity_resolution_report.json"
DOC = ROOT / "docs" / "reference" / "CROSS_SOURCE_IDENTITY_RESOLUTION_CONTRACT.md"
POLICY = ROOT / "control" / "inventory" / "identity" / "cross_source_identity_resolution_policy.json"


class CrossSourceIdentityResolutionContractAuditTests(unittest.TestCase):
    def test_audit_pack_and_report_exist(self) -> None:
        required = {
            "README.md",
            "CONTRACT_SUMMARY.md",
            "IDENTITY_RESOLUTION_ASSESSMENT_SCHEMA.md",
            "IDENTITY_CLUSTER_SCHEMA.md",
            "IDENTITY_RELATION_TAXONOMY.md",
            "IDENTIFIER_MODEL.md",
            "ALIAS_AND_NAME_NORMALIZATION_MODEL.md",
            "VERSION_PLATFORM_ARCHITECTURE_MATCHING_MODEL.md",
            "SOURCE_AND_PROVENANCE_EVIDENCE_MODEL.md",
            "HASH_CHECKSUM_INTRINSIC_ID_MODEL.md",
            "PACKAGE_REPOSITORY_ARCHIVE_CAPTURE_IDENTITY_MODEL.md",
            "REPRESENTATION_AND_MEMBER_IDENTITY_MODEL.md",
            "CONFLICT_AND_DUPLICATE_PRESERVATION_MODEL.md",
            "CONFIDENCE_AND_REVIEW_MODEL.md",
            "PROMOTION_AND_MERGE_BOUNDARY_MODEL.md",
            "PUBLIC_SEARCH_OBJECT_SOURCE_COMPARISON_PROJECTION.md",
            "PRIVACY_AND_REDACTION_POLICY.md",
            "NO_DESTRUCTIVE_MERGE_POLICY.md",
            "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
            "INTEGRATION_BOUNDARIES.md",
            "EXAMPLE_IDENTITY_RESOLUTION_REVIEW.md",
            "FUTURE_RUNTIME_PATH.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "cross_source_identity_resolution_report.json",
        }
        self.assertTrue(AUDIT_DIR.exists())
        present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertTrue(required <= present)

    def test_report_hard_booleans_and_blockers(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        guarantees = report["no_runtime_no_mutation_guarantees"]
        for key in (
            "runtime_identity_resolution_implemented",
            "persistent_identity_store_implemented",
            "identity_cluster_runtime_implemented",
            "merge_runtime_implemented",
            "identity_cluster_created",
            "records_merged",
            "destructive_merge_performed",
            "destructive_merge_allowed",
            "candidate_promotion_allowed",
            "candidate_promotion_performed",
            "master_index_mutation_allowed",
            "public_index_mutation_allowed",
            "local_index_mutation_allowed",
            "source_cache_mutation_allowed",
            "evidence_ledger_mutation_allowed",
            "candidate_index_mutation_allowed",
            "public_search_identity_resolution_enabled_now",
            "live_source_called",
            "external_calls_performed",
            "telemetry_implemented",
        ):
            self.assertFalse(guarantees[key], key)
        self.assertIn("Result Merge and Deduplication Contract v0", report["next_recommended_branch"])
        self.assertTrue(report["remaining_blockers"])

    def test_policy_and_docs_state_contract_only_boundaries(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["status"], "contract_only")
        self.assertFalse(policy["runtime_identity_resolution_implemented"])
        self.assertFalse(policy["destructive_merge_allowed"])
        self.assertFalse(policy["candidate_promotion_allowed"])
        self.assertTrue(policy["confidence_not_truth_required"])
        self.assertTrue(policy["name_match_not_sufficient_alone"])
        text = DOC.read_text(encoding="utf-8").lower()
        for phrase in (
            "contract-only",
            "identity resolution is not runtime",
            "identity resolution is not destructive deduplication",
            "no destructive merge",
            "no records merged",
            "confidence_not_truth",
            "name_match_not_sufficient_alone",
            "no master index mutation",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
