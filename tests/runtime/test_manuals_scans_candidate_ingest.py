from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_manuals_scans


class ManualsScansCandidateIngestTests(unittest.TestCase):
    def test_candidate_index_is_metadata_only(self) -> None:
        result = run_seed_batch_manuals_scans(fixture=True)
        candidate_index = result["candidate_index"]
        self.assertEqual(16, candidate_index["candidate_count"])
        for candidate in candidate_index["candidates"]:
            self.assertEqual("manuals_docs_scans", candidate["domain_id"])
            self.assertFalse(candidate["accepted_truth"])
            self.assertIn("no_file_fetch", candidate["limitations"])
            self.assertIn("no_ocr", candidate["limitations"])


if __name__ == "__main__":
    unittest.main()
