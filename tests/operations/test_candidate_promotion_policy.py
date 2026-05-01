import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "query" / "candidate_promotion_assessment.v0.json"
POLICY = ROOT / "control" / "inventory" / "query_intelligence" / "candidate_promotion_policy.json"
REPORT = ROOT / "control" / "audits" / "candidate-promotion-policy-v0" / "candidate_promotion_policy_report.json"
EXAMPLES = ROOT / "examples" / "candidate_promotion"


class CandidatePromotionPolicyOperationsTests(unittest.TestCase):
    def test_schema_policy_report_and_examples_exist(self) -> None:
        self.assertTrue(CONTRACT.is_file())
        self.assertTrue(POLICY.is_file())
        self.assertTrue(REPORT.is_file())
        self.assertGreaterEqual(len([path for path in EXAMPLES.iterdir() if path.is_dir()]), 4)
        self.assertEqual(json.loads(CONTRACT.read_text(encoding="utf-8"))["x-status"], "contract_only")

    def test_policy_hard_false_and_required_true_flags(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        for key in (
            "runtime_promotion_implemented",
            "automatic_promotion_allowed",
            "candidate_promotion_runtime_implemented",
            "master_index_mutation_allowed",
            "source_registry_mutation_allowed",
            "source_cache_mutation_allowed",
            "evidence_ledger_mutation_allowed",
            "public_index_mutation_allowed",
            "local_index_mutation_allowed",
            "candidate_index_mutation_allowed",
            "public_search_candidate_injection_allowed",
            "telemetry_implemented",
            "public_query_logging_enabled",
            "destructive_merge_allowed",
        ):
            self.assertFalse(policy[key], key)
        for key in (
            "privacy_filter_required",
            "evidence_required_for_promotion_review",
            "provenance_required_for_promotion_review",
            "human_or_policy_review_required",
            "rights_risk_review_required",
            "conflict_review_required",
        ):
            self.assertTrue(policy[key], key)

    def test_example_hard_boundaries(self) -> None:
        for assessment_path in sorted(EXAMPLES.glob("*/CANDIDATE_PROMOTION_ASSESSMENT.json")):
            with self.subTest(path=assessment_path):
                payload = json.loads(assessment_path.read_text(encoding="utf-8"))
                self.assertFalse(payload["no_auto_promotion_guarantees"]["promotion_performed"])
                self.assertFalse(payload["no_auto_promotion_guarantees"]["accepted_as_truth"])
                self.assertFalse(payload["no_auto_promotion_guarantees"]["promoted_to_master_index"])
                self.assertFalse(payload["recommended_decision"]["automatic"])
                self.assertFalse(payload["review_requirements"]["promotion_allowed_now"])
                self.assertTrue(payload["confidence_assessment"]["confidence_not_truth"])
                self.assertFalse(payload["confidence_assessment"]["confidence_sufficient_for_promotion"])
                self.assertFalse(payload["source_policy_assessment"]["live_source_called"])
                self.assertFalse(payload["source_policy_assessment"]["live_probe_enabled"])
                self.assertFalse(payload["rights_and_risk_assessment"]["rights_clearance_claimed"])
                self.assertFalse(payload["rights_and_risk_assessment"]["malware_safety_claimed"])
                for field in ("master_index_mutated", "source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated"):
                    self.assertFalse(payload["no_mutation_guarantees"][field], field)
                for output in payload["future_outputs"]:
                    self.assertFalse(output["output_runtime_implemented"])

    def test_docs_state_contract_only_no_runtime_no_truth(self) -> None:
        text = (ROOT / "docs" / "reference" / "CANDIDATE_PROMOTION_POLICY.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "promotion policy is not promotion runtime",
            "candidate promotion runtime is not implemented",
            "candidate confidence is not truth",
            "automatic promotion is forbidden",
            "destructive merge is forbidden",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
