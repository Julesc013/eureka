from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.search_hunt import run_background_hunt_batch, run_next_hunt_workunit
from runtime.search_need import create_workunits_from_need
from runtime.workunit_queue.records import WorkUnit, WorkUnitType


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class BackgroundHuntRunnerExecutionTests(unittest.TestCase):
    def test_run_next_executes_one_safe_workunit_and_records_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="execution")
                create_workunits_from_need(runtime, need.id, operator_label="execution")

                result = run_next_hunt_workunit(runtime, hunt.id, operator_context={"authorized": True, "operator_label": "execution"})
                refs = runtime.workunit_queue.list_payload_refs(limit=200)
                transitions = runtime.workunit_queue.list_transitions(limit=200)
                runs = runtime.search_hunt.list_background_hunt_runs(hunt_id=hunt.id, limit=10)

                self.assertEqual("complete", result.run.status.value)
                self.assertEqual(1, len(result.run.worker_results))
                self.assertTrue(any(ref.ref_kind == "worker_result" for ref in refs))
                self.assertTrue(any(item.to_state.value == "complete" for item in transitions))
                self.assertEqual(1, len(runs))
                self.assertFalse(result.run.to_dict()["source_probe_executed"])
            finally:
                close_local_appliance(runtime)

    def test_run_batch_respects_limit_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="batch")
                for index in range(12):
                    payload = {
                        "search_need_id": need.id,
                        "search_hunt_id": hunt.id,
                        "exhaustion_report_id": need.exhaustion_report_id,
                        "policy_state": "queued_local_safe",
                        "worker_kind": "noop_worker",
                    }
                    runtime.workunit_queue.create_workunit(WorkUnit.new(WorkUnitType.REGRESSION_TEST, f"safe local check {index}", payload=payload))

                result = run_background_hunt_batch(runtime, hunt.id, limit=50, operator_context={"authorized": True, "operator_label": "batch"})
                self.assertEqual(10, len(result.run.workunit_ids))
                self.assertEqual("complete", result.run.status.value)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
