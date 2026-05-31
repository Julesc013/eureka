from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh


class SnapshotRefreshRelayProjectionTests(unittest.TestCase):
    def test_relay_projection_is_read_only_preview(self) -> None:
        projection = run_snapshot_refresh(from_seed_examples=True)["refreshed_relay_projection"]

        self.assertTrue(projection["read_only"])
        self.assertFalse(projection["mutation_enabled"])
        self.assertFalse(projection["live_source_actions_enabled"])
        self.assertFalse(projection["download_enabled"])
        self.assertFalse(projection["deployment_performed"])
        self.assertTrue(projection["query_previews"])


if __name__ == "__main__":
    unittest.main()
