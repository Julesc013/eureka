from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_02


class SnapshotRefreshReviewedPreviewSectionTests(unittest.TestCase):
    def test_preview_sections_remain_preview_only(self) -> None:
        result = run_snapshot_refresh_02(from_live_metadata_review_examples=True)
        metadata_section = result["reviewed_metadata_preview_section"]
        source_lead_section = result["reviewed_source_lead_preview_section"]

        self.assertEqual(1, metadata_section["preview_count"])
        self.assertEqual(2, source_lead_section["source_lead_preview_count"])

        for section in (metadata_section, source_lead_section):
            self.assertFalse(section["accepted_truth"])
            self.assertTrue(section["local_apply_required"])
            self.assertFalse(section["reviewed_index_mutated"])
            self.assertFalse(section["public_index_mutated"])
            for preview in section["previews"]:
                self.assertFalse(preview["accepted_truth"])
                self.assertTrue(preview["local_apply_required"])
                self.assertFalse(preview["review_preview_applied"])
                self.assertFalse(preview["verified_download_claim_created"])
                self.assertFalse(preview["malware_clean_claim_created"])
                self.assertFalse(preview["rights_clearance_claim_created"])

    def test_public_search_cards_do_not_verify_previews_as_artifacts(self) -> None:
        result = run_snapshot_refresh_02(from_live_metadata_review_examples=True)
        projection = result["public_search_view_model_projection"]

        self.assertTrue(projection["read_only"])
        self.assertEqual(3, projection["status_counts"]["source_lead"])
        self.assertFalse(projection["public_mutation_enabled"])
        self.assertFalse(projection["public_live_source_fanout_enabled"])

        for card in projection["result_cards"]:
            self.assertNotEqual("verified", card["status"])
            self.assertFalse(card["accepted_truth"])
            self.assertFalse(card.get("verified_download_claim_created", False))
            self.assertFalse(card.get("malware_clean_claim_created", False))
            self.assertFalse(card.get("rights_clearance_claim_created", False))


if __name__ == "__main__":
    unittest.main()
