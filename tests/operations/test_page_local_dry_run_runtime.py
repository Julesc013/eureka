import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "object-source-comparison-page-local-dry-run-runtime-v0"
REPORT = AUDIT_DIR / "page_local_dry_run_runtime_report.json"
INVENTORY = REPO_ROOT / "control" / "inventory" / "pages" / "page_local_dry_run_runtime.json"
DOC = REPO_ROOT / "docs" / "operations" / "OBJECT_SOURCE_COMPARISON_PAGE_LOCAL_DRY_RUN_RUNTIME.md"
RUNTIME_DOC = REPO_ROOT / "runtime" / "pages" / "README.md"
COMMAND_MATRIX = REPO_ROOT / "control" / "inventory" / "tests" / "command_matrix.json"


REQUIRED_FILES = {
    "README.md",
    "IMPLEMENTATION_SUMMARY.md",
    "RUNTIME_SCOPE.md",
    "DRY_RUN_INPUT_MODEL.md",
    "DRY_RUN_OUTPUT_MODEL.md",
    "PAGE_RECORD_CLASSIFICATION.md",
    "RENDERING_MODEL.md",
    "HTML_TEXT_JSON_PREVIEW_MODEL.md",
    "PRIVACY_AND_PUBLIC_SAFETY_REVIEW.md",
    "ACTION_RIGHTS_AND_RISK_REVIEW.md",
    "SOURCE_EVIDENCE_CANDIDATE_BOUNDARY.md",
    "PUBLIC_SEARCH_BOUNDARY.md",
    "HOSTED_RUNTIME_BOUNDARY.md",
    "FAILURE_AND_ERROR_MODEL.md",
    "ACCEPTANCE_RESULTS.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "page_local_dry_run_runtime_report.json",
}


class PageLocalDryRunRuntimeOperationsTests(unittest.TestCase):
    def test_audit_pack_inventory_and_docs_exist(self) -> None:
        self.assertTrue(AUDIT_DIR.is_dir())
        present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertFalse(REQUIRED_FILES - present)
        self.assertTrue(INVENTORY.is_file())
        self.assertTrue(DOC.is_file())
        self.assertTrue(RUNTIME_DOC.is_file())

    def test_report_and_inventory_boundaries(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertTrue(report["local_dry_run_runtime_implemented"])
        for field in (
            "hosted_runtime_enabled",
            "public_routes_added",
            "api_routes_added",
            "public_search_runtime_mutated",
            "public_search_response_changed",
            "public_search_order_changed",
            "source_cache_read",
            "evidence_ledger_read",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "execution_enabled",
        ):
            self.assertFalse(report[field], field)
        self.assertEqual(inventory["status"], "implemented_local_dry_run")
        self.assertFalse(inventory["public_search_integration_enabled"])
        self.assertFalse(inventory["hosted_page_runtime_implemented"])
        self.assertFalse(inventory["source_cache_reads_enabled"])
        self.assertFalse(inventory["evidence_ledger_reads_enabled"])

    def test_docs_and_command_matrix_document_boundaries(self) -> None:
        text = DOC.read_text(encoding="utf-8").casefold()
        for phrase in (
            "local dry-run",
            "no public routes",
            "no hosted runtime",
            "no public search integration",
            "no source cache reads",
            "no evidence ledger reads",
            "no mutation",
            "downloads disabled",
        ):
            self.assertIn(phrase, text)
        matrix = COMMAND_MATRIX.read_text(encoding="utf-8")
        self.assertIn("page_local_dry_run_report_validator", matrix)
        self.assertIn("page_local_dry_run_json", matrix)


if __name__ == "__main__":
    unittest.main()
