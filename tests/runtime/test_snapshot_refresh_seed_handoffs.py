from __future__ import annotations

import unittest

from runtime.snapshots import build_snapshot_refresh_plan, load_seed_batch_handoffs


class SnapshotRefreshSeedHandoffTests(unittest.TestCase):
    def test_seed_handoffs_load_frontier_and_legacy_batches(self) -> None:
        handoffs = load_seed_batch_handoffs()
        plan = build_snapshot_refresh_plan(handoffs)

        self.assertEqual(2, handoffs["source_batch_count"])
        self.assertIn("seed_batch_frontier_media_00", [item["batch_id"] for item in plan["source_batches"]])
        self.assertIn("seed_batch_legacy_software_00", [item["batch_id"] for item in plan["source_batches"]])


if __name__ == "__main__":
    unittest.main()
