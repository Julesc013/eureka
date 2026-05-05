import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "source-page-contract-v0"
REPORT_PATH = AUDIT_DIR / "source_page_contract_report.json"
CONTRACT_PATH = ROOT / "contracts" / "pages" / "source_page.v0.json"
DOC_PATH = ROOT / "docs" / "reference" / "SOURCE_PAGE_CONTRACT.md"


class SourcePageContractAuditTests(unittest.TestCase):
    def test_required_audit_files_exist(self) -> None:
        required = {
            "README.md",
            "CONTRACT_SUMMARY.md",
            "SOURCE_PAGE_SCHEMA.md",
            "SOURCE_IDENTITY_MODEL.md",
            "SOURCE_FAMILY_AND_STATUS_MODEL.md",
            "SOURCE_COVERAGE_MODEL.md",
            "CONNECTOR_POSTURE_MODEL.md",
            "SOURCE_POLICY_AND_APPROVAL_MODEL.md",
            "SOURCE_CACHE_AND_EVIDENCE_LEDGER_PROJECTION.md",
            "PUBLIC_INDEX_AND_SEARCH_PROJECTION.md",
            "QUERY_INTELLIGENCE_PROJECTION.md",
            "SOURCE_LIMITATION_AND_GAP_MODEL.md",
            "SOURCE_TRUST_AND_PROVENANCE_CAUTION_MODEL.md",
            "RIGHTS_ACCESS_AND_RISK_POSTURE_MODEL.md",
            "RESULT_CARD_AND_SOURCE_BADGE_PROJECTION.md",
            "API_PROJECTION.md",
            "STATIC_DEMO_PROJECTION.md",
            "PRIVACY_AND_REDACTION_POLICY.md",
            "NO_LIVE_CALL_DOWNLOAD_OR_MUTATION_POLICY.md",
            "INTEGRATION_BOUNDARIES.md",
            "EXAMPLE_SOURCE_PAGE_REVIEW.md",
            "FUTURE_RUNTIME_PATH.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "source_page_contract_report.json",
        }
        present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertTrue(required.issubset(present))

    def test_schema_and_examples_exist(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["x-status"], "contract_only")
        for rel in (
            "minimal_fixture_source_page_v0",
            "minimal_recorded_fixture_source_page_v0",
            "minimal_connector_approval_source_page_v0",
            "minimal_placeholder_source_page_v0",
        ):
            self.assertTrue((ROOT / "examples" / "source_pages" / rel / "SOURCE_PAGE.json").is_file())

    def test_report_no_runtime_no_mutation(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "source_page_contract_v0")
        for key in (
            "runtime_source_pages_implemented",
            "persistent_source_page_store_implemented",
            "source_page_generated_from_live_source",
            "connector_runtime_implemented",
            "connector_live_enabled",
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
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "source_trust_claimed",
            "telemetry_implemented",
        ):
            self.assertFalse(report[key], key)
        self.assertEqual(report["next_recommended_branch"], "P81 Comparison Page Contract v0")

    def test_docs_state_contract_only_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8").casefold()
        for phrase in (
            "contract-only",
            "source page is not connector runtime",
            "source page is not source trust authority",
            "no live source",
            "no source cache mutation",
            "no evidence ledger mutation",
            "no candidate promotion",
            "no download",
            "no install",
            "no execution",
            "no rights clearance",
            "no malware safety",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
