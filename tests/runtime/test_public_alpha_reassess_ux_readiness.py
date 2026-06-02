from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_04


class PublicAlphaReassessUxReadinessTests(unittest.TestCase):
    def test_public_search_view_models_are_not_public_ux_mvp(self) -> None:
        result = run_public_alpha_reassess_04(from_manuals_driver_snapshot_examples=True)
        ux = result["ux_readiness"]

        self.assertTrue(result["public_search_view_models_available"])
        self.assertFalse(result["public_search_ux_mvp_implemented"])
        self.assertEqual("missing", ux["ux_mvp_status"])
        self.assertTrue(ux["public_search_view_models_are_not_full_public_ux"])
        self.assertTrue(result["needs_public_search_ux_mvp"])
        self.assertTrue(result["needs_snapshot_refresh_after_ux"])
        self.assertTrue(result["needs_public_alpha_reassess_after_ux"])
        self.assertIn("PUBLIC-SEARCH-UX-MVP-00", result["recommended_next_task"])

    def test_ux_reassessment_keeps_non_claim_boundaries(self) -> None:
        result = run_public_alpha_reassess_04(from_manuals_driver_snapshot_examples=True)

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
            "artifact_verified_claim_created",
            "verified_download_claim_created",
            "malware_clean_claim_created",
            "compatibility_guarantee_created",
            "rights_clearance_claim_created",
            "scan_completeness_claim_created",
            "ocr_quality_claim_created",
        ):
            self.assertFalse(result["boundary_report"][key], key)


if __name__ == "__main__":
    unittest.main()
