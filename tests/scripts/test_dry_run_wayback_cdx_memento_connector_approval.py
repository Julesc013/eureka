import json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class DryRunWaybackCdxMementoConnectorApprovalTests(unittest.TestCase):
    def test_dry_run_json_is_safe_stdout_only_record(self):
        c=subprocess.run([sys.executable,'scripts/dry_run_wayback_cdx_memento_connector_approval.py','--json'],cwd=ROOT,text=True,capture_output=True,check=True); p=json.loads(c.stdout); self.assertEqual(p['approval_record_kind'],'wayback_cdx_memento_connector_approval')
        for k in ('connector_runtime_implemented','connector_approved_now','live_source_called','external_calls_performed','archived_content_fetched','capture_replayed','warc_downloaded','public_search_live_fanout_enabled','arbitrary_url_fetch_allowed','source_cache_mutated','evidence_ledger_mutated','master_index_mutated'):
            self.assertFalse(p[k],k)
if __name__=='__main__': unittest.main()
