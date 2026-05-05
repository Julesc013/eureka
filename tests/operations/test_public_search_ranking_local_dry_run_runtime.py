import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = ROOT / "control" / "audits" / "public-search-ranking-local-dry-run-runtime-v0"
REPORT = AUDIT_ROOT / "public_search_ranking_local_dry_run_runtime_report.json"
INVENTORY = ROOT / "control" / "inventory" / "search" / "public_search_ranking_local_dry_run_runtime.json"
DOCS = ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RANKING_LOCAL_DRY_RUN_RUNTIME.md"


class PublicSearchRankingLocalDryRunRuntimeOperationTests(unittest.TestCase):
    def test_audit_pack_inventory_docs_and_runtime_docs_exist(self):
        self.assertTrue(AUDIT_ROOT.exists())
        self.assertTrue(REPORT.exists())
        self.assertTrue(INVENTORY.exists())
        self.assertTrue(DOCS.exists())
        self.assertTrue((ROOT / "runtime" / "engine" / "ranking" / "README.md").exists())

    def test_report_and_inventory_make_no_integration_claims(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertTrue(report["local_dry_run_runtime_implemented"])
        self.assertFalse(report["public_search_ranking_runtime_enabled"])
        self.assertFalse(report["hosted_runtime_enabled"])
        self.assertFalse(report["hidden_scores_enabled"])
        self.assertFalse(report["result_suppression_enabled"])
        self.assertFalse(report["telemetry_signal_used"])
        self.assertFalse(report["model_call_performed"])
        self.assertFalse(report["source_cache_read"])
        self.assertFalse(report["evidence_ledger_read"])
        self.assertFalse(report["source_cache_mutated"])
        self.assertFalse(report["evidence_ledger_mutated"])
        self.assertFalse(report["downloads_enabled"])
        self.assertFalse(inventory["public_search_order_changed"])
        self.assertFalse(inventory["source_cache_reads_enabled"])
        self.assertFalse(inventory["evidence_ledger_reads_enabled"])

    def test_command_matrix_includes_new_commands(self):
        matrix = json.loads((ROOT / "control" / "inventory" / "tests" / "command_matrix.json").read_text(encoding="utf-8"))
        text = json.dumps(matrix)
        self.assertIn("public_search_ranking_dry_run_json", text)
        self.assertIn("public_search_ranking_dry_run_report_validator", text)
        self.assertIn("public_search_ranking_dry_run_report_validator_json", text)


if __name__ == "__main__":
    unittest.main()
