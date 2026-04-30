from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = REPO_ROOT / "scripts" / "validate_only_pack_import.py"
DOC = REPO_ROOT / "docs" / "operations" / "VALIDATE_ONLY_PACK_IMPORT.md"
PACK_VALIDATION_DOC = REPO_ROOT / "docs" / "operations" / "PACK_VALIDATION.md"
IMPORT_REPORT_DOC = REPO_ROOT / "docs" / "reference" / "PACK_IMPORT_REPORT_FORMAT.md"
IMPORT_PLANNING_DOC = REPO_ROOT / "docs" / "reference" / "PACK_IMPORT_PLANNING.md"
IMPORT_PIPELINE_DOC = REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "validate-only-pack-import-tool-v0"
AUDIT_REPORT = AUDIT_ROOT / "validate_only_pack_import_tool_report.json"
TEST_REGISTRY = REPO_ROOT / "control" / "inventory" / "tests" / "test_registry.json"
COMMAND_MATRIX = REPO_ROOT / "control" / "inventory" / "tests" / "command_matrix.json"


class ValidateOnlyPackImportToolOperationTestCase(unittest.TestCase):
    def test_tool_exists_and_is_validate_only(self) -> None:
        self.assertTrue(TOOL.exists())
        text = TOOL.read_text(encoding="utf-8")
        self.assertIn("validate_only_pack_import_tool_v0", text)
        self.assertIn("validate_pack_set.validate_pack_root", text)
        self.assertIn("network_performed", text)
        self.assertNotIn("requests.", text)
        self.assertNotIn("urllib.request", text)

    def test_docs_record_report_generation_and_boundaries(self) -> None:
        for path in [DOC, PACK_VALIDATION_DOC, IMPORT_REPORT_DOC, IMPORT_PLANNING_DOC, IMPORT_PIPELINE_DOC]:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("validate-only pack import tool v0", text)
                self.assertIn("pack import report v0", text)
                self.assertIn("does not import", text)
                self.assertIn("does not stage", text)
                self.assertIn("does not index", text)
                self.assertIn("does not upload", text)
                self.assertIn("does not mutate", text)
                self.assertIn("master index", text)

    def test_audit_pack_records_no_mutation_tooling(self) -> None:
        required = {
            "README.md",
            "TOOL_SUMMARY.md",
            "COMMAND_USAGE.md",
            "REPORT_GENERATION_MODEL.md",
            "SAFETY_AND_NO_MUTATION_REVIEW.md",
            "EXAMPLE_RUN_RESULTS.md",
            "RELATION_TO_IMPORT_PIPELINE.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_STEPS.md",
            "validate_only_pack_import_tool_report.json",
        }
        self.assertTrue(AUDIT_ROOT.exists())
        self.assertTrue(required.issubset({path.name for path in AUDIT_ROOT.iterdir()}))
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "implemented_validate_only")
        self.assertTrue(report["validate_only_tool_implemented"])
        self.assertFalse(report["import_runtime_implemented"])
        self.assertFalse(report["staging_implemented"])
        self.assertFalse(report["indexing_implemented"])
        self.assertFalse(report["upload_implemented"])
        self.assertFalse(report["runtime_mutation_implemented"])
        self.assertFalse(report["master_index_mutation_implemented"])
        self.assertFalse(report["network_calls_performed"])
        self.assertFalse(report["model_calls_performed"])
        self.assertEqual(report["example_run_summary"]["report_status"], "validate_only_passed")

    def test_test_registry_and_command_matrix_include_tool(self) -> None:
        registry = json.loads(TEST_REGISTRY.read_text(encoding="utf-8"))
        matrix = json.loads(COMMAND_MATRIX.read_text(encoding="utf-8"))
        registry_text = json.dumps(registry)
        matrix_text = json.dumps(matrix)
        self.assertIn("validate-only-pack-import-tool-v0", registry_text)
        self.assertIn("scripts/validate_only_pack_import.py", registry_text)
        self.assertIn("validate-only-pack-import-tool-v0", matrix_text)
        self.assertIn("validate_only_pack_import_tool_examples", matrix_text)
        self.assertIn("validate_only_pack_import_tool_tests", matrix_text)


if __name__ == "__main__":
    unittest.main()
