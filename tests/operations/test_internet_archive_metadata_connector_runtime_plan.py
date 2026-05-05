import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "internet-archive-metadata-connector-runtime-planning-v0"


class InternetArchiveMetadataConnectorRuntimePlanOperationTests(unittest.TestCase):
    def test_report_and_inventory_parse(self):
        report = json.loads((AUDIT / "internet_archive_metadata_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        inventory = json.loads((ROOT / "control" / "inventory" / "connectors" / "internet_archive_metadata_connector_runtime_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(report["readiness_decision"], "blocked_connector_approval_pending")
        self.assertEqual(inventory["status"], "planning_only")
        self.assertEqual(inventory["connector_id"], "internet_archive_metadata_connector")

    def test_hard_booleans_false(self):
        report = json.loads((AUDIT / "internet_archive_metadata_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        for key in (
            "runtime_connector_implemented",
            "live_calls_enabled",
            "external_calls_performed",
            "archive_org_called",
            "internet_archive_api_called",
            "source_sync_worker_execution_enabled",
            "source_cache_runtime_enabled",
            "evidence_ledger_runtime_enabled",
            "public_search_live_fanout_enabled",
            "downloads_enabled",
            "mirroring_enabled",
            "file_retrieval_enabled",
            "installs_enabled",
            "execution_enabled",
            "telemetry_enabled",
            "credentials_configured",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
        ):
            self.assertFalse(report[key], key)

    def test_required_gate_docs_exist(self):
        for name in (
            "APPROVAL_GATE_REVIEW.md",
            "SOURCE_POLICY_AND_OPERATOR_GATE_REVIEW.md",
            "USER_AGENT_CONTACT_AND_RATE_LIMIT_REVIEW.md",
            "ACCEPTANCE_CRITERIA.md",
            "DO_NOT_IMPLEMENT_YET.md",
        ):
            self.assertTrue((AUDIT / name).exists(), name)
        do_not = (AUDIT / "DO_NOT_IMPLEMENT_YET.md").read_text(encoding="utf-8").lower()
        for phrase in ("no ia api calls", "no connector runtime", "no source cache writes", "no evidence ledger writes", "no index/master mutation"):
            self.assertIn(phrase, do_not)

    def test_gates_present_in_report(self):
        report = json.loads((AUDIT / "internet_archive_metadata_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["approval_gate_review"]["connector_approved_now"])
        self.assertEqual(report["approval_gate_review"]["decision"], "runtime_blocked")
        self.assertTrue(report["source_policy_operator_gate_review"]["source_policy_review_required"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["user_agent_configured"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["contact_configured"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["rate_limit_configured"])


if __name__ == "__main__":
    unittest.main()
