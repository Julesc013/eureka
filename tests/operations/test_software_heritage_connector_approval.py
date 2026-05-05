import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVAL = ROOT / "examples/connectors/software_heritage_approval_v0/SOFTWARE_HERITAGE_CONNECTOR_APPROVAL.json"
MANIFEST = ROOT / "examples/connectors/software_heritage_approval_v0/SOFTWARE_HERITAGE_CONNECTOR_MANIFEST.json"
INVENTORY = ROOT / "control/inventory/connectors/software_heritage_connector.json"
REPORT = ROOT / "control/audits/software-heritage-connector-approval-v0/software_heritage_connector_approval_report.json"


class SoftwareHeritageConnectorApprovalOperationsTests(unittest.TestCase):
    def test_contracts_example_inventory_and_report_exist(self):
        for path in (
            ROOT / "contracts/connectors/software_heritage_connector_approval.v0.json",
            ROOT / "contracts/connectors/software_heritage_connector_manifest.v0.json",
            APPROVAL,
            MANIFEST,
            INVENTORY,
            REPORT,
            ROOT / "docs/reference/SOFTWARE_HERITAGE_CONNECTOR_APPROVAL.md",
        ):
            self.assertTrue(path.is_file(), path)

    def test_example_hard_flags_false_and_pending(self):
        a = json.loads(APPROVAL.read_text(encoding="utf-8"))
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
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
            "repository_cloned",
            "source_code_downloaded",
            "source_archive_downloaded",
            "source_file_retrieved",
            "public_search_live_fanout_enabled",
            "downloads_enabled",
            "file_retrieval_enabled",
            "mirroring_enabled",
            "installs_enabled",
            "execution_enabled",
            "credentials_used",
            "software_heritage_token_used",
            "telemetry_exported",
        ):
            self.assertFalse(a["no_runtime_guarantees"][key], key)
        for key in ("source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated", "public_index_mutated", "local_index_mutated", "master_index_mutated"):
            self.assertFalse(a["no_mutation_guarantees"][key], key)
        self.assertFalse(a["swhid_origin_repository_policy"]["arbitrary_public_query_origin_allowed"])
        self.assertTrue(a["swhid_origin_repository_policy"]["swhid_review_required"])
        self.assertTrue(a["swhid_origin_repository_policy"]["origin_url_review_required"])
        self.assertTrue(a["swhid_origin_repository_policy"]["repository_identity_review_required"])
        self.assertFalse(a["source_code_content_risk_policy"]["content_blob_fetch_allowed"])
        self.assertFalse(a["source_code_content_risk_policy"]["repository_clone_allowed"])
        self.assertFalse(a["source_code_content_risk_policy"]["source_code_safety_claim_allowed"])
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
            "arbitrary_origin_fetch_allowed",
            "arbitrary_swhid_fetch_allowed",
            "repository_clone_allowed",
            "source_code_download_allowed",
            "source_archive_download_allowed",
            "content_blob_fetch_allowed",
            "origin_crawl_allowed",
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
            "software_heritage_api_called",
            "swhid_resolved_live",
            "origin_lookup_performed",
            "visit_lookup_performed",
            "snapshot_lookup_performed",
            "release_lookup_performed",
            "revision_lookup_performed",
            "directory_lookup_performed",
            "content_blob_lookup_performed",
            "repository_cloned",
            "source_code_downloaded",
            "source_archive_downloaded",
            "source_file_retrieved",
            "public_search_live_fanout_enabled",
            "arbitrary_origin_fetch_allowed",
            "arbitrary_swhid_fetch_allowed",
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
            "source_code_safety_claimed",
            "source_completeness_claimed",
            "telemetry_implemented",
            "credentials_configured",
            "token_required_now",
            "software_heritage_token_used",
        ):
            self.assertFalse(rep[key], key)

    def test_docs_state_approval_only_no_runtime_no_mutation(self):
        text = (ROOT / "docs/reference/SOFTWARE_HERITAGE_CONNECTOR_APPROVAL.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "live connector is not implemented",
            "no external calls",
            "no software heritage api calls",
            "software identity/archive metadata-only",
            "arbitrary origin fetch",
            "arbitrary swhid fetch",
            "source code content fetch",
            "content blob fetch",
            "repository clone",
            "source archive download",
            "token policy",
            "cache-first",
            "public search must not call software heritage",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
