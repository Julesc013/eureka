from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_manuals_scans


class SeedBatchManualsScansTests(unittest.TestCase):
    def test_fixture_batch_builds_full_packet(self) -> None:
        result = run_seed_batch_manuals_scans(fixture=True)
        self.assertTrue(result["fixture_seed_batch_passed"])
        self.assertEqual(16, result["query_count"])
        self.assertEqual(16, result["candidate_count"])
        self.assertFalse(result["accepted_truth"])
        self.assertFalse(result["reviewed_index_mutated"])
        self.assertFalse(result["file_fetch_performed"])
        self.assertFalse(result["ocr_performed"])


if __name__ == "__main__":
    unittest.main()
