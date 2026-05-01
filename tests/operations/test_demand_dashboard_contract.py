import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "query" / "demand_dashboard_snapshot.v0.json"
SIGNAL_CONTRACT = ROOT / "contracts" / "query" / "demand_signal.v0.json"
POLICY = ROOT / "control" / "inventory" / "query_intelligence" / "demand_dashboard_policy.json"
REPORT = ROOT / "control" / "audits" / "demand-dashboard-v0" / "demand_dashboard_report.json"
EXAMPLES = ROOT / "examples" / "demand_dashboard"


class DemandDashboardOperationsTests(unittest.TestCase):
    def test_schema_policy_report_and_examples_exist(self) -> None:
        self.assertTrue(CONTRACT.is_file())
        self.assertTrue(SIGNAL_CONTRACT.is_file())
        self.assertTrue(POLICY.is_file())
        self.assertTrue(REPORT.is_file())
        self.assertGreaterEqual(len([path for path in EXAMPLES.iterdir() if path.is_dir()]), 2)
        self.assertEqual(json.loads(CONTRACT.read_text(encoding="utf-8"))["x-status"], "contract_only")

    def test_policy_hard_flags(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        for key in (
            "runtime_dashboard_implemented",
            "persistent_dashboard_store_implemented",
            "telemetry_implemented",
            "account_tracking_implemented",
            "ip_tracking_implemented",
            "public_query_logging_enabled",
            "high_privacy_risk_public_aggregate_allowed",
            "high_poisoning_risk_public_aggregate_allowed",
            "real_user_demand_claimed",
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
        ):
            self.assertFalse(policy[key], key)
        self.assertEqual(policy["raw_query_retention_default"], "none")
        self.assertTrue(policy["privacy_filter_required"])
        self.assertTrue(policy["poisoning_guard_required_before_aggregation"])

    def test_example_boundaries(self) -> None:
        for snapshot_path in sorted(EXAMPLES.glob("*/DEMAND_DASHBOARD_SNAPSHOT.json")):
            with self.subTest(path=snapshot_path):
                payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
                self.assertFalse(payload["input_summary"]["real_user_data_included"])
                self.assertFalse(payload["input_summary"]["raw_queries_included"])
                self.assertFalse(payload["input_summary"]["protected_data_included"])
                self.assertTrue(payload["privacy_guard_summary"]["privacy_filter_required"])
                self.assertTrue(payload["poisoning_guard_summary"]["poisoning_filter_required"])
                self.assertFalse(payload["public_visibility"]["raw_queries_visible"])
                self.assertFalse(payload["public_visibility"]["private_data_visible"])
                for bucket in payload["aggregate_buckets"]:
                    self.assertFalse(bucket["count_claimed_as_real_user_demand"])
                    self.assertTrue(bucket["privacy_safe"])
                    self.assertTrue(bucket["poisoning_filtered"])
                for field in (
                    "runtime_dashboard_implemented",
                    "persistent_dashboard_store_implemented",
                    "telemetry_exported",
                    "account_tracking_performed",
                    "ip_tracking_performed",
                    "public_query_logging_enabled",
                    "raw_query_retained",
                    "real_user_demand_claimed",
                ):
                    self.assertFalse(payload["no_runtime_guarantees"][field], field)
                for field in (
                    "query_observation_mutated",
                    "result_cache_mutated",
                    "miss_ledger_mutated",
                    "search_need_mutated",
                    "probe_queue_mutated",
                    "candidate_index_mutated",
                    "candidate_promotion_mutated",
                    "known_absence_mutated",
                    "public_index_mutated",
                    "local_index_mutated",
                    "master_index_mutated",
                    "external_calls_performed",
                    "live_source_called",
                ):
                    self.assertFalse(payload["no_mutation_guarantees"][field], field)

    def test_report_hard_flags(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertFalse(report["runtime_dashboard_implemented"])
        self.assertFalse(report["persistent_dashboard_store_implemented"])
        self.assertFalse(report["telemetry_implemented"])
        self.assertFalse(report["account_tracking_implemented"])
        self.assertFalse(report["ip_tracking_implemented"])
        self.assertFalse(report["real_user_demand_claimed"])
        self.assertTrue(report["raw_query_retention_default_none"])
        self.assertFalse(report["master_index_mutation_allowed"])

    def test_docs_state_contract_only_no_runtime_no_mutation(self) -> None:
        text = (ROOT / "docs" / "reference" / "DEMAND_DASHBOARD_CONTRACT.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "dashboard is not runtime yet",
            "dashboard is not telemetry",
            "dashboard is not user tracking",
            "does not claim real demand",
            "privacy filtering before aggregation",
            "poisoning/fake-demand filtering before aggregation",
            "public visibility caveats",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
