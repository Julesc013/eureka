from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.worker import LocalWorkerRunner
from runtime.worker.workunit_queue import WorkUnit


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class LocalWorkerIntegrationTests(unittest.TestCase):
    def test_runner_uses_local_appliance_composition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            try:
                self.assertIsNotNone(runtime.workunit_queue)
                item = runtime.workunit_queue.create_workunit(
                    WorkUnit.new("regression_test", "Composition sample", payload={"worker_kind": "local_status_snapshot_worker"})
                )
                result = LocalWorkerRunner(runtime).run_one(item.id)
                self.assertEqual("complete", result.status.value)
                status = result.outputs["runtime_status"]
                self.assertEqual("pass", status["status"])
                self.assertFalse(status["lan_enabled"])
                self.assertFalse(status["deployment_performed"])
            finally:
                close_local_appliance(runtime)

    def test_plan_does_not_transition_workunit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            try:
                item = runtime.workunit_queue.create_workunit(
                    WorkUnit.new("regression_test", "Plan sample", payload={"worker_kind": "noop_worker"})
                )
                before_transitions = len(runtime.workunit_queue.list_transitions(item.id))
                result = LocalWorkerRunner(runtime).plan_run(item.id)
                self.assertEqual("planned", result.status.value)
                self.assertEqual("queued", runtime.workunit_queue.get_workunit(item.id).state.value)
                self.assertEqual(before_transitions, len(runtime.workunit_queue.list_transitions(item.id)))
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
