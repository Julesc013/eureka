import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVAL = ROOT / "examples/connectors/github_releases_approval_v0/GITHUB_RELEASES_CONNECTOR_APPROVAL.json"
MANIFEST = ROOT / "examples/connectors/github_releases_approval_v0/GITHUB_RELEASES_CONNECTOR_MANIFEST.json"
INVENTORY = ROOT / "control/inventory/connectors/github_releases_connector.json"
REPORT = ROOT / "control/audits/github-releases-connector-approval-v0/github_releases_connector_approval_report.json"


class GitHubReleasesConnectorApprovalOperationsTests(unittest.TestCase):
    def test_contracts_example_inventory_and_report_exist(self):
        for path in (
            ROOT / "contracts/connectors/github_releases_connector_approval.v0.json",
            ROOT / "contracts/connectors/github_releases_connector_manifest.v0.json",
            APPROVAL,
            MANIFEST,
            INVENTORY,
            REPORT,
            ROOT / "docs/reference/GITHUB_RELEASES_CONNECTOR_APPROVAL.md",
        ):
            self.assertTrue(path.is_file(), path)

    def test_example_hard_flags_false_and_pending(self):
        a = json.loads(APPROVAL.read_text(encoding="utf-8"))
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
            "external_calls_performed",
            "github_api_called",
            "repository_cloned",
            "tags_fetched",
            "releases_fetched",
            "release_assets_downloaded",
            "source_archive_downloaded",
            "public_search_live_fanout_enabled",
            "downloads_enabled",
            "file_retrieval_enabled",
            "mirroring_enabled",
            "installs_enabled",
            "execution_enabled",
            "credentials_used",
            "github_token_used",
            "telemetry_exported",
        ):
            self.assertFalse(a["no_runtime_guarantees"][key], key)
        for key in ("source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated", "public_index_mutated", "local_index_mutated", "master_index_mutated"):
            self.assertFalse(a["no_mutation_guarantees"][key], key)
        self.assertFalse(a["repository_identity_policy"]["arbitrary_public_query_repository_allowed"])
        self.assertTrue(a["repository_identity_policy"]["owner_repo_review_required"])
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
            "arbitrary_repository_fetch_allowed",
            "repository_clone_allowed",
            "release_asset_download_allowed",
            "source_archive_download_allowed",
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
            "github_api_called",
            "repository_cloned",
            "releases_fetched",
            "release_assets_downloaded",
            "source_archive_downloaded",
            "public_search_live_fanout_enabled",
            "arbitrary_repository_fetch_allowed",
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
            "telemetry_implemented",
            "credentials_configured",
            "token_required_now",
            "github_token_used",
        ):
            self.assertFalse(rep[key], key)

    def test_docs_state_approval_only_no_runtime_no_mutation(self):
        text = (ROOT / "docs/reference/GITHUB_RELEASES_CONNECTOR_APPROVAL.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "live connector is not implemented",
            "no external calls",
            "no github api calls",
            "release metadata-only",
            "arbitrary repository fetch",
            "repository clone",
            "release asset download",
            "source archive download",
            "repository owner/name review",
            "token policy",
            "cache-first",
            "public search must not call github",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
