from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_01


class SnapshotRefreshPublicSearchViewModelTests(unittest.TestCase):
    def test_live_metadata_projection_uses_candidate_cards(self) -> None:
        result = run_snapshot_refresh_01(from_live_metadata_pilot_examples=True)
        projection = result["public_search_view_model_projection"]
        cards = projection["result_cards"]

        self.assertEqual("snapshot_public_search_view_model_projection.v0", projection["schema_version"])
        self.assertTrue(projection["read_only"])
        self.assertFalse(projection["public_mutation_enabled"])
        self.assertFalse(projection["public_live_source_fanout_enabled"])
        self.assertTrue(projection["candidate_verified_separation_visible"])
        self.assertEqual(result["live_metadata_candidate_count"], len(cards))
        self.assertEqual(result["live_metadata_candidate_count"], projection["status_counts"]["candidate"])

        for card in cards:
            self.assertEqual("candidate", card["status"])
            self.assertFalse(card["accepted_truth"])
            self.assertTrue(card["review_required"])
            self.assertIn("no raw response", card["snippet"])


if __name__ == "__main__":
    unittest.main()
