import json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class WaybackCdxMementoConnectorContractValidatorTests(unittest.TestCase):
    def test_contract_validator_passes(self):
        c=subprocess.run([sys.executable,'scripts/validate_wayback_cdx_memento_connector_contract.py'],cwd=ROOT,text=True,capture_output=True,check=True); self.assertIn('status: valid',c.stdout)
    def test_contract_validator_json_parses(self):
        c=subprocess.run([sys.executable,'scripts/validate_wayback_cdx_memento_connector_contract.py','--json'],cwd=ROOT,text=True,capture_output=True,check=True); r=json.loads(c.stdout); self.assertEqual(r['status'],'valid'); self.assertEqual(r['example_count'],1); self.assertEqual(r['contract_file'],'contracts/connectors/wayback_cdx_memento_connector_approval.v0.json')
if __name__=='__main__': unittest.main()
