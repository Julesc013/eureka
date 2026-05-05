from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class SearchResultExplanationContractOperationTests(unittest.TestCase):
    def load(self, rel: str):
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))

    def test_required_audit_pack_files_exist(self):
        audit = ROOT / "control/audits/search-result-explanation-contract-v0"
        required = [
            "README.md",
            "CONTRACT_SUMMARY.md",
            "SEARCH_RESULT_EXPLANATION_SCHEMA.md",
            "EXPLANATION_COMPONENT_TAXONOMY.md",
            "QUERY_INTERPRETATION_EXPLANATION_MODEL.md",
            "MATCH_AND_RECALL_EXPLANATION_MODEL.md",
            "SOURCE_COVERAGE_EXPLANATION_MODEL.md",
            "EVIDENCE_AND_PROVENANCE_EXPLANATION_MODEL.md",
            "IDENTITY_GROUPING_AND_DEDUPLICATION_EXPLANATION_MODEL.md",
            "RANKING_EXPLANATION_RELATIONSHIP.md",
            "COMPATIBILITY_EXPLANATION_MODEL.md",
            "ABSENCE_NEAR_MISS_AND_GAP_EXPLANATION_MODEL.md",
            "ACTION_SAFETY_EXPLANATION_MODEL.md",
            "RIGHTS_RISK_CAUTION_MODEL.md",
            "USER_FACING_COPY_POLICY.md",
            "API_STATIC_LITE_TEXT_PROJECTION.md",
            "PRIVACY_AND_REDACTION_POLICY.md",
            "NO_HIDDEN_SCORE_NO_TRUTH_NO_RUNTIME_NO_MUTATION_POLICY.md",
            "INTEGRATION_BOUNDARIES.md",
            "EXAMPLE_SEARCH_RESULT_EXPLANATION_REVIEW.md",
            "FUTURE_RUNTIME_PATH.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "search_result_explanation_contract_report.json",
        ]
        for name in required:
            self.assertTrue((audit / name).exists(), name)

    def test_docs_say_contract_only_no_runtime_no_hidden_score_no_mutation(self):
        docs = [
            ROOT / "docs/reference/SEARCH_RESULT_EXPLANATION_CONTRACT.md",
            ROOT / "control/audits/search-result-explanation-contract-v0/NO_HIDDEN_SCORE_NO_TRUTH_NO_RUNTIME_NO_MUTATION_POLICY.md",
            ROOT / "control/audits/search-result-explanation-contract-v0/USER_FACING_COPY_POLICY.md",
        ]
        lowered = "\n".join(path.read_text(encoding="utf-8").lower() for path in docs)
        for phrase in ["contract-only", "no runtime", "no hidden score", "no suppression", "no ai answer", "no mutation"]:
            self.assertIn(phrase, lowered)

    def test_report_and_inventory_hard_booleans_false(self):
        report = self.load("control/audits/search-result-explanation-contract-v0/search_result_explanation_contract_report.json")
        for key, value in report.items():
            if key.endswith("_implemented") or key.endswith("_mutated") or key in {
                "persistent_explanation_store_implemented",
                "explanation_generated_by_runtime",
                "explanation_applied_to_live_search",
                "public_search_response_changed",
                "public_search_order_changed",
                "hidden_score_used",
                "hidden_suppression_performed",
                "result_suppressed",
                "model_call_performed",
                "AI_generated_answer",
                "candidate_promotion_performed",
                "ranking_applied_to_live_search",
                "live_source_called",
                "external_calls_performed",
                "downloads_enabled",
                "installs_enabled",
                "execution_enabled",
                "telemetry_enabled",
                "rights_clearance_claimed",
                "malware_safety_claimed",
                "installability_claimed",
            }:
                self.assertIs(value, False, key)
        inventory = self.load("control/inventory/search/search_result_explanation_policy.json")
        self.assertEqual(inventory["status"], "contract_only")
        for key in [
            "runtime_explanation_implemented",
            "persistent_explanation_store_implemented",
            "explanation_applied_to_live_search",
            "public_search_response_changed",
            "public_search_order_changed",
            "hidden_scores_allowed",
            "hidden_suppression_allowed",
            "model_calls_allowed",
            "AI_answer_generation_allowed",
            "telemetry_enabled",
            "candidate_promotion_allowed",
            "source_cache_mutation_allowed",
            "evidence_ledger_mutation_allowed",
            "master_index_mutation_allowed",
            "raw_query_in_explanation_allowed",
            "private_data_in_public_explanation_allowed",
            "rights_clearance_claim_allowed",
            "malware_safety_claim_allowed",
        ]:
            self.assertIs(inventory[key], False, key)


if __name__ == "__main__":
    unittest.main()
