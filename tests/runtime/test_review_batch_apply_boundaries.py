from __future__ import annotations

import unittest

from runtime.local_apply import run_review_batch_apply_next


class ReviewBatchApplyBoundariesTests(unittest.TestCase):
    def test_boundary_flags_remain_false(self) -> None:
        result = run_review_batch_apply_next(from_examples=True, use_temp_instance=True)
        boundary = result["boundary_report"]

        for key in (
            "operator_instance_mutated",
            "committed_instance_state",
            "public_index_mutated",
            "master_index_mutated",
            "artifact_verified_claim_created",
            "verified_download_claim_created",
            "malware_clean_claim_created",
            "rights_clearance_claim_created",
            "download_performed",
            "file_fetch_performed",
            "ocr_performed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
