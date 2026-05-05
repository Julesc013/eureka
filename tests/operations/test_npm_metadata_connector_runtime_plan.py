import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "npm-metadata-connector-runtime-planning-v0"


class NpmMetadataConnectorRuntimePlanOperationTests(unittest.TestCase):
    def test_report_and_inventory_parse(self):
        report = json.loads((AUDIT / "npm_metadata_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        inventory = json.loads((ROOT / "control" / "inventory" / "connectors" / "npm_metadata_connector_runtime_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(report["readiness_decision"], "blocked_connector_approval_pending")
        self.assertEqual(inventory["status"], "planning_only")
        self.assertEqual(inventory["connector_id"], "npm_metadata_connector")

    def test_hard_booleans_false(self):
        report = json.loads((AUDIT / "npm_metadata_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        for key in (
            "runtime_connector_implemented",
            "live_calls_enabled",
            "external_calls_performed",
            "npm_registry_api_called",
            "npmjs_com_called",
            "npm_cli_called",
            "package_metadata_fetched",
            "version_metadata_fetched",
            "dist_tag_metadata_fetched",
            "tarball_metadata_fetched",
            "source_sync_worker_execution_enabled",
            "source_cache_runtime_enabled",
            "evidence_ledger_runtime_enabled",
            "public_search_live_fanout_enabled",
            "arbitrary_package_fetch_enabled",
            "tarball_download_enabled",
            "package_file_download_enabled",
            "package_install_enabled",
            "dependency_resolution_enabled",
            "npm_audit_enabled",
            "package_archive_inspection_enabled",
            "lifecycle_script_execution_enabled",
            "package_manager_invocation_enabled",
            "downloads_enabled",
            "mirroring_enabled",
            "file_retrieval_enabled",
            "installs_enabled",
            "execution_enabled",
            "telemetry_enabled",
            "credentials_configured",
            "npm_token_enabled",
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
            "PACKAGE_IDENTITY_SCOPED_PACKAGE_AND_SOURCE_POLICY_GATE_REVIEW.md",
            "DEPENDENCY_METADATA_BOUNDARY_REVIEW.md",
            "LIFECYCLE_SCRIPT_RISK_BOUNDARY_REVIEW.md",
            "TOKEN_AUTH_BOUNDARY_REVIEW.md",
            "USER_AGENT_CONTACT_AND_RATE_LIMIT_REVIEW.md",
            "PACKAGE_IDENTITY_REVIEW_AND_NORMALIZATION_PLAN.md",
            "ACCEPTANCE_CRITERIA.md",
            "DO_NOT_IMPLEMENT_YET.md",
        ):
            self.assertTrue((AUDIT / name).exists(), name)
        do_not = (AUDIT / "DO_NOT_IMPLEMENT_YET.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "no npm registry api calls",
            "no npmjs.com calls",
            "no connector runtime",
            "no source cache writes",
            "no evidence ledger writes",
            "no arbitrary package fetch",
            "no tarball download",
            "no package file download",
            "no package install",
            "no dependency resolution",
            "no npm audit",
            "no package archive inspection",
            "no package manager invocation",
            "no lifecycle script execution",
            "no index/master mutation",
        ):
            self.assertIn(phrase, do_not)

    def test_gates_present_in_report(self):
        report = json.loads((AUDIT / "npm_metadata_connector_runtime_planning_report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["approval_gate_review"]["connector_approved_now"])
        self.assertEqual(report["approval_gate_review"]["decision"], "runtime_blocked")
        gates = report["package_identity_scoped_package_source_policy_gate_review"]
        self.assertTrue(gates["package_identity_review_required"])
        self.assertTrue(gates["scoped_package_policy_review_required"])
        self.assertTrue(gates["source_policy_review_required"])
        self.assertFalse(report["dependency_metadata_boundary_review"]["dependency_resolution_enabled"])
        self.assertFalse(report["dependency_metadata_boundary_review"]["dependency_safety_claimed"])
        self.assertFalse(report["dependency_metadata_boundary_review"]["installability_claimed"])
        self.assertFalse(report["lifecycle_script_risk_boundary_review"]["lifecycle_script_execution_enabled"])
        self.assertFalse(report["lifecycle_script_risk_boundary_review"]["npm_audit_enabled"])
        self.assertFalse(report["lifecycle_script_risk_boundary_review"]["script_safety_claimed"])
        self.assertTrue(report["token_auth_boundary_review"]["token_free_v0"])
        self.assertFalse(report["token_auth_boundary_review"]["npm_token_enabled"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["user_agent_configured"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["contact_configured"])
        self.assertFalse(report["user_agent_contact_rate_limit_review"]["rate_limit_configured"])


if __name__ == "__main__":
    unittest.main()
