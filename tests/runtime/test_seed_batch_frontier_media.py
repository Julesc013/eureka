from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_frontier_media


class SeedBatchFrontierMediaTests(unittest.TestCase):
    def test_fixture_batch_builds_full_packet(self) -> None:
        result = run_seed_batch_frontier_media(fixture=True)
        self.assertTrue(result["fixture_seed_batch_passed"])
        self.assertEqual(12, result["query_count"])
        self.assertEqual(12, result["candidate_count"])
        self.assertFalse(result["accepted_truth"])
        self.assertFalse(result["reviewed_index_mutated"])


if __name__ == "__main__":
    unittest.main()
