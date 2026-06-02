from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_05


class PublicAlphaReassessPublicSearchUxMvpTests(unittest.TestCase):
    def test_public_search_ux_mvp_metrics_and_decision(self) -> None:
        result = run_public_alpha_reassess_05(from_public_search_ux_projection_examples=True)

        self.assertEqual("pass", result["status"])
        self.assertEqual(1, result["existing_reviewed_record_count"])
        self.assertEqual(1, result["reviewed_metadata_record_count"])
        self.assertEqual(2, result["reviewed_source_lead_count"])
        self.assertEqual(4, result["total_limited_reviewed_record_projection_count"])
        self.assertEqual(68, result["candidate_count"])
        self.assertEqual(4, result["domain_count"])
        self.assertEqual(8, result["public_ux_routes_count"])
        self.assertEqual(8, result["result_card_states_count"])
        self.assertTrue(result["public_search_ux_mvp_verified"])
        self.assertFalse(result["launch_recommended"])

    def test_public_search_ux_mvp_boundaries(self) -> None:
        result = run_public_alpha_reassess_05(from_public_search_ux_projection_examples=True)

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
            "compatibility_guarantee_created",
            "rights_clearance_claim_created",
            "scan_completeness_claim_created",
            "ocr_quality_claim_created",
        ):
            self.assertFalse(result["boundary_report"][key], key)


if __name__ == "__main__":
    unittest.main()
