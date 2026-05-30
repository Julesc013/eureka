from __future__ import annotations

import unittest

from runtime.review.batch import run_review_batch_from_examples


class ReviewBatchPromotionPreviewTests(unittest.TestCase):
    def test_accept_preview_builds_non_promoting_previews(self) -> None:
        preview = run_review_batch_from_examples(
            "accept_local_reviewed_preview",
            {"projection_profile": "operator_workbench", "operator_token": "local-dev-token", "dry_run": True},
        )["decision_preview"]
        self.assertGreaterEqual(len(preview["promotion_previews"]), 1)
        self.assertTrue(all(item["promotion_preview_is_not_promotion"] for item in preview["promotion_previews"]))
        self.assertTrue(all(item["accepted_truth"] is False for item in preview["promotion_previews"]))


if __name__ == "__main__":
    unittest.main()
