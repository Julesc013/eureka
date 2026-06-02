from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_01, run_snapshot_refresh_04


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

    def test_manuals_driver_projection_keeps_seed_domains_as_candidates(self) -> None:
        result = run_snapshot_refresh_04(from_manuals_driver_examples=True)
        projection = result["public_search_view_model_projection"]

        self.assertTrue(projection["read_only"])
        self.assertEqual(68, projection["status_counts"]["candidate"])
        self.assertEqual(3, projection["status_counts"]["source_lead"])
        self.assertTrue(projection["manuals_scans_cards_remain_candidates"])
        self.assertTrue(projection["driver_support_cards_remain_candidates"])

        domain_cards = [
            card
            for card in projection["result_cards"]
            if card["object_type"] in {"manuals_scans_candidate", "driver_support_candidate"}
        ]
        self.assertEqual(32, len(domain_cards))
        for card in domain_cards:
            self.assertEqual("candidate", card["status"])
            self.assertFalse(card["artifact_verified"])
            self.assertFalse(card["verified_download_claim"])
            self.assertFalse(card["rights_clearance_claim"])


if __name__ == "__main__":
    unittest.main()
