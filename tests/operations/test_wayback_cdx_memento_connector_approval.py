import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
APPROVAL=ROOT/'examples/connectors/wayback_cdx_memento_approval_v0/WAYBACK_CDX_MEMENTO_CONNECTOR_APPROVAL.json'
MANIFEST=ROOT/'examples/connectors/wayback_cdx_memento_approval_v0/WAYBACK_CDX_MEMENTO_CONNECTOR_MANIFEST.json'
INVENTORY=ROOT/'control/inventory/connectors/wayback_cdx_memento_connector.json'
REPORT=ROOT/'control/audits/wayback-cdx-memento-connector-approval-v0/wayback_cdx_memento_connector_approval_report.json'
class WaybackCdxMementoConnectorApprovalOperationsTests(unittest.TestCase):
    def test_contracts_example_inventory_and_report_exist(self):
        for p in (ROOT/'contracts/connectors/wayback_cdx_memento_connector_approval.v0.json',ROOT/'contracts/connectors/wayback_cdx_memento_connector_manifest.v0.json',APPROVAL,MANIFEST,INVENTORY,REPORT,ROOT/'docs/reference/WAYBACK_CDX_MEMENTO_CONNECTOR_APPROVAL.md'):
            self.assertTrue(p.is_file(),p)
    def test_example_hard_flags_false_and_pending(self):
        a=json.loads(APPROVAL.read_text(encoding='utf-8'))
        for k in ('connector_runtime_implemented','connector_approved_now','live_source_called','external_calls_performed','archived_content_fetched','capture_replayed','warc_downloaded','public_search_live_fanout_enabled','downloads_enabled','file_retrieval_enabled','mirroring_enabled','installs_enabled','execution_enabled','credentials_used','telemetry_exported'):
            self.assertFalse(a['no_runtime_guarantees'][k],k)
        for k in ('source_cache_mutated','evidence_ledger_mutated','candidate_index_mutated','public_index_mutated','local_index_mutated','master_index_mutated'):
            self.assertFalse(a['no_mutation_guarantees'][k],k)
        self.assertFalse(a['url_and_uri_policy']['arbitrary_public_query_url_allowed']); self.assertTrue(a['url_and_uri_policy']['uri_r_review_required']); self.assertFalse(a['user_agent_and_contact_policy']['contact_value_configured_now']); self.assertIsNone(a['user_agent_and_contact_policy']['contact_value']); self.assertTrue(all(i['status']=='pending' for i in a['approval_checklist'])); self.assertTrue(all(i['status']=='pending' for i in a['operator_checklist']))
    def test_inventory_and_report_hard_flags_false(self):
        inv=json.loads(INVENTORY.read_text(encoding='utf-8')); rep=json.loads(REPORT.read_text(encoding='utf-8'))
        for k in ('connector_runtime_implemented','connector_approved_now','live_enabled_by_default','public_query_fanout_allowed','arbitrary_url_fetch_allowed','archived_content_fetch_allowed','capture_replay_allowed','warc_download_allowed','downloads_allowed','file_retrieval_allowed','mirroring_allowed','source_cache_mutation_allowed_now','evidence_ledger_mutation_allowed_now','candidate_index_mutation_allowed_now','master_index_mutation_allowed'):
            self.assertFalse(inv[k],k)
        for k in ('connector_runtime_implemented','connector_approved_now','live_source_called','external_calls_performed','public_search_live_fanout_enabled','arbitrary_url_fetch_allowed','archived_content_fetch_allowed','capture_replay_allowed','warc_download_allowed','source_cache_mutation_allowed_now','evidence_ledger_mutation_allowed_now','candidate_index_mutation_allowed_now','public_index_mutation_allowed_now','local_index_mutation_allowed_now','master_index_mutation_allowed','downloads_allowed','file_retrieval_allowed','mirroring_allowed','rights_clearance_claimed','malware_safety_claimed','telemetry_implemented','credentials_configured'):
            self.assertFalse(rep[k],k)
    def test_docs_state_approval_only_no_runtime_no_mutation(self):
        text=(ROOT/'docs/reference/WAYBACK_CDX_MEMENTO_CONNECTOR_APPROVAL.md').read_text(encoding='utf-8').casefold()
        for phrase in ('connector is not implemented','no external calls','availability/capture metadata-only','arbitrary url fetch','archived page content fetch','capture replay','warc download','uri-r review','cache-first','public search must not call'):
            self.assertIn(phrase,text)
if __name__=='__main__': unittest.main()
