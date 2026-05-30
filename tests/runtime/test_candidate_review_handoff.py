from __future__ import annotations

import unittest

from runtime.candidate_store import build_candidate_review_handoff, sample_candidate_index


class CandidateReviewHandoffTest(unittest.TestCase):
    def test_review_handoff_is_not_promotion(self) -> None:
        candidate = sample_candidate_index()["candidates"][0]
        handoff = build_candidate_review_handoff(candidate)

        self.assertEqual(handoff["candidate_id"], candidate["candidate_id"])
        self.assertTrue(handoff["review_required"])
        self.assertFalse(handoff["accepted_truth"])
        self.assertTrue(handoff["promotion_requires_review"])
        self.assertFalse(handoff["reviewed_index_mutated"])


if __name__ == "__main__":
    unittest.main()
