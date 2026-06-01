from __future__ import annotations

import unittest

from runtime.review.live_metadata import run_live_metadata_candidate_review


class LiveMetadataSnapshotHandoffTests(unittest.TestCase):
    def test_snapshot_refresh_is_handoff_only(self) -> None:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)
        handoff = result["snapshot_refresh_handoff"]

        self.assertEqual("live_metadata_snapshot_refresh_handoff.v0", handoff["schema_version"])
        self.assertTrue(handoff["snapshot_refresh_handoff_only"])
        self.assertFalse(handoff["snapshot_refresh_executed"])
        self.assertTrue(handoff["requires_separate_snapshot_refresh_gate"])
        self.assertEqual(8, handoff["decision_counts"]["live_metadata_candidates_reviewed"])
        self.assertFalse(handoff["public_index_mutated"])


if __name__ == "__main__":
    unittest.main()
