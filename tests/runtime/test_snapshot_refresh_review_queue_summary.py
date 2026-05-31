from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh


class SnapshotRefreshReviewQueueTests(unittest.TestCase):
    def test_review_queue_summary_keeps_operator_gate(self) -> None:
        result = run_snapshot_refresh(from_seed_examples=True)
        section = result["review_queue_section"]

        self.assertEqual(result["candidate_count"], section["candidate_count"])
        self.assertTrue(section["operator_context_required"])
        self.assertTrue(section["review_required"])
        self.assertFalse(section["candidate_promoted_to_reviewed"])


if __name__ == "__main__":
    unittest.main()
