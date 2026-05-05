import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "public-search-ranking-runtime-planning-v0"


class PublicSearchRankingRuntimePlanOperationTests(unittest.TestCase):
    def test_report_and_inventory_parse(self):
        report = json.loads((AUDIT / "public_search_ranking_runtime_planning_report.json").read_text(encoding="utf-8"))
        inventory = json.loads((ROOT / "control" / "inventory" / "search" / "public_search_ranking_runtime_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(report["readiness_decision"], "ready_for_local_dry_run_runtime_after_operator_approval")
        self.assertEqual(inventory["status"], "planning_only")

    def test_hard_booleans_false(self):
        report = json.loads((AUDIT / "public_search_ranking_runtime_planning_report.json").read_text(encoding="utf-8"))
        for key in (
            "runtime_ranking_implemented",
            "public_search_ranking_enabled",
            "public_search_order_changed",
            "public_search_response_changed",
            "persistent_ranking_store_implemented",
            "ranking_applied_to_live_search",
            "hidden_scores_enabled",
            "result_suppression_enabled",
            "telemetry_signal_enabled",
            "popularity_signal_enabled",
            "user_profile_signal_enabled",
            "ad_signal_enabled",
            "model_call_enabled",
            "live_source_calls_enabled",
            "external_calls_performed",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "candidate_promotion_performed",
        ):
            self.assertFalse(report[key], key)

    def test_required_docs_and_boundaries(self):
        for name in (
            "RANKING_CONTRACT_GATE_REVIEW.md",
            "PUBLIC_SEARCH_AND_INDEX_GATE_REVIEW.md",
            "EVAL_AND_BASELINE_GATE_REVIEW.md",
            "HOSTED_DEPLOYMENT_GATE_REVIEW.md",
            "PRIVACY_NO_TELEMETRY_AND_NO_HIDDEN_SCORE_POLICY.md",
            "EVAL_AND_REGRESSION_PLAN.md",
            "ACCEPTANCE_CRITERIA.md",
            "DO_NOT_IMPLEMENT_YET.md",
        ):
            self.assertTrue((AUDIT / name).exists(), name)
        do_not = (AUDIT / "DO_NOT_IMPLEMENT_YET.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "no runtime ranking",
            "no public search order change",
            "no public search response change",
            "no hidden scores",
            "no result suppression",
            "no ai/model calls",
            "no telemetry",
            "no public/local/master index mutation",
            "no live source calls",
            "no deployment",
        ):
            self.assertIn(phrase, do_not)

    def test_gates_present_in_report(self):
        report = json.loads((AUDIT / "public_search_ranking_runtime_planning_report.json").read_text(encoding="utf-8"))
        gate = report["ranking_contract_gate_review"]
        self.assertEqual(gate["evidence_weighted_ranking_contract_status"], "valid")
        self.assertEqual(gate["compatibility_aware_ranking_contract_status"], "valid")
        self.assertEqual(gate["result_merge_deduplication_contract_status"], "valid")
        self.assertEqual(gate["identity_resolution_contract_status"], "valid")
        self.assertEqual(gate["search_result_explanation_contract_status"], "valid")
        public = report["public_search_index_gate_review"]
        self.assertEqual(public["public_search_safety_status"], "valid")
        self.assertEqual(public["public_index_format_status"], "valid")
        eval_gate = report["eval_baseline_gate_review"]
        self.assertFalse(eval_gate["production_quality_claims_eligible"])
        self.assertFalse(eval_gate["ranking_regression_tests_sufficient"])
        hosted = report["hosted_deployment_gate_review"]
        self.assertFalse(hosted["hosted_backend_verified"])
        self.assertFalse(hosted["hosted_ranking_runtime_immediate_next_step"])


if __name__ == "__main__":
    unittest.main()
