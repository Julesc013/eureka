import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "comparison-page-contract-v0"
REPORT_PATH = AUDIT_DIR / "comparison_page_contract_report.json"
CONTRACT_PATH = ROOT / "contracts" / "pages" / "comparison_page.v0.json"
DOC_PATH = ROOT / "docs" / "reference" / "COMPARISON_PAGE_CONTRACT.md"


class ComparisonPageContractAuditTests(unittest.TestCase):
    def test_required_audit_files_exist(self) -> None:
        required = {
            "README.md",
            "CONTRACT_SUMMARY.md",
            "COMPARISON_PAGE_SCHEMA.md",
            "COMPARISON_SUBJECT_MODEL.md",
            "COMPARISON_TYPE_TAXONOMY.md",
            "COMPARISON_CRITERIA_MODEL.md",
            "IDENTITY_SAME_AS_DIFFERENT_FROM_MODEL.md",
            "VERSION_STATE_RELEASE_COMPARISON_MODEL.md",
            "REPRESENTATION_AND_MEMBER_COMPARISON_MODEL.md",
            "SOURCE_EVIDENCE_PROVENANCE_COMPARISON_MODEL.md",
            "COMPATIBILITY_COMPARISON_MODEL.md",
            "RIGHTS_RISK_ACTION_COMPARISON_MODEL.md",
            "CONFLICT_DUPLICATE_AND_DISAGREEMENT_MODEL.md",
            "ABSENCE_NEAR_MISS_AND_GAP_COMPARISON_MODEL.md",
            "RESULT_CARD_OBJECT_SOURCE_PROJECTION.md",
            "API_PROJECTION.md",
            "STATIC_DEMO_PROJECTION.md",
            "PRIVACY_AND_REDACTION_POLICY.md",
            "NO_WINNER_WITHOUT_EVIDENCE_POLICY.md",
            "NO_DOWNLOAD_INSTALL_EXECUTION_POLICY.md",
            "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
            "INTEGRATION_BOUNDARIES.md",
            "EXAMPLE_COMPARISON_PAGE_REVIEW.md",
            "FUTURE_RUNTIME_PATH.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "comparison_page_contract_report.json",
        }
        present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertTrue(required.issubset(present))

    def test_schema_and_examples_exist(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["x-status"], "contract_only")
        for rel in (
            "minimal_object_comparison_page_v0",
            "minimal_version_comparison_page_v0",
            "minimal_source_comparison_page_v0",
            "minimal_compatibility_comparison_page_v0",
            "minimal_conflicted_comparison_page_v0",
        ):
            self.assertTrue((ROOT / "examples" / "comparison_pages" / rel / "COMPARISON_PAGE.json").is_file())

    def test_report_no_runtime_no_mutation_no_winner(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "comparison_page_contract_v0")
        for key in (
            "runtime_comparison_pages_implemented",
            "persistent_comparison_page_store_implemented",
            "comparison_page_generated_from_live_source",
            "comparison_winner_claimed",
            "live_source_called",
            "external_calls_performed",
            "source_sync_worker_executed",
            "source_cache_mutation_allowed",
            "evidence_ledger_mutation_allowed",
            "candidate_index_mutation_allowed",
            "candidate_promotion_allowed",
            "public_index_mutation_allowed",
            "local_index_mutation_allowed",
            "master_index_mutation_allowed",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "execution_enabled",
            "arbitrary_url_fetch_enabled",
            "winner_claims_allowed_without_evidence",
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "source_trust_claimed",
            "telemetry_implemented",
        ):
            self.assertFalse(report[key], key)
        self.assertEqual(report["next_recommended_branch"], "P82 Cross-Source Identity Resolution Contract v0")

    def test_docs_state_contract_only_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8").casefold()
        for phrase in (
            "contract-only",
            "comparison page is not ranking authority",
            "comparison page is not candidate promotion",
            "no runtime comparison pages",
            "no live source",
            "no source cache mutation",
            "no evidence ledger mutation",
            "no candidate promotion",
            "no winner without evidence",
            "no download",
            "no install",
            "no execution",
            "no rights clearance",
            "no malware safety",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
