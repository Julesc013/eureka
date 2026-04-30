from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_ROOT = REPO_ROOT / "control" / "inventory" / "local_state"
MODEL = INVENTORY_ROOT / "local_quarantine_staging_model.json"
PATH_POLICY = INVENTORY_ROOT / "local_state_path_policy.json"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "local-quarantine-staging-model-v0"
AUDIT_REPORT = AUDIT_ROOT / "local_quarantine_staging_model_report.json"
GITIGNORE = REPO_ROOT / ".gitignore"
VALIDATOR = REPO_ROOT / "scripts" / "validate_local_quarantine_staging_model.py"


class LocalQuarantineStagingModelOperationTestCase(unittest.TestCase):
    def test_inventory_files_exist_and_parse(self) -> None:
        self.assertTrue((INVENTORY_ROOT / "README.md").exists())
        model = json.loads(MODEL.read_text(encoding="utf-8"))
        path_policy = json.loads(PATH_POLICY.read_text(encoding="utf-8"))
        self.assertEqual(model["status"], "planning_only")
        self.assertFalse(model["staging_runtime_implemented"])
        self.assertEqual(model["default_visibility"], "local_private")
        self.assertEqual(model["default_search_impact"], "none")
        self.assertEqual(model["default_master_index_impact"], "none")
        self.assertFalse(model["default_telemetry_enabled"])
        self.assertEqual(path_policy["suggested_dev_root"], ".eureka-local/")
        self.assertIn("site/dist", path_policy["prohibited_roots"])
        self.assertIn("external", path_policy["prohibited_roots"])
        self.assertIn("runtime", path_policy["prohibited_roots"])
        self.assertIn("snapshots/examples committed examples", path_policy["prohibited_roots"])
        self.assertIn("docs", path_policy["prohibited_roots"])

    def test_audit_pack_exists_and_records_planning_only(self) -> None:
        required = {
            "README.md",
            "MODEL_SUMMARY.md",
            "PATH_POLICY.md",
            "STAGED_ENTITY_MODEL.md",
            "PROVENANCE_AND_REPORT_LINKING.md",
            "PRIVACY_RIGHTS_RISK_POLICY.md",
            "RESET_DELETE_EXPORT_MODEL.md",
            "LOCAL_SEARCH_AND_INDEX_IMPACT.md",
            "NATIVE_RELAY_SNAPSHOT_IMPACT.md",
            "MASTER_INDEX_IMPACT.md",
            "IMPLEMENTATION_BOUNDARIES.md",
            "FUTURE_IMPLEMENTATION_SEQUENCE.md",
            "RISKS_AND_LIMITATIONS.md",
            "NEXT_STEPS.md",
            "local_quarantine_staging_model_report.json",
        }
        self.assertTrue(AUDIT_ROOT.exists())
        self.assertTrue(required.issubset({path.name for path in AUDIT_ROOT.iterdir()}))
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "planning_only")
        self.assertFalse(report["staging_runtime_implemented"])
        self.assertEqual(report["default_visibility"], "local_private")
        self.assertEqual(report["default_search_impact"], "none")
        self.assertEqual(report["default_master_index_impact"], "none")
        self.assertIn("delete_staged_pack", report["required_future_operations"])
        self.assertIn("export_staging_report_only", report["required_future_operations"])

    def test_gitignore_blocks_future_local_state_roots_without_creating_them(self) -> None:
        text = GITIGNORE.read_text(encoding="utf-8")
        for entry in [".eureka-local/", ".eureka-cache/", ".eureka-staging/"]:
            self.assertIn(entry, text)
            self.assertFalse((REPO_ROOT / entry.rstrip("/")).exists())

    def test_docs_record_no_staging_runtime_and_no_impact(self) -> None:
        docs = [
            REPO_ROOT / "docs" / "architecture" / "LOCAL_QUARANTINE_STAGING_MODEL.md",
            REPO_ROOT / "docs" / "reference" / "LOCAL_STAGING_PATH_POLICY.md",
            REPO_ROOT / "docs" / "reference" / "LOCAL_CACHE_PRIVACY_POLICY.md",
            REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md",
            REPO_ROOT / "docs" / "operations" / "VALIDATE_ONLY_PACK_IMPORT.md",
        ]
        for path in docs:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("no staging runtime exists", text)
                self.assertIn("does not create", text)
                self.assertIn("does not import", text)
                self.assertIn("does not stage", text)
                self.assertIn("does not index", text)
                self.assertIn("does not upload", text)
                self.assertIn("does not mutate", text)
                self.assertIn("public search", text)
                self.assertIn("master index", text)

    def test_no_runtime_staging_tool_added(self) -> None:
        self.assertTrue(VALIDATOR.exists())
        suspicious_scripts = [
            path.name
            for path in (REPO_ROOT / "scripts").glob("*staging*.py")
            if path.name != "validate_local_quarantine_staging_model.py"
        ]
        self.assertEqual(suspicious_scripts, [])


if __name__ == "__main__":
    unittest.main()
