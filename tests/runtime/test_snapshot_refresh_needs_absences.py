from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh


class SnapshotRefreshNeedsAbsencesTests(unittest.TestCase):
    def test_needs_and_absences_are_projected_as_unresolved(self) -> None:
        section = run_snapshot_refresh(from_seed_examples=True)["need_absence_section"]

        self.assertGreater(section["known_need_count"], 0)
        self.assertGreater(section["absence_count"], 0)
        self.assertTrue(section["bounded_absence_statements"])
        self.assertTrue(section["unresolved_needs_remain_unresolved"])
        self.assertFalse(section["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
