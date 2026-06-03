from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_06


class PublicAlphaReassessLaunchBlockerTests(unittest.TestCase):
    def test_resilience_and_launch_blockers_are_recorded(self) -> None:
        result = run_public_alpha_reassess_06(from_review_batch_apply_refresh_examples=True)
        blocker_ids = {blocker["blocker_id"] for blocker in result["launch_blockers"]["blockers"]}

        self.assertIn("reviewed_record_count_below_threshold", blocker_ids)
        self.assertIn("limited_reviewed_records_are_not_verified_artifacts", blocker_ids)
        self.assertIn("indexless_live_fallback_missing", blocker_ids)
        self.assertIn("search_usefulness_eval_missing", blocker_ids)
        self.assertIn("no_external_full_discovery_after_current_dev_stack", blocker_ids)
        self.assertFalse(result["indexless_live_fallback_implemented"])
        self.assertFalse(result["search_usefulness_eval_implemented"])
        self.assertTrue(result["needs_indexless_live_search_fallback"])
        self.assertTrue(result["needs_search_usefulness_eval"])
        self.assertTrue(result["needs_external_full_discovery"])
        self.assertTrue(result["needs_main_promotion_before_launch"])
        self.assertTrue(result["needs_public_alpha_launch_approval"])

    def test_boundaries_remain_false(self) -> None:
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
