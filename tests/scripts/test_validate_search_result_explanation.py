from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)


class SearchResultExplanationTestMixin:
    maxDiff = None

    def load(self, rel: str):
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))

    def sample(self):
        return self.load("examples/search_result_explanations/minimal_match_explanation_v0/SEARCH_RESULT_EXPLANATION.json")


class ValidateSearchResultExplanationTests(SearchResultExplanationTestMixin, unittest.TestCase):
    def test_validator_passes_and_json_parses(self):
        result = run_cmd("scripts/validate_search_result_explanation.py", "--all-examples")
        self.assertEqual(result.returncode, 0, result.stderr)
        result_json = run_cmd("scripts/validate_search_result_explanation.py", "--all-examples", "--json")
        self.assertEqual(result_json.returncode, 0, result_json.stderr)
        payload = json.loads(result_json.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["error_count"], 0)

    def test_hard_booleans_and_required_nested_values(self):
        explanation = self.sample()
        for key in [
            "runtime_explanation_implemented",
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
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "live_source_called",
            "external_calls_performed",
            "downloads_enabled",
            "installs_enabled",
            "execution_enabled",
            "telemetry_exported",
        ]:
            self.assertIs(explanation[key], False, key)
        self.assertIs(explanation["query_interpretation"]["raw_query_included"], False)
        self.assertIs(explanation["query_interpretation"]["interpretation_not_truth"], True)
        self.assertIs(explanation["match_and_recall"]["match_strength_not_truth"], True)
        self.assertIs(explanation["source_coverage"]["source_coverage_not_exhaustive"], True)
        self.assertIs(explanation["evidence_and_provenance"]["evidence_not_truth"], True)
        self.assertIs(explanation["evidence_and_provenance"]["provenance_not_truth"], True)
        self.assertIs(explanation["evidence_and_provenance"]["accepted_as_truth"], False)
        self.assertIs(explanation["identity_grouping_deduplication"]["conflicts_hidden"], False)
        self.assertIs(explanation["identity_grouping_deduplication"]["destructive_merge_performed"], False)
        self.assertIs(explanation["ranking_relationship"]["ranking_not_truth"], True)
        self.assertIs(explanation["compatibility"]["compatibility_not_truth"], True)
        self.assertIs(explanation["absence_near_miss_gaps"]["global_absence_claimed"], False)
        self.assertIs(explanation["absence_near_miss_gaps"]["absence_not_truth"], True)
        self.assertIs(explanation["rights_risk"]["rights_clearance_claimed"], False)
        self.assertIs(explanation["rights_risk"]["malware_safety_claimed"], False)
        self.assertIs(explanation["rights_risk"]["installability_claimed"], False)
        self.assertTrue(explanation["user_facing_summary"]["summary_text"])

    def assert_invalid(self, mutation):
        data = self.sample()
        mutation(data)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "SEARCH_RESULT_EXPLANATION.json"
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            result = run_cmd("scripts/validate_search_result_explanation.py", "--explanation", str(path))
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_negative_hard_boolean_mutations_fail(self):
        for key in [
            "runtime_explanation_implemented",
            "explanation_applied_to_live_search",
            "public_search_order_changed",
            "hidden_score_used",
            "result_suppressed",
            "model_call_performed",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "master_index_mutated",
        ]:
            self.assert_invalid(lambda data, key=key: data.__setitem__(key, True))

    def test_negative_nested_claims_fail(self):
        self.assert_invalid(lambda data: data["query_interpretation"].__setitem__("raw_query_included", True))
        self.assert_invalid(lambda data: data["rights_risk"].__setitem__("rights_clearance_claimed", True))
        self.assert_invalid(lambda data: data["rights_risk"].__setitem__("malware_safety_claimed", True))
        self.assert_invalid(lambda data: data["explained_result"].__setitem__("result_ref", "C:\\Users\\name\\secret"))


if __name__ == "__main__":
    unittest.main()
