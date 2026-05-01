import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APPROVAL = ROOT / "examples/connectors/internet_archive_metadata_approval_v0/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.json"
MANIFEST = ROOT / "examples/connectors/internet_archive_metadata_approval_v0/INTERNET_ARCHIVE_METADATA_CONNECTOR_MANIFEST.json"
INVENTORY = ROOT / "control/inventory/connectors/internet_archive_metadata_connector.json"
REPORT = ROOT / "control/audits/internet-archive-metadata-connector-approval-v0/internet_archive_metadata_connector_approval_report.json"


class InternetArchiveMetadataConnectorApprovalOperationsTests(unittest.TestCase):
    def test_contracts_example_inventory_and_report_exist(self) -> None:
        for path in (
            ROOT / "contracts/connectors/internet_archive_metadata_connector_approval.v0.json",
            ROOT / "contracts/connectors/internet_archive_metadata_connector_manifest.v0.json",
            APPROVAL,
            MANIFEST,
            INVENTORY,
            REPORT,
            ROOT / "docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md",
        ):
            self.assertTrue(path.is_file(), path)

    def test_example_hard_flags_false_and_pending(self) -> None:
        approval = json.loads(APPROVAL.read_text(encoding="utf-8"))
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
            "external_calls_performed",
            "public_search_live_fanout_enabled",
            "downloads_enabled",
            "file_retrieval_enabled",
            "mirroring_enabled",
            "installs_enabled",
            "execution_enabled",
            "credentials_used",
            "telemetry_exported",
        ):
            self.assertFalse(approval["no_runtime_guarantees"][key], key)
        for key in (
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
        ):
            self.assertFalse(approval["no_mutation_guarantees"][key], key)
        self.assertFalse(approval["user_agent_and_contact_policy"]["contact_value_configured_now"])
        self.assertIsNone(approval["user_agent_and_contact_policy"]["contact_value"])
        self.assertTrue(all(item["status"] == "pending" for item in approval["approval_checklist"]))
        self.assertTrue(all(item["status"] == "pending" for item in approval["operator_checklist"]))

    def test_inventory_and_report_hard_flags_false(self) -> None:
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_enabled_by_default",
            "public_query_fanout_allowed",
            "downloads_allowed",
            "file_retrieval_allowed",
            "mirroring_allowed",
            "arbitrary_url_fetch_allowed",
            "source_cache_mutation_allowed_now",
            "evidence_ledger_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "master_index_mutation_allowed",
        ):
            self.assertFalse(inventory[key], key)
        for key in (
            "connector_runtime_implemented",
            "connector_approved_now",
            "live_source_called",
            "external_calls_performed",
            "public_search_live_fanout_enabled",
            "source_cache_mutation_allowed_now",
            "evidence_ledger_mutation_allowed_now",
            "candidate_index_mutation_allowed_now",
            "public_index_mutation_allowed_now",
            "local_index_mutation_allowed_now",
            "master_index_mutation_allowed",
            "downloads_allowed",
            "file_retrieval_allowed",
            "mirroring_allowed",
            "arbitrary_url_fetch_allowed",
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "telemetry_implemented",
            "credentials_configured",
        ):
            self.assertFalse(report[key], key)

    def test_docs_state_approval_only_no_runtime_no_mutation(self) -> None:
        text = (ROOT / "docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "connector is not implemented",
            "no external calls",
            "metadata-only",
            "downloads",
            "arbitrary url fetch",
            "source policy",
            "cache-first",
            "public search must not call",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
