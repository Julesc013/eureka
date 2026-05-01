from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "control" / "inventory" / "local_state" / "staging_report_path_contract.json"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "staging-report-path-contract-v0"
AUDIT_REPORT = AUDIT_ROOT / "staging_report_path_contract_report.json"
GITIGNORE = REPO_ROOT / ".gitignore"
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "STAGING_REPORT_PATH_CONTRACT.md"
OPERATIONS_DOC = REPO_ROOT / "docs" / "operations" / "LOCAL_REPORT_PATHS.md"
VALIDATE_ONLY_DOC = REPO_ROOT / "docs" / "operations" / "VALIDATE_ONLY_PACK_IMPORT.md"
VALIDATE_ONLY_TOOL = REPO_ROOT / "scripts" / "validate_only_pack_import.py"


class StagingReportPathContractOperationTestCase(unittest.TestCase):
    def test_inventory_exists_and_records_stdout_default(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "planning_only")
        self.assertFalse(contract["report_path_runtime_implemented"])
        self.assertFalse(contract["staging_runtime_implemented"])
        self.assertEqual(contract["default_output_mode"], "stdout")
        self.assertTrue(contract["explicit_output_required_for_file_write"])
        self.assertFalse(contract["auto_create_parent_directories_default"])
        self.assertTrue(contract["local_private_by_default"])
        roots = "\n".join(contract["committed_report_roots_forbidden"])
        for marker in ["site/dist", "external", "runtime", "control/inventory", "contracts", "snapshots/examples", "docs"]:
            self.assertIn(marker, roots)

    def test_audit_pack_exists_and_records_no_runtime(self) -> None:
        required = {
            "README.md",
            "CONTRACT_SUMMARY.md",
            "ALLOWED_AND_FORBIDDEN_ROOTS.md",
            "FILENAME_POLICY.md",
            "REDACTION_POLICY.md",
            "TOOL_BEHAVIOR_POLICY.md",
            "GITIGNORE_REVIEW.md",
            "NATIVE_RELAY_SNAPSHOT_IMPACT.md",
            "PUBLIC_SEARCH_AND_MASTER_INDEX_IMPACT.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_STEPS.md",
            "staging_report_path_contract_report.json",
        }
        self.assertTrue(AUDIT_ROOT.exists())
        self.assertTrue(required.issubset({path.name for path in AUDIT_ROOT.iterdir()}))
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "planning_only")
        self.assertEqual(report["default_output_mode"], "stdout")
        self.assertFalse(report["report_path_runtime_implemented"])
        self.assertFalse(report["staging_runtime_implemented"])
        self.assertEqual(report["next_recommended_milestone"], "Local Staging Manifest Format v0")

    def test_gitignore_blocks_future_report_roots_without_creating_them(self) -> None:
        text = GITIGNORE.read_text(encoding="utf-8")
        for entry in [".eureka-local/", ".eureka-cache/", ".eureka-staging/", ".eureka-reports/"]:
            self.assertIn(entry, text)
            self.assertFalse((REPO_ROOT / entry.rstrip("/")).exists())

    def test_docs_record_redaction_and_no_impact(self) -> None:
        for path in [REFERENCE_DOC, OPERATIONS_DOC, VALIDATE_ONLY_DOC]:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("stdout", text)
                self.assertIn("explicit output", text)
                self.assertIn("redact", text)
                self.assertIn("public search", text)
                self.assertIn("master index", text)
                self.assertIn("no staging runtime exists", text)

    def test_validate_only_tool_rejects_forbidden_output_roots(self) -> None:
        text = VALIDATE_ONLY_TOOL.read_text(encoding="utf-8")
        self.assertIn("FORBIDDEN_OUTPUT_REPO_ROOTS", text)
        self.assertIn("site/dist", text)
        self.assertIn("control/inventory", text)
        self.assertIn("_output_path_policy_error", text)


if __name__ == "__main__":
    unittest.main()
