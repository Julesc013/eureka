from __future__ import annotations

import unittest

from runtime.snapshots import project_reviewed_record_to_snapshot
from runtime.snapshots.relay_foundation import sample_reviewed_records


class SnapshotRecordTests(unittest.TestCase):
    def test_private_fields_are_removed_from_snapshot_record(self) -> None:
        snapshot_record = project_reviewed_record_to_snapshot(sample_reviewed_records()[0])

        self.assertTrue(snapshot_record["private_fields_removed"])
        self.assertNotIn("private_notes", snapshot_record)
        self.assertEqual(snapshot_record["reviewed_status"], "reviewed_local")


if __name__ == "__main__":
    unittest.main()
