from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_manuals_scans


class ManualsScansBoundaryTests(unittest.TestCase):
    def test_no_document_fetch_or_quality_claim_boundaries(self) -> None:
        result = run_seed_batch_manuals_scans(fixture=True)
        for key in (
            "accepted_truth_created",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "download_performed",
            "file_fetch_performed",
            "ocr_performed",
            "extraction_executed",
            "rights_clearance_claim_created",
            "scan_completeness_claim_created",
            "ocr_quality_claim_created",
            "deployment_performed",
        ):
            self.assertFalse(result[key], key)


if __name__ == "__main__":
    unittest.main()
