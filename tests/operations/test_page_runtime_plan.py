import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "object-source-comparison-page-runtime-planning-v0"


class PageRuntimePlanOperationTests(unittest.TestCase):
    def test_report_and_inventory_parse(self):
        report = json.loads((AUDIT / "object_source_comparison_page_runtime_planning_report.json").read_text(encoding="utf-8"))
        inventory = json.loads((ROOT / "control" / "inventory" / "pages" / "page_runtime_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(report["readiness_decision"], "ready_for_local_dry_run_runtime_after_operator_approval")
        self.assertEqual(inventory["status"], "planning_only")

    def test_hard_booleans_false(self):
        report = json.loads((AUDIT / "object_source_comparison_page_runtime_planning_report.json").read_text(encoding="utf-8"))
        for key in (
            "runtime_page_implementation_enabled",
            "object_page_runtime_implemented",
            "source_page_runtime_implemented",
            "comparison_page_runtime_implemented",
            "persistent_page_store_implemented",
            "public_search_runtime_mutated",
            "public_search_page_links_enabled_now",
            "hosted_page_runtime_verified",
            "live_source_calls_enabled",
            "external_calls_performed",
            "arbitrary_url_fetch_enabled",
            "local_path_access_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "execution_enabled",
            "telemetry_enabled",
            "accounts_enabled",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "candidate_promotion_performed",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
        ):
            self.assertFalse(report[key], key)

    def test_required_docs_and_boundaries(self):
        for name in (
            "ROUTING_AND_IDENTIFIER_POLICY.md",
            "RUNTIME_BOUNDARY.md",
            "DATA_INPUT_MODEL.md",
            "STATIC_AND_LITE_FALLBACK_MODEL.md",
            "ACCEPTANCE_CRITERIA.md",
            "DO_NOT_IMPLEMENT_YET.md",
        ):
            self.assertTrue((AUDIT / name).exists(), name)
        do_not = (AUDIT / "DO_NOT_IMPLEMENT_YET.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "no runtime page routes",
            "no object/source/comparison runtime renderer",
            "no database tables",
            "no persistent page store",
            "no public search mutation",
            "no live source calls",
            "no source cache writes",
            "no evidence ledger writes",
            "no candidate promotion",
            "no public/master index mutation",
            "no downloads/installers/execution",
            "no telemetry/accounts",
        ):
            self.assertIn(phrase, do_not)

    def test_gates_present_in_report(self):
        report = json.loads((AUDIT / "object_source_comparison_page_runtime_planning_report.json").read_text(encoding="utf-8"))
        gate = report["page_contract_gate_review"]
        self.assertTrue(gate["object_page_contract_valid"])
        self.assertTrue(gate["source_page_contract_valid"])
        self.assertTrue(gate["comparison_page_contract_valid"])
        search = report["public_search_index_gate_review"]
        self.assertTrue(search["public_search_contract_valid"])
        self.assertTrue(search["public_index_format_valid"])
        self.assertTrue(search["blocked_request_safety_valid"])
        self.assertFalse(search["page_links_enabled_now"])
        hosted = report["hosted_deployment_gate_review"]
        self.assertFalse(hosted["hosted_backend_verified"])
        self.assertFalse(hosted["hosted_page_runtime_immediate_next_step"])


if __name__ == "__main__":
    unittest.main()
