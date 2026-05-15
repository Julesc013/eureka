from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class HuntToSearchNeedTests(unittest.TestCase):
    def test_search_need_created_from_hunt_and_exhaustion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance)
            try:
                before_work = runtime.workunit_queue.summarize().to_dict()
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="tester")
                duplicate = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="tester")
                latest_report = runtime.search_hunt.get_latest_exhaustion_report(hunt.id)
                after_work = runtime.workunit_queue.summarize().to_dict()

                self.assertEqual(need.id, duplicate.id)
                self.assertEqual(hunt.id, need.hunt_id)
                self.assertEqual(latest_report.report_id, need.exhaustion_report_id)
                self.assertFalse(need.to_dict()["workunit_creation_enabled"])
                self.assertEqual(before_work, after_work)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
