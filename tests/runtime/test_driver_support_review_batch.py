from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_driver_support


class DriverSupportReviewBatchTests(unittest.TestCase):
    def test_review_batch_packet_and_handoffs_build(self) -> None:
        result = run_seed_batch_driver_support(fixture=True)
        review = result["review_packets"]
        self.assertTrue(review["review_batch_refs"])
        self.assertTrue(review["promotion_preview_refs"])
        self.assertTrue(review["local_apply_handoff_refs"])
        self.assertTrue(review["snapshot_refresh_handoff_refs"])
        self.assertFalse(review["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
