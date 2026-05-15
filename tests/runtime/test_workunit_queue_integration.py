from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import LocalReadOnlyStoreMutationError, close_local_appliance, open_local_appliance
from runtime.workunit_queue import WorkUnit


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class WorkUnitQueueIntegrationTests(unittest.TestCase):
    def test_queue_integrates_with_local_appliance_manifest_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            try:
                self.assertIsNotNone(runtime.workunit_queue)
                self.assertIn("workunit_queue", runtime.store_manifest.stores)
                status = runtime.status().to_dict()
                self.assertIn("workunit_queue", status["stores"])
                self.assertEqual("db/workunit_queue.sqlite", status["workunit_queue"]["relative_path"])
                self.assertIs(status["workunit_queue"]["execution_enabled"], False)
                self.assertEqual("pass", runtime.check_integrity()["status"])
            finally:
                close_local_appliance(runtime)

    def test_queue_mutation_does_not_change_public_index_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            try:
                before = runtime.public_index.summarize().to_dict()
                runtime.workunit_queue.create_workunit(WorkUnit.new("search_need", "No public index mutation"))
                after = runtime.public_index.summarize().to_dict()
                self.assertEqual(before, after)
            finally:
                close_local_appliance(runtime)

    def test_read_only_runtime_blocks_queue_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                with self.assertRaises(LocalReadOnlyStoreMutationError):
                    runtime.workunit_queue.create_workunit
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
