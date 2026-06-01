from __future__ import annotations

import unittest

from runtime.review.live_metadata import run_live_metadata_candidate_review


class LiveMetadataReviewBoundaryTests(unittest.TestCase):
    def test_boundaries_are_false(self) -> None:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)
        boundary = result["boundary_report"]

        for key in (
            "new_live_source_calls_performed",
            "raw_live_response_committed",
            "verified_download_claim_created",
            "malware_clean_claim_created",
            "rights_clearance_claim_created",
            "accepted_truth_created",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
