import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EXAMPLE=ROOT/'examples/connectors/wayback_cdx_memento_approval_v0/WAYBACK_CDX_MEMENTO_CONNECTOR_APPROVAL.json'
class WaybackCdxMementoConnectorApprovalValidatorTests(unittest.TestCase):
    def test_approval_validator_passes(self):
        c=subprocess.run([sys.executable,'scripts/validate_wayback_cdx_memento_connector_approval.py','--all-examples'],cwd=ROOT,text=True,capture_output=True,check=True); self.assertIn('status: valid',c.stdout)
    def test_approval_validator_json_parses(self):
        c=subprocess.run([sys.executable,'scripts/validate_wayback_cdx_memento_connector_approval.py','--all-examples','--json'],cwd=ROOT,text=True,capture_output=True,check=True); r=json.loads(c.stdout); self.assertEqual(r['status'],'valid'); self.assertEqual(r['example_count'],1)
    def test_negative_runtime_mutation_and_source_calls_fail(self):
        cases=[('connector_runtime_implemented',['no_runtime_guarantees','connector_runtime_implemented']),('connector_approved_now',['no_runtime_guarantees','connector_approved_now']),('live_source_called',['no_runtime_guarantees','live_source_called']),('external_calls_performed',['no_runtime_guarantees','external_calls_performed']),('archived_content_fetched',['no_runtime_guarantees','archived_content_fetched']),('capture_replayed',['no_runtime_guarantees','capture_replayed']),('warc_downloaded',['no_runtime_guarantees','warc_downloaded']),('downloads_enabled',['no_runtime_guarantees','downloads_enabled']),('file_retrieval_enabled',['no_runtime_guarantees','file_retrieval_enabled']),('public_search_live_fanout_enabled',['no_runtime_guarantees','public_search_live_fanout_enabled']),('source_cache_mutated',['no_mutation_guarantees','source_cache_mutated']),('evidence_ledger_mutated',['no_mutation_guarantees','evidence_ledger_mutated']),('master_index_mutated',['no_mutation_guarantees','master_index_mutated'])]
        base=json.loads(EXAMPLE.read_text(encoding='utf-8'))
        for label,path in cases:
            with self.subTest(label=label):
                p=copy.deepcopy(base); t=p
                for k in path[:-1]: t=t[k]
                t[path[-1]]=True; self._assert_invalid(p)
    def test_negative_url_policy_contact_and_secret_fail(self):
        base=json.loads(EXAMPLE.read_text(encoding='utf-8'))
        p=copy.deepcopy(base); p['user_agent_and_contact_policy']['contact_value']='ops@example.invalid'; p['user_agent_and_contact_policy']['contact_value_configured_now']=True; self._assert_invalid(p)
        p=copy.deepcopy(base); p['notes'].append('api_key=not-a-real-key'); self._assert_invalid(p)
        p=copy.deepcopy(base); p['url_and_uri_policy']['example_uri_r']='http://localhost/private'; self._assert_invalid(p)
    def test_negative_output_runtime_and_forbidden_policy_fail(self):
        base=json.loads(EXAMPLE.read_text(encoding='utf-8'))
        p=copy.deepcopy(base); p['expected_source_cache_outputs'][0]['output_runtime_implemented']=True; self._assert_invalid(p)
        p=copy.deepcopy(base)
        for item in p['forbidden_capabilities']:
            if item['capability']=='capture_replay': item['forbidden_now']=False
        self._assert_invalid(p)
        p=copy.deepcopy(base); p['url_and_uri_policy']['arbitrary_public_query_url_allowed']=True; self._assert_invalid(p)
    def _assert_invalid(self,payload):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'approval.json'; path.write_text(json.dumps(payload),encoding='utf-8')
            c=subprocess.run([sys.executable,'scripts/validate_wayback_cdx_memento_connector_approval.py','--approval',str(path),'--json'],cwd=ROOT,text=True,capture_output=True)
            self.assertNotEqual(c.returncode,0,c.stdout); self.assertEqual(json.loads(c.stdout)['status'],'invalid')
if __name__=='__main__': unittest.main()
