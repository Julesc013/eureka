from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.search_hunt import build_background_hunt_plan
from runtime.search_need import create_workunits_from_need


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class BackgroundHuntRunnerPlanTests(unittest.TestCase):
    def test_plan_lists_runnable_and_blocked_workunits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="plan")
                create_workunits_from_need(runtime, need.id, operator_label="plan")

                plan = build_background_hunt_plan(runtime, hunt.id)
                self.assertGreaterEqual(plan.runnable_count, 1)
                self.assertGreaterEqual(plan.blocked_count, 1)
                self.assertTrue(any(item.worker_kind == "noop_worker" for item in plan.runnable_items))
                self.assertTrue(any(item.worker_kind == "source_probe_worker" for item in plan.blocked_items))
                self.assertFalse(plan.to_dict()["source_probe_execution_enabled"])
                self.assertFalse(plan.to_dict()["model_provider_enabled"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
