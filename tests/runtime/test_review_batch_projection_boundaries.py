from __future__ import annotations

import unittest

from runtime.review.batch import project_review_batch, run_review_batch_from_examples


class ReviewBatchProjectionBoundaryTests(unittest.TestCase):
    def test_public_projection_is_read_only(self) -> None:
        packet = run_review_batch_from_examples()["review_batch_packet"]
        projection = project_review_batch(packet, "public_web")
        self.assertTrue(projection["read_only"])
        self.assertFalse(projection["decision_actions_visible"])
        self.assertFalse(projection["public_mutation_enabled"])


if __name__ == "__main__":
    unittest.main()
