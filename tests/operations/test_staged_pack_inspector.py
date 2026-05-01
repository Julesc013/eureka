from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
INSPECTOR = REPO_ROOT / "scripts" / "inspect_staged_pack.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_staged_pack_inspector.py"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "staged-pack-inspector-v0"
AUDIT_REPORT = AUDIT_ROOT / "staged_pack_inspector_report.json"
DOC = REPO_ROOT / "docs" / "operations" / "STAGED_PACK_INSPECTION.md"


class StagedPackInspectorOperationTestCase(unittest.TestCase):
    def test_scripts_exist(self) -> None:
        self.assertTrue(INSPECTOR.exists())
        self.assertTrue(VALIDATOR.exists())

    def test_audit_pack_records_read_only_no_mutation_posture(self) -> None:
        required = {
            "README.md",
            "INSPECTOR_SUMMARY.md",
            "COMMAND_USAGE.md",
            "JSON_OUTPUT_MODEL.md",
            "HUMAN_OUTPUT_MODEL.md",
            "REDACTION_REVIEW.md",
            "NO_MUTATION_REVIEW.md",
            "EXAMPLE_INSPECTION_RESULTS.md",
            "FUTURE_STAGING_TOOL_IMPACT.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_STEPS.md",
            "staged_pack_inspector_report.json",
        }
        self.assertTrue(AUDIT_ROOT.exists())
        self.assertTrue(required.issubset({path.name for path in AUDIT_ROOT.iterdir()}))
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "implemented_read_only")
        for field in [
            "staging_runtime_implemented",
            "staging_performed",
            "import_performed",
            "indexing_performed",
            "upload_performed",
            "runtime_mutation_performed",
            "master_index_mutation_performed",
            "network_performed",
            "model_calls_performed",
        ]:
            self.assertFalse(report[field], field)

    def test_docs_say_no_staging_import_index_or_master_mutation(self) -> None:
        docs = [
            DOC,
            REPO_ROOT / "docs" / "reference" / "LOCAL_STAGING_MANIFEST_FORMAT.md",
            REPO_ROOT / "docs" / "architecture" / "LOCAL_QUARANTINE_STAGING_MODEL.md",
            REPO_ROOT / "docs" / "reference" / "LOCAL_STAGING_PATH_POLICY.md",
            REPO_ROOT / "docs" / "reference" / "STAGING_REPORT_PATH_CONTRACT.md",
            REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md",
        ]
        for path in docs:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("read-only", text)
                self.assertIn("no staging runtime", text)
                self.assertIn("does not stage", text)
                self.assertIn("does not import", text)
                self.assertIn("does not index", text)
                self.assertIn("public search", text)
                self.assertIn("local index", text)
                self.assertIn("master index", text)

    def test_no_local_runtime_state_directory_created(self) -> None:
        for root in [".eureka-local", ".eureka-cache", ".eureka-staging", ".eureka-reports"]:
            self.assertFalse((REPO_ROOT / root).exists())


if __name__ == "__main__":
    unittest.main()
