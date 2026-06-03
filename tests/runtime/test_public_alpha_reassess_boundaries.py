from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess, run_public_alpha_reassess_06


class PublicAlphaReassessBoundaryTests(unittest.TestCase):
    def test_reassessment_does_not_claim_or_mutate(self) -> None:
        result = run_public_alpha_reassess(from_snapshot_refresh_examples=True)
        boundary = result["boundary_report"]

        for key in (
            "deployment_performed",
            "public_launch_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "site_dist_written",
            "public_mutation_enabled",
            "public_live_source_fanout_enabled",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
            "live_source_call_performed",
            "accepted_truth_created",
            "candidate_promoted_to_reviewed",
        ):
            self.assertFalse(boundary[key], key)

    def test_review_batch_apply_reassessment_does_not_claim_or_mutate(self) -> None:
        result = run_public_alpha_reassess_06(from_review_batch_apply_refresh_examples=True)
        boundary = result["boundary_report"]

        for key in (
            "deployment_performed",
            "public_launch_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "site_dist_written",
            "public_mutation_enabled",
            "public_live_source_fanout_enabled",
            "download_performed",
            "file_fetch_performed",
            "ocr_performed",
            "extraction_executed",
            "install_execution_enabled",
            "model_provider_used",
            "live_source_call_performed",
            "accepted_truth_created",
            "candidate_promoted_to_reviewed",
            "artifact_verified_claim_created",
            "verified_download_claim_created",
            "malware_clean_claim_created",
            "compatibility_guarantee_claim_created",
            "rights_clearance_claim_created",
            "scan_completeness_claim_created",
            "ocr_quality_claim_created",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
