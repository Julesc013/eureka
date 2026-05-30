from __future__ import annotations

import unittest

from runtime.review.batch import run_review_batch_from_examples


class ReviewBatchRuntimeTests(unittest.TestCase):
    def test_builds_review_batch_from_examples(self) -> None:
        result = run_review_batch_from_examples()
        self.assertEqual("pass", result["status"])
        self.assertGreaterEqual(result["cluster_count"], 1)
        self.assertFalse(result["accepted_truth"])
        self.assertFalse(result["reviewed_index_mutated"])


if __name__ == "__main__":
    unittest.main()
