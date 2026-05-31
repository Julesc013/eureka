import unittest

from runtime.seed_batches import run_live_metadata_pilot_batch


class LiveMetadataPilotCandidateIngestTests(unittest.TestCase):
    def test_fixture_candidates_are_review_only(self):
        result = run_live_metadata_pilot_batch(fixture=True)
        candidates = result["candidate_packet"]["candidates"]

        self.assertEqual(len(candidates), 8)
        self.assertTrue(all(candidate["accepted_truth"] is False for candidate in candidates))
        self.assertTrue(all(candidate["review_state"] == "needs_review" for candidate in candidates))
        self.assertTrue(result["review_batch_packet_created"])


if __name__ == "__main__":
    unittest.main()
