from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_06


class SnapshotRefreshReviewedBoundedAbsencesTests(unittest.TestCase):
    def test_reviewed_bounded_absences_are_not_universal(self) -> None:
        result = run_snapshot_refresh_06(from_review_batch_apply_examples=True)
        section = result["reviewed_bounded_absence_section"]

        self.assertEqual("snapshot_reviewed_bounded_absence_section.v0", section["schema_version"])
        self.assertEqual(2, section["reviewed_bounded_absence_count"])
        self.assertTrue(section["reviewed_bounded_absences_are_bounded_not_universal"])
        for record in section["records"]:
            self.assertFalse(record["accepted_truth"])
            self.assertFalse(record["universal_absence_claim"])
            self.assertTrue(record["reviewed_bounded_absence_not_universal"])
            self.assertFalse(record["public_index_mutated"])


if __name__ == "__main__":
    unittest.main()
