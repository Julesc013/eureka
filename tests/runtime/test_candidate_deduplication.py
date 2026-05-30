from __future__ import annotations

import unittest

from runtime.candidate_store import dedupe_candidates, sample_candidate_index


class CandidateDeduplicationTest(unittest.TestCase):
    def test_duplicate_candidate_is_marked_not_accepted(self) -> None:
        candidate = sample_candidate_index()["candidates"][0]
        duplicate = dict(candidate)
        duplicate["candidate_id"] = "duplicate_candidate"

        result = dedupe_candidates([candidate, duplicate])

        self.assertEqual(result["unique_count"], 1)
        self.assertEqual(result["duplicate_count"], 1)
        self.assertEqual(result["duplicate_candidates"][0]["review_state"], "duplicate")
        self.assertFalse(result["accepted_truth_created"])
        self.assertFalse(result["reviewed_index_mutated"])


if __name__ == "__main__":
    unittest.main()
