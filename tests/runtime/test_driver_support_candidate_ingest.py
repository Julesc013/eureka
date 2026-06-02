from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_driver_support


class DriverSupportCandidateIngestTests(unittest.TestCase):
    def test_candidate_summaries_are_review_only_metadata(self) -> None:
        result = run_seed_batch_driver_support(fixture=True)
        candidates = result["candidate_summaries"]
        self.assertEqual(16, len(candidates))
        self.assertTrue(all(item["review_required"] for item in candidates))
        self.assertTrue(all(item["accepted_truth"] is False for item in candidates))
        self.assertTrue(all("download" in item["blocked_actions"] for item in candidates))
        self.assertTrue(all(item["malware_clean_claim_created"] is False for item in candidates))
        self.assertTrue(all(item["compatibility_guarantee_created"] is False for item in candidates))


if __name__ == "__main__":
    unittest.main()
