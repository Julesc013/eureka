import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "software-heritage-connector-runtime-planning-v0"


class SoftwareHeritageConnectorRuntimePlanOperationTests(unittest.TestCase):
    def test_report_and_inventory_parse(self):
        report = json.loads((AUDIT / "software_heritage_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        inventory = json.loads((ROOT / "control" / "inventory" / "connectors" / "software_heritage_connector_runtime_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(report["readiness_decision"], "blocked_connector_approval_pending")
        self.assertEqual(inventory["status"], "planning_only")
        self.assertEqual(inventory["connector_id"], "software_heritage_connector")

    def test_hard_booleans_false(self):
        report = json.loads((AUDIT / "software_heritage_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        for key in (
            "runtime_connector_implemented",
            "live_calls_enabled",
            "external_calls_performed",
            "software_heritage_api_called",
            "swhid_resolved_live",
            "origin_lookup_performed",
            "visit_lookup_performed",
            "snapshot_lookup_performed",
            "release_lookup_performed",
            "revision_lookup_performed",
            "directory_lookup_performed",
            "content_blob_lookup_performed",
            "source_sync_worker_execution_enabled",
            "source_cache_runtime_enabled",
            "evidence_ledger_runtime_enabled",
            "public_search_live_fanout_enabled",
            "arbitrary_swhid_fetch_enabled",
            "arbitrary_origin_fetch_enabled",
            "arbitrary_repository_fetch_enabled",
            "content_blob_fetch_enabled",
            "directory_content_traversal_enabled",
            "source_code_download_enabled",
            "source_archive_download_enabled",
            "repository_clone_enabled",
            "origin_crawl_enabled",
            "source_code_execution_enabled",
            "downloads_enabled",
            "mirroring_enabled",
            "file_retrieval_enabled",
            "installs_enabled",
            "execution_enabled",
            "telemetry_enabled",
            "credentials_configured",
            "software_heritage_token_enabled",
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
            "SWHID_ORIGIN_REPOSITORY_AND_SOURCE_POLICY_GATE_REVIEW.md",
            "SOURCE_CODE_CONTENT_BOUNDARY_REVIEW.md",
            "TOKEN_AUTH_BOUNDARY_REVIEW.md",
            "USER_AGENT_CONTACT_AND_RATE_LIMIT_REVIEW.md",
            "SWHID_ORIGIN_REPOSITORY_REVIEW_AND_NORMALIZATION_PLAN.md",
            "ACCEPTANCE_CRITERIA.md",
            "DO_NOT_IMPLEMENT_YET.md",
        ):
            self.assertTrue((AUDIT / name).exists(), name)
        do_not = (AUDIT / "DO_NOT_IMPLEMENT_YET.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "no software heritage api calls",
            "no connector runtime",
            "no source cache writes",
            "no evidence ledger writes",
            "no arbitrary swhid/origin/repository fetch",
            "no swhid live resolution",
            "no origin lookup",
            "no visit/snapshot/release/revision/directory/content lookup",
            "no content blob fetch",
            "no directory traversal",
            "no source code download",
            "no source archive download",
            "no repository clone",
            "no origin crawl",
            "no source code execution",
            "no index/master mutation",
        ):
            self.assertIn(phrase, do_not)

    def test_gates_present_in_report(self):
        report = json.loads((AUDIT / "software_heritage_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["approval_gate_review"]["connector_approved_now"])
        self.assertEqual(report["approval_gate_review"]["decision"], "runtime_blocked")
        gates = report["swhid_origin_repository_source_policy_gate_review"]
        self.assertTrue(gates["swhid_policy_review_required"])
        self.assertTrue(gates["origin_url_policy_review_required"])
        self.assertTrue(gates["repository_identity_review_required"])
        self.assertTrue(gates["source_policy_review_required"])
        self.assertFalse(report["source_code_content_boundary_review"]["content_blob_fetch_enabled"])
        self.assertFalse(report["source_code_content_boundary_review"]["directory_content_traversal_enabled"])
        self.assertFalse(report["source_code_content_boundary_review"]["repository_clone_enabled"])
        self.assertFalse(report["source_code_content_boundary_review"]["source_code_safety_claimed"])
        self.assertTrue(report["token_auth_boundary_review"]["token_free_v0"])
        self.assertFalse(report["token_auth_boundary_review"]["software_heritage_token_enabled"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["user_agent_configured"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["contact_configured"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["rate_limit_configured"])


if __name__ == "__main__":
    unittest.main()
