import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVAL = ROOT / "examples/connectors/npm_metadata_approval_v0/NPM_METADATA_CONNECTOR_APPROVAL.json"
MANIFEST = ROOT / "examples/connectors/npm_metadata_approval_v0/NPM_METADATA_CONNECTOR_MANIFEST.json"
INVENTORY = ROOT / "control/inventory/connectors/npm_metadata_connector.json"
REPORT = ROOT / "control/audits/npm-metadata-connector-approval-v0/npm_metadata_connector_approval_report.json"


class NpmMetadataConnectorApprovalOperationsTests(unittest.TestCase):
    def test_contracts_example_inventory_and_report_exist(self):
        for path in (
            ROOT / "contracts/connectors/npm_metadata_connector_approval.v0.json",
            ROOT / "contracts/connectors/npm_metadata_connector_manifest.v0.json",
            APPROVAL,
            MANIFEST,
            INVENTORY,
            REPORT,
            ROOT / "docs/reference/NPM_METADATA_CONNECTOR_APPROVAL.md",
        ):
            self.assertTrue(path.is_file(), path)

    def test_example_hard_flags_false_and_pending(self):
        a = json.loads(APPROVAL.read_text(encoding="utf-8"))
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
            "external_calls_performed",
            "npm_registry_api_called",
            "npm_cli_called",
            "package_metadata_fetched",
            "versions_fetched",
            "dist_tags_fetched",
            "tarball_metadata_fetched",
            "tarballs_downloaded",
            "package_files_downloaded",
            "package_installed",
            "dependency_resolution_performed",
            "package_archive_inspected",
            "lifecycle_scripts_executed",
            "npm_audit_performed",
            "public_search_live_fanout_enabled",
            "downloads_enabled",
            "file_retrieval_enabled",
            "mirroring_enabled",
            "installs_enabled",
            "execution_enabled",
            "credentials_used",
            "npm_token_used",
            "telemetry_exported",
        ):
            self.assertFalse(a["no_runtime_guarantees"][key], key)
        for key in ("source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated", "public_index_mutated", "local_index_mutated", "master_index_mutated"):
            self.assertFalse(a["no_mutation_guarantees"][key], key)
        self.assertFalse(a["package_identity_policy"]["arbitrary_public_query_package_allowed"])
        self.assertTrue(a["package_identity_policy"]["package_name_review_required"])
        self.assertTrue(a["package_identity_policy"]["scoped_package_review_required"])
        self.assertTrue(a["scoped_package_policy"]["scope_name_review_required"])
        self.assertFalse(a["dependency_metadata_caution_policy"]["dependency_resolution_allowed_now"])
        self.assertFalse(a["dependency_metadata_caution_policy"]["dependency_safety_claim_allowed"])
        self.assertFalse(a["dependency_metadata_caution_policy"]["vulnerability_status_claim_allowed"])
        self.assertFalse(a["package_script_and_lifecycle_risk_policy"]["lifecycle_script_execution_allowed"])
        self.assertFalse(a["package_script_and_lifecycle_risk_policy"]["script_safety_claim_allowed"])
        self.assertFalse(a["user_agent_and_contact_policy"]["contact_value_configured_now"])
        self.assertIsNone(a["user_agent_and_contact_policy"]["contact_value"])
        self.assertTrue(all(i["status"] == "pending" for i in a["approval_checklist"]))
        self.assertTrue(all(i["status"] == "pending" for i in a["operator_checklist"]))

    def test_inventory_and_report_hard_flags_false(self):
        inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
        rep = json.loads(REPORT.read_text(encoding="utf-8"))
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_enabled_by_default",
            "public_query_fanout_allowed",
            "arbitrary_package_fetch_allowed",
            "package_install_allowed",
            "tarball_download_allowed",
            "package_file_download_allowed",
            "dependency_resolution_allowed_now",
            "lifecycle_script_execution_allowed",
            "npm_audit_allowed_now",
            "downloads_allowed",
            "file_retrieval_allowed",
            "mirroring_allowed",
            "token_required_now",
            "credentials_configured",
            "source_cache_mutation_allowed_now",
            "evidence_ledger_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "master_index_mutation_allowed",
        ):
            self.assertFalse(inv[key], key)
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
            "external_calls_performed",
            "npm_registry_api_called",
            "npm_cli_called",
            "package_metadata_fetched",
            "versions_fetched",
            "dist_tags_fetched",
            "tarball_metadata_fetched",
            "tarballs_downloaded",
            "package_files_downloaded",
            "package_installed",
            "dependency_resolution_performed",
            "package_archive_inspected",
            "lifecycle_scripts_executed",
            "npm_audit_performed",
            "public_search_live_fanout_enabled",
            "arbitrary_package_fetch_allowed",
            "source_cache_mutation_allowed_now",
            "evidence_ledger_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "public_index_mutation_allowed_now",
            "local_index_mutation_allowed_now",
            "master_index_mutation_allowed",
            "downloads_allowed",
            "file_retrieval_allowed",
            "mirroring_allowed",
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "dependency_safety_claimed",
            "vulnerability_status_claimed",
            "script_safety_claimed",
            "installability_claimed",
            "telemetry_implemented",
            "credentials_configured",
            "token_required_now",
            "npm_token_used",
        ):
            self.assertFalse(rep[key], key)

    def test_docs_state_approval_only_no_runtime_no_mutation(self):
        text = (ROOT / "docs/reference/NPM_METADATA_CONNECTOR_APPROVAL.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "live connector is not implemented",
            "no external calls",
            "no npm registry api calls",
            "no npm/yarn/pnpm cli calls",
            "package metadata-only",
            "arbitrary package fetch",
            "package install",
            "tarball download",
            "dependency resolution",
            "lifecycle script",
            "npm audit",
            "token policy",
            "cache-first",
            "public search must not call npm",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
