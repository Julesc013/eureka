from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh


class SnapshotRefreshTests(unittest.TestCase):
    def test_refresh_builds_full_packet(self) -> None:
        result = run_snapshot_refresh(from_seed_examples=True)

        self.assertEqual("snapshot_refresh_result.v0", result["schema_version"])
        self.assertTrue(result["fixture_snapshot_refresh_passed"])
        self.assertEqual(2, len(result["source_batches"]))
        self.assertGreater(result["candidate_count"], 0)
        self.assertFalse(result["accepted_truth_created"])


if __name__ == "__main__":
    unittest.main()
