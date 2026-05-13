from __future__ import annotations

import unittest

from runtime.local_worker import evaluate_worker_policy, validate_no_forbidden_worker_kind
from runtime.local_worker.errors import LocalWorkerValidationError
from runtime.workunit_queue import WorkUnit


class LocalWorkerPolicyTests(unittest.TestCase):
    def test_allowed_worker_policy(self) -> None:
        workunit = WorkUnit.new("regression_test", "Policy sample", payload={"worker_kind": "noop_worker"})
        decision = evaluate_worker_policy(workunit, "noop_worker")
        self.assertTrue(decision["allowed"])
        self.assertFalse(decision["external_network_allowed"])
        self.assertFalse(decision["source_probe_allowed"])
        self.assertFalse(decision["model_provider_allowed"])

    def test_rebuild_worker_requires_operator_token(self) -> None:
        workunit = WorkUnit.new("index_rebuild", "Rebuild sample", payload={"worker_kind": "reviewed_index_rebuild_worker"})
        blocked = evaluate_worker_policy(workunit, "reviewed_index_rebuild_worker")
        self.assertFalse(blocked["allowed"])
        self.assertIn("operator token", blocked["reason"])
        allowed = evaluate_worker_policy(workunit, "reviewed_index_rebuild_worker", {"authorized": True})
        self.assertTrue(allowed["allowed"])
        self.assertTrue(allowed["requires_operator_token"])

    def test_disabled_workers_fail_closed(self) -> None:
        workunit = WorkUnit.new("source_probe", "Blocked sample", payload={"worker_kind": "source_probe_worker"})
        for kind in ("source_probe_worker", "extraction_worker", "ai_model_worker"):
            decision = evaluate_worker_policy(workunit, kind)
            self.assertFalse(decision["allowed"])
            self.assertFalse(decision["external_network_allowed"])
            with self.assertRaises(LocalWorkerValidationError):
                validate_no_forbidden_worker_kind(kind)


if __name__ == "__main__":
    unittest.main()
