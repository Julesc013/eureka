from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_06


class SnapshotRefreshReviewedKnownNeedsTests(unittest.TestCase):
    def test_reviewed_known_needs_are_not_resolved_objects(self) -> None:
        result = run_snapshot_refresh_06(from_review_batch_apply_examples=True)
        section = result["reviewed_known_need_section"]

        self.assertEqual("snapshot_reviewed_known_need_section.v0", section["schema_version"])
        self.assertEqual(2, section["reviewed_known_need_count"])
        self.assertTrue(section["reviewed_known_needs_are_not_resolved_objects"])
        for record in section["records"]:
            self.assertFalse(record["accepted_truth"])
            self.assertFalse(record["resolved_object_created"])
            self.assertTrue(record["reviewed_known_need_not_resolved_object"])
            self.assertFalse(record["public_index_mutated"])


if __name__ == "__main__":
    unittest.main()
