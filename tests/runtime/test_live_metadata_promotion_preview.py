from __future__ import annotations

import unittest

from runtime.review.live_metadata import run_live_metadata_candidate_review


class LiveMetadataPromotionPreviewTests(unittest.TestCase):
    def test_promotion_previews_are_not_promotions(self) -> None:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)
        previews = result["promotion_previews"]

        self.assertEqual(3, len(previews))
        for preview in previews:
            self.assertTrue(preview["promotion_preview_is_not_promotion"])
            self.assertTrue(preview["local_apply_required"])
            self.assertFalse(preview["accepted_truth"])
            self.assertFalse(preview["reviewed_index_mutated"])
            self.assertFalse(preview["download_claim"])
            self.assertFalse(preview["malware_clean_claim"])
            self.assertFalse(preview["rights_clearance_claim"])

    def test_preview_kinds_are_limited(self) -> None:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)

        self.assertEqual(1, len(result["reviewed_metadata_record_previews"]))
        self.assertEqual(2, len(result["reviewed_source_lead_previews"]))


if __name__ == "__main__":
    unittest.main()
