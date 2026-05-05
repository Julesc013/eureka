import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "public-query-observation-runtime-planning-v0"


class PublicQueryObservationRuntimePlanOperationTests(unittest.TestCase):
    def test_report_and_inventory_parse(self):
        report = json.loads((AUDIT / "public_query_observation_runtime_planning_report.json").read_text(encoding="utf-8"))
        inventory = json.loads((ROOT / "control" / "inventory" / "query_intelligence" / "public_query_observation_runtime_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(report["readiness_decision"], "blocked_hosted_deployment_unverified")
        self.assertEqual(inventory["status"], "planning_only")

    def test_hard_booleans_false(self):
        report = json.loads((AUDIT / "public_query_observation_runtime_planning_report.json").read_text(encoding="utf-8"))
        for key in (
            "runtime_query_observation_implemented",
            "persistent_observation_store_implemented",
            "hosted_runtime_enabled",
            "telemetry_implemented",
            "raw_query_retention_enabled",
            "ip_tracking_enabled",
            "account_tracking_enabled",
            "user_profile_tracking_enabled",
            "public_aggregate_enabled",
            "public_search_runtime_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "live_source_called",
            "external_calls_performed",
        ):
            self.assertFalse(report[key], key)

    def test_required_planning_docs_exist(self):
        for name in ("SAFE_FIELD_MODEL.md", "ACCEPTANCE_CRITERIA.md", "HOSTED_DEPLOYMENT_GATE_REVIEW.md", "DO_NOT_IMPLEMENT_YET.md"):
            self.assertTrue((AUDIT / name).exists(), name)
        do_not = (AUDIT / "DO_NOT_IMPLEMENT_YET.md").read_text(encoding="utf-8").lower()
        self.assertIn("no runtime observation writes", do_not)
        self.assertIn("no telemetry", do_not)
        self.assertIn("no raw query logging", do_not)
        self.assertIn("no index mutation", do_not)


if __name__ == "__main__":
    unittest.main()
