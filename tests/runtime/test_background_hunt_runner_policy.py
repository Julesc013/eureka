from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.search.hunt import build_background_hunt_plan, run_next_hunt_workunit
from runtime.search.need import create_workunits_from_need
from runtime.worker.workunit_queue.records import WorkUnit, WorkUnitType


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class BackgroundHuntRunnerPolicyTests(unittest.TestCase):
    def test_disabled_workers_remain_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="policy")
                create_workunits_from_need(runtime, need.id, operator_label="policy")
                extraction = self._blocked(runtime, need, WorkUnitType.EXTRACTION_TASK, "extraction_worker")
                ai_model = self._blocked(runtime, need, WorkUnitType.REGRESSION_TEST, "ai_model_worker")

                plan = build_background_hunt_plan(runtime, hunt.id)
                run_next_hunt_workunit(runtime, hunt.id, operator_context={"authorized": True, "operator_label": "policy"})

                self.assertTrue(any(item.worker_kind == "source_probe_worker" and not item.runnable for item in plan.blocked_items))
                self.assertTrue(any(item.worker_kind == "extraction_worker" and not item.runnable for item in plan.blocked_items))
                self.assertTrue(any(item.worker_kind == "ai_model_worker" and not item.runnable for item in plan.blocked_items))
                self.assertEqual("blocked", runtime.workunit_queue.get_workunit(extraction.id).state.value)
                self.assertEqual("blocked", runtime.workunit_queue.get_workunit(ai_model.id).state.value)
            finally:
                close_local_appliance(runtime)

    def _blocked(self, runtime, need, kind, worker_kind):
        payload = {
            "search_need_id": need.id,
            "search_hunt_id": need.hunt_id,
            "exhaustion_report_id": need.exhaustion_report_id,
            "policy_state": "blocked_by_policy",
            "worker_kind": worker_kind,
        }
        stored = runtime.workunit_queue.create_workunit(WorkUnit.new(kind, worker_kind, payload=payload, parent_id=need.id))
        return runtime.workunit_queue.block_workunit(stored.id, "blocked by policy test")


if __name__ == "__main__":
    unittest.main()
