from __future__ import annotations

import unittest

from runtime.snapshots import build_snapshot_from_examples, build_snapshot_plan
from runtime.snapshots.relay_foundation import sample_reviewed_records


class SnapshotBuildTests(unittest.TestCase):
    def test_snapshot_plan_builds_from_reviewed_records(self) -> None:
        plan = build_snapshot_plan(sample_reviewed_records())

        self.assertEqual(plan["schema_version"], "snapshot_build_plan.v0")
        self.assertTrue(plan["reviewed_only"])
        self.assertTrue(plan["public_safe"])
        self.assertEqual(plan["reviewed_record_count"], 1)

    def test_snapshot_build_emits_required_packets(self) -> None:
        result = build_snapshot_from_examples()

        self.assertEqual(result["schema_version"], "snapshot_build_result.v0")
        self.assertEqual(result["envelope"]["schema_version"], "snapshot_envelope.v0")
        self.assertEqual(result["validation_report"]["status"], "pass")
        self.assertTrue(result["record_set"]["records"])


if __name__ == "__main__":
    unittest.main()
