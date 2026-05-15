from __future__ import annotations

import unittest

from runtime.local_worker import LocalWorkerResult, LocalWorkerRun, LocalWorkerStatus, validate_worker_result
from runtime.local_worker.errors import LocalWorkerValidationError


class LocalWorkerResultTests(unittest.TestCase):
    def test_worker_result_records_audit_event(self) -> None:
        run = LocalWorkerRun.new("wku_sample", "noop_worker")
        result = LocalWorkerResult.from_worker_output(
            run,
            {"allowed": True, "worker_kind": "noop_worker"},
            inputs={"workunit_id": "wku_sample"},
            outputs={"message": "ok"},
        )
        validate_worker_result(result)
        payload = result.to_dict()
        self.assertEqual("complete", payload["status"])
        self.assertEqual("local_worker_audit_event.v0", payload["audit_event"]["schema_version"])
        self.assertFalse(payload["external_network_used"])
        self.assertFalse(payload["source_probe_executed"])

    def test_only_rebuild_worker_may_record_public_index_mutation(self) -> None:
        run = LocalWorkerRun.new("wku_sample", "noop_worker")
        result = LocalWorkerResult.from_worker_output(
            run,
            {"allowed": True, "worker_kind": "noop_worker"},
            inputs={},
            outputs={},
            store_mutations=({"store_id": "public_index"},),
        )
        with self.assertRaises(LocalWorkerValidationError):
            validate_worker_result(result)

    def test_status_values_are_stable(self) -> None:
        self.assertEqual(
            {"planned", "running", "complete", "failed", "blocked", "skipped"},
            {item.value for item in LocalWorkerStatus},
        )


if __name__ == "__main__":
    unittest.main()
