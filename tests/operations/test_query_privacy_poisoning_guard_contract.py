import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "query" / "query_guard_decision.v0.json"
PRIVACY_RISK = ROOT / "contracts" / "query" / "query_privacy_risk.v0.json"
POISONING_RISK = ROOT / "contracts" / "query" / "query_poisoning_risk.v0.json"
POLICY = ROOT / "control" / "inventory" / "query_intelligence" / "query_privacy_poisoning_guard_policy.json"
REPORT = ROOT / "control" / "audits" / "query-privacy-poisoning-guard-v0" / "query_privacy_poisoning_guard_report.json"
EXAMPLES = ROOT / "examples" / "query_guard"


class QueryPrivacyPoisoningGuardOperationsTests(unittest.TestCase):
    def test_schema_policy_report_and_examples_exist(self) -> None:
        self.assertTrue(CONTRACT.is_file())
        self.assertTrue(PRIVACY_RISK.is_file())
        self.assertTrue(POISONING_RISK.is_file())
        self.assertTrue(POLICY.is_file())
        self.assertTrue(REPORT.is_file())
        self.assertGreaterEqual(len([path for path in EXAMPLES.iterdir() if path.is_dir()]), 5)
        self.assertEqual(json.loads(CONTRACT.read_text(encoding="utf-8"))["x-status"], "contract_only")

    def test_policy_hard_flags(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        for key in (
            "runtime_guard_implemented",
            "persistent_guard_store_implemented",
            "telemetry_implemented",
            "account_tracking_implemented",
            "ip_tracking_implemented",
            "public_query_logging_enabled",
            "automatic_acceptance_allowed",
            "query_observation_mutation_allowed",
            "result_cache_mutation_allowed",
            "miss_ledger_mutation_allowed",
            "search_need_mutation_allowed",
            "probe_queue_mutation_allowed",
            "candidate_index_mutation_allowed",
            "known_absence_mutation_allowed",
            "public_index_mutation_allowed",
            "local_index_mutation_allowed",
            "master_index_mutation_allowed",
            "high_privacy_risk_public_aggregate_allowed",
            "high_poisoning_risk_public_aggregate_allowed",
        ):
            self.assertFalse(policy[key], key)
        self.assertEqual(policy["raw_query_retention_default"], "none")
        self.assertTrue(policy["privacy_filter_required"])
        self.assertTrue(policy["poisoning_guard_required_before_public_aggregation"])

    def test_example_boundaries(self) -> None:
        for decision_path in sorted(EXAMPLES.glob("*/QUERY_GUARD_DECISION.json")):
            with self.subTest(path=decision_path):
                payload = json.loads(decision_path.read_text(encoding="utf-8"))
                self.assertFalse(payload["input_context"]["raw_query_retained"])
                self.assertEqual(payload["retention_policy"]["raw_query_retention"], "none")
                self.assertFalse(payload["review_requirements"]["automatic_acceptance_allowed"])
                for field in (
                    "runtime_guard_implemented",
                    "persistent_guard_store_implemented",
                    "telemetry_exported",
                    "account_tracking_performed",
                    "ip_tracking_performed",
                    "public_query_logging_enabled",
                ):
                    self.assertFalse(payload["no_runtime_guarantees"][field], field)
                for field in (
                    "query_observation_mutated",
                    "result_cache_mutated",
                    "miss_ledger_mutated",
                    "search_need_mutated",
                    "probe_queue_mutated",
                    "candidate_index_mutated",
                    "known_absence_mutated",
                    "public_index_mutated",
                    "local_index_mutated",
                    "master_index_mutated",
                    "external_calls_performed",
                    "live_source_called",
                ):
                    self.assertFalse(payload["no_mutation_guarantees"][field], field)

    def test_risky_examples_block_aggregate(self) -> None:
        for name in (
            "minimal_private_path_rejected_v0",
            "minimal_secret_rejected_v0",
            "minimal_source_stuffing_quarantined_v0",
            "minimal_fake_demand_throttled_v0",
        ):
            payload = json.loads((EXAMPLES / name / "QUERY_GUARD_DECISION.json").read_text(encoding="utf-8"))
            self.assertFalse(payload["aggregate_eligibility"]["public_aggregate_allowed"], name)
            self.assertFalse(payload["query_intelligence_eligibility"]["public_aggregate_allowed"], name)

    def test_docs_state_contract_only_no_runtime_no_mutation(self) -> None:
        text = (ROOT / "docs" / "reference" / "QUERY_PRIVACY_POISONING_GUARD_CONTRACT.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "guard is not runtime yet",
            "guard is not telemetry",
            "guard is not waf",
            "raw query retention default none",
            "aggregate eligibility",
            "automatic acceptance is forbidden",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
