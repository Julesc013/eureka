from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.search_need import create_workunits_from_need, list_workunits_for_need


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class NeedToWorkUnitCreationTests(unittest.TestCase):
    def test_create_workunits_from_need_without_running_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="tester")
                result = create_workunits_from_need(runtime, need.id, operator_label="tester")
                second = create_workunits_from_need(runtime, need.id, operator_label="tester")
                linked = list_workunits_for_need(runtime, need.id, limit=100)

                self.assertEqual(result.created_count, len(result.plan.items))
                self.assertEqual(len(result.workunits), len(linked))
                self.assertEqual(len(result.workunits), len(second.workunits))
                self.assertTrue(any(item["state"] == "queued" for item in linked))
                self.assertTrue(any(item["state"] == "blocked" for item in linked))
                self.assertFalse(any(item["state"] in {"running", "complete", "failed"} for item in linked))
                self.assertTrue(all(item["search_need_id"] == need.id for item in linked))
                self.assertTrue(all(item["search_hunt_id"] == hunt.id for item in linked))
                self.assertTrue(all(item["exhaustion_report_id"] == need.exhaustion_report_id for item in linked))
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
