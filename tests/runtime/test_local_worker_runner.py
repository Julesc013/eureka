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


class LocalWorkerRunnerTests(unittest.TestCase):
    def make_runtime(self):
        temp = tempfile.TemporaryDirectory()
        instance = Path(temp.name) / "eureka-instance"
        self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
        runtime = open_local_appliance(instance)
        return temp, runtime

    def test_noop_worker_completes_and_records_refs(self) -> None:
        temp, runtime = self.make_runtime()
        try:
            before_public = runtime.public_index.summarize().to_dict()
            item = runtime.workunit_queue.create_workunit(
                WorkUnit.new("regression_test", "Noop sample", payload={"worker_kind": "noop_worker"})
            )
            result = LocalWorkerRunner(runtime).run_one(item.id)
            self.assertEqual("complete", result.status.value)
            self.assertFalse(result.to_dict()["external_network_used"])
            self.assertGreaterEqual(len(runtime.workunit_queue.list_transitions(item.id)), 2)
            refs = runtime.workunit_queue.list_payload_refs(item.id)
            self.assertTrue(any(ref.ref_kind == "worker_audit_event" for ref in refs))
            self.assertEqual(before_public, runtime.public_index.summarize().to_dict())
        finally:
            close_local_appliance(runtime)
            temp.cleanup()

    def test_safe_workers_complete(self) -> None:
        temp, runtime = self.make_runtime()
        try:
            runner = LocalWorkerRunner(runtime)
            samples = [
                WorkUnit.new("evidence_review", "Review summary", payload={"worker_kind": "review_queue_checker"}),
                WorkUnit.new("search_need", "Absence sample", payload={"worker_kind": "absence_report_worker", "query": "not-present"}),
                WorkUnit.new("regression_test", "Status sample", payload={"worker_kind": "local_status_snapshot_worker"}),
            ]
            for sample in samples:
                item = runtime.workunit_queue.create_workunit(sample)
                result = runner.run_one(item.id)
                self.assertEqual("complete", result.status.value)
                self.assertFalse(result.to_dict()["source_probe_executed"])
                self.assertFalse(result.to_dict()["model_provider_used"])
        finally:
            close_local_appliance(runtime)
            temp.cleanup()

    def test_rebuild_worker_requires_token_and_disabled_workers_block(self) -> None:
        temp, runtime = self.make_runtime()
        try:
            runner = LocalWorkerRunner(runtime)
            rebuild = runtime.workunit_queue.create_workunit(
                WorkUnit.new("index_rebuild", "Rebuild sample", payload={"worker_kind": "reviewed_index_rebuild_worker"})
            )
            rebuild_result = runner.run_one(rebuild.id)
            self.assertEqual("blocked", rebuild_result.status.value)
            for kind in ("source_probe_worker", "extraction_worker", "ai_model_worker"):
                item = runtime.workunit_queue.create_workunit(WorkUnit.new("regression_test", kind, payload={"worker_kind": kind}))
                result = runner.run_one(item.id)
                self.assertEqual("blocked", result.status.value)
                self.assertFalse(result.to_dict()["external_network_used"])
        finally:
            close_local_appliance(runtime)
            temp.cleanup()

    def test_untagged_source_probe_defaults_to_blocked_worker(self) -> None:
        temp, runtime = self.make_runtime()
        try:
            item = runtime.workunit_queue.create_workunit(WorkUnit.new("source_probe", "Untagged source probe"))
            result = LocalWorkerRunner(runtime).run_one(item.id)
            self.assertEqual("blocked", result.status.value)
            self.assertEqual("source_probe_worker", result.run.worker_kind)
            self.assertFalse(result.to_dict()["source_probe_executed"])
        finally:
            close_local_appliance(runtime)
            temp.cleanup()

    def test_run_next_filters_on_natural_worker_kind(self) -> None:
        temp, runtime = self.make_runtime()
        try:
            source_item = runtime.workunit_queue.create_workunit(WorkUnit.new("source_probe", "Queued source probe"))
            noop_item = runtime.workunit_queue.create_workunit(
                WorkUnit.new("regression_test", "Queued noop", payload={"worker_kind": "noop_worker"})
            )
            results = LocalWorkerRunner(runtime).run_next(kind="noop_worker")
            self.assertEqual(1, len(results))
            self.assertEqual(noop_item.id, results[0].run.workunit_id)
            self.assertEqual("queued", runtime.workunit_queue.get_workunit(source_item.id).state.value)
        finally:
            close_local_appliance(runtime)
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
