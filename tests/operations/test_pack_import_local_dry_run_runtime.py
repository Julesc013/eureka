import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "pack-import-local-dry-run-runtime-v0"
REPORT = AUDIT_DIR / "pack_import_local_dry_run_runtime_report.json"
INVENTORY = REPO_ROOT / "control" / "inventory" / "packs" / "pack_import_local_dry_run_runtime.json"
DOCS = REPO_ROOT / "docs" / "operations" / "PACK_IMPORT_LOCAL_DRY_RUN_RUNTIME.md"
RUNTIME_DOCS = REPO_ROOT / "runtime" / "packs" / "README.md"


class PackImportLocalDryRunRuntimeOperationsTests(unittest.TestCase):
    def test_audit_pack_inventory_and_docs_exist(self):
        self.assertTrue(AUDIT_DIR.is_dir())
        for name in [
            "README.md",
            "RUNTIME_SCOPE.md",
            "DRY_RUN_INPUT_MODEL.md",
            "DRY_RUN_OUTPUT_MODEL.md",
            "PACK_DISCOVERY_AND_CLASSIFICATION.md",
            "VALIDATION_PIPELINE_IMPLEMENTATION.md",
            "MUTATION_AND_PROMOTION_BOUNDARY.md",
            "PUBLIC_CONTRIBUTION_BOUNDARY.md",
            "COMMAND_RESULTS.md",
            "pack_import_local_dry_run_runtime_report.json",
        ]:
            self.assertTrue((AUDIT_DIR / name).is_file(), name)
        self.assertTrue(INVENTORY.is_file())
        self.assertTrue(DOCS.is_file())
        self.assertTrue(RUNTIME_DOCS.is_file())

    def test_report_and_inventory_boundaries(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertTrue(report["local_dry_run_runtime_implemented"])
        for field in [
            "authoritative_pack_import_runtime_implemented",
            "real_pack_staging_performed",
            "quarantine_store_written",
            "staging_store_written",
            "promotion_decision_created",
            "accepted_record_created",
            "public_contribution_intake_enabled",
            "upload_endpoint_enabled",
            "admin_endpoint_enabled",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "master_index_mutated",
        ]:
            self.assertFalse(report[field], field)
        self.assertFalse(inventory["authoritative_pack_import_runtime_implemented"])
        self.assertFalse(inventory["quarantine_runtime_enabled"])
        self.assertFalse(inventory["staging_runtime_enabled"])
        self.assertFalse(inventory["promotion_runtime_enabled"])
        self.assertFalse(inventory["public_contribution_intake_enabled"])

    def test_command_matrix_includes_new_commands(self):
        matrix_text = (REPO_ROOT / "control" / "inventory" / "tests" / "command_matrix.json").read_text(
            encoding="utf-8"
        )
        self.assertIn("pack_import_local_dry_run_json", matrix_text)
        self.assertIn("pack_import_local_dry_run_no_validators_json", matrix_text)
        self.assertIn("pack_import_dry_run_report_validator", matrix_text)
        self.assertIn("pack_import_dry_run_report_validator_json", matrix_text)


if __name__ == "__main__":
    unittest.main()
