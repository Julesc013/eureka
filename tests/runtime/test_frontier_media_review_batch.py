from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_frontier_media


class FrontierMediaReviewBatchTests(unittest.TestCase):
    def test_review_batch_packet_and_handoffs_are_previews(self) -> None:
        result = run_seed_batch_frontier_media(fixture=True)
        review = result["review_packets"]
        self.assertTrue(review["review_batch_packet"]["candidate_refs"])
        preview = review["decision_preview"]
        self.assertFalse(preview["batch_decision_applied"])
        self.assertFalse(preview["local_apply_executed"])
        self.assertFalse(preview["snapshot_refresh_executed"])


if __name__ == "__main__":
    unittest.main()
