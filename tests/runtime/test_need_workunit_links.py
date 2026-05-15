from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.search_need import create_workunits_from_need, list_workunits_for_hunt, list_workunits_for_need


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


class NeedWorkUnitLinkTests(unittest.TestCase):
    def test_workunit_payload_refs_link_need_hunt_and_exhaustion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="tester")
                result = create_workunits_from_need(runtime, need.id, operator_label="tester")
                by_need = list_workunits_for_need(runtime, need.id)
                by_hunt = list_workunits_for_hunt(runtime, hunt.id)
                refs = runtime.workunit_queue.list_payload_refs(limit=500)

                self.assertEqual(len(result.workunits), len(by_need))
                self.assertEqual(len(by_need), len(by_hunt))
                ref_pairs = {(ref.ref_kind, ref.ref_id) for ref in refs}
                self.assertIn(("search_need", need.id), ref_pairs)
                self.assertIn(("search_hunt", hunt.id), ref_pairs)
                self.assertIn(("exhaustion_report", need.exhaustion_report_id), ref_pairs)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
