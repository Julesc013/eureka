from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_06


class SnapshotRefreshReviewBatchApplySectionTests(unittest.TestCase):
    def test_review_batch_apply_section_projects_temp_apply_only(self) -> None:
        result = run_snapshot_refresh_06(from_review_batch_apply_examples=True)
        section = result["review_batch_apply_section"]

        self.assertEqual("snapshot_review_batch_apply_section.v0", section["schema_version"])
        self.assertEqual(12, section["eligible_apply_count"])
        self.assertEqual(8, section["reviewed_record_delta_count"])
        self.assertEqual(2, section["reviewed_known_needs_created"])
        self.assertEqual(2, section["reviewed_bounded_absences_created"])
        self.assertEqual(60, section["non_applied_count"])
        self.assertTrue(section["temp_apply_only"])
        self.assertFalse(section["operator_instance_mutated"])
        self.assertFalse(section["public_index_mutated"])
        self.assertFalse(section["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()
