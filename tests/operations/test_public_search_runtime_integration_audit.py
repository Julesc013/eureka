import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "public-search-runtime-integration-audit-v0"
REPORT = AUDIT / "public_search_runtime_integration_audit_report.json"
INVENTORY = ROOT / "control" / "inventory" / "publication" / "public_search_runtime_integration_status.json"
DOC = ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RUNTIME_INTEGRATION_AUDIT.md"


VALID_CLASSIFICATIONS = {
    "implemented_public_runtime",
    "implemented_local_runtime",
    "implemented_local_dry_run",
    "implemented_static_artifact",
    "contract_only",
    "planning_only",
    "approval_gated",
    "operator_gated",
    "disabled",
    "absent",
    "blocked",
    "unexpected_integration",
}

REQUIRED_FILES = {
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "INTEGRATION_STATUS_MATRIX.md",
    "PUBLIC_SEARCH_RUNTIME_STATUS.md",
    "PUBLIC_SEARCH_ROUTE_STATUS.md",
    "PUBLIC_INDEX_STATUS.md",
    "STATIC_SITE_SEARCH_HANDOFF_STATUS.md",
    "HOSTED_DEPLOYMENT_STATUS.md",
    "SOURCE_CACHE_DRY_RUN_INTEGRATION_STATUS.md",
    "EVIDENCE_LEDGER_DRY_RUN_INTEGRATION_STATUS.md",
    "QUERY_OBSERVATION_INTEGRATION_STATUS.md",
    "PAGE_RUNTIME_INTEGRATION_STATUS.md",
    "CONNECTOR_RUNTIME_INTEGRATION_STATUS.md",
    "PACK_IMPORT_INTEGRATION_STATUS.md",
    "DEEP_EXTRACTION_INTEGRATION_STATUS.md",
    "SEARCH_RESULT_EXPLANATION_INTEGRATION_STATUS.md",
    "RANKING_RUNTIME_INTEGRATION_STATUS.md",
    "SAFETY_AND_BLOCKED_REQUEST_STATUS.md",
    "MUTATION_BOUNDARY_STATUS.md",
    "TELEMETRY_ACCOUNT_UPLOAD_DOWNLOAD_STATUS.md",
    "ARCHITECTURE_BOUNDARY_REVIEW.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "public_search_runtime_integration_audit_report.json",
}


class PublicSearchRuntimeIntegrationAuditOperationTests(unittest.TestCase):
    def test_audit_pack_inventory_and_docs_exist(self):
        self.assertTrue(AUDIT.exists())
        for name in REQUIRED_FILES:
            self.assertTrue((AUDIT / name).is_file(), name)
        self.assertTrue(INVENTORY.is_file())
        self.assertTrue(DOC.is_file())

    def test_report_and_inventory_parse(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "public_search_runtime_integration_audit_v0")
        self.assertEqual(inventory["status"], "audited")

    def test_classifications_are_valid_and_boundaries_hold(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        matrix = report["integration_status_matrix"]
        for value in matrix.values():
            self.assertIn(value, VALID_CLASSIFICATIONS)
        self.assertEqual(matrix["source_cache_dry_run"], "implemented_local_dry_run")
        self.assertEqual(matrix["evidence_ledger_dry_run"], "implemented_local_dry_run")
        self.assertEqual(matrix["connector_runtimes"], "approval_gated")
        self.assertEqual(matrix["ranking_runtime"], "planning_only")
        self.assertEqual(matrix["deep_extraction"], "contract_only")
        self.assertFalse(report["source_cache_dry_run_integrated_with_public_search"])
        self.assertFalse(report["evidence_ledger_dry_run_integrated_with_public_search"])
        self.assertFalse(report["connector_runtime_integrated_with_public_search"])
        self.assertFalse(report["page_runtime_integrated_with_public_search"])
        self.assertFalse(report["ranking_runtime_integrated_with_public_search"])
        self.assertFalse(report["explanation_runtime_integrated_with_public_search"])
        self.assertFalse(report["deep_extraction_runtime_integrated_with_public_search"])
        self.assertFalse(report["pack_import_runtime_integrated_with_public_search"])

    def test_mutation_and_public_search_change_booleans_false(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        for key in (
            "runtime_integration_implemented",
            "public_search_runtime_mutated",
            "public_search_routes_changed",
            "public_search_response_changed",
            "public_search_order_changed",
            "public_search_live_source_fanout_enabled",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "external_calls_performed",
            "live_source_called",
            "telemetry_enabled",
            "accounts_enabled",
            "uploads_enabled",
            "downloads_enabled",
            "installs_enabled",
            "execution_enabled",
            "deployment_performed",
        ):
            self.assertFalse(report[key], key)

    def test_command_matrix_and_docs_reference_validator(self):
        matrix_text = (ROOT / "control" / "inventory" / "tests" / "command_matrix.json").read_text(encoding="utf-8")
        registry_text = (ROOT / "control" / "inventory" / "tests" / "test_registry.json").read_text(encoding="utf-8")
        scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        for text in (matrix_text, registry_text, scripts_readme):
            self.assertIn("validate_public_search_runtime_integration_audit.py", text)
            self.assertIn("report_public_search_runtime_integration_status.py --json", text)
        doc_text = DOC.read_text(encoding="utf-8").lower()
        for phrase in (
            "audit-only",
            "source-cache dry-run",
            "evidence-ledger dry-run",
            "not integrated now",
            "mutation",
            "safety",
        ):
            self.assertIn(phrase, doc_text)


if __name__ == "__main__":
    unittest.main()
