from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_03


class PublicAlphaReassessLocalApplyTests(unittest.TestCase):
    def test_limited_reviewed_record_metrics_do_not_recommend_launch(self) -> None:
        result = run_public_alpha_reassess_03(from_local_apply_live_metadata_refresh_examples=True)

        self.assertEqual("PUBLIC-ALPHA-REASSESS-03", result["task"])
        self.assertEqual(1, result["existing_reviewed_record_count"])
        self.assertEqual(1, result["reviewed_metadata_record_count"])
        self.assertEqual(2, result["reviewed_source_lead_count"])
        self.assertEqual(3, result["reviewed_record_delta_count"])
        self.assertEqual(4, result["total_limited_reviewed_record_projection_count"])
        self.assertEqual(28, result["fixture_candidate_count"])
        self.assertEqual(8, result["live_metadata_candidate_count"])
        self.assertEqual(36, result["total_candidate_count"])
        self.assertFalse(result["launch_recommended"])
        self.assertTrue(result["demo_mode_recommended"])
        self.assertTrue(result["internal_review_recommended"])

    def test_limited_records_are_not_verified_artifacts(self) -> None:
        result = run_public_alpha_reassess_03(from_local_apply_live_metadata_refresh_examples=True)
        limited = result["limited_reviewed_record_usefulness"]

        self.assertTrue(limited["limited_reviewed_records_count_for_usefulness"])
        self.assertFalse(limited["limited_reviewed_records_are_verified_artifacts"])
        self.assertFalse(limited["artifact_verified"])
        self.assertFalse(limited["verified_download_claim"])
        self.assertFalse(limited["malware_clean_claim"])
        self.assertFalse(limited["rights_clearance_claim"])
        self.assertTrue(result["needs_more_reviewed_artifact_records"])

    def test_next_work_keeps_launch_deferred(self) -> None:
        result = run_public_alpha_reassess_03(from_local_apply_live_metadata_refresh_examples=True)

        self.assertTrue(result["needs_more_reviewed_records"])
        self.assertTrue(result["needs_more_domains"])
        self.assertTrue(result["needs_more_seed_batches"])
        self.assertTrue(result["needs_seed_batch_manuals_scans"])
        self.assertTrue(result["needs_seed_batch_driver_support"])
        self.assertIn("SEED-BATCH-MANUALS-SCANS-00", result["recommended_next_task"])

    def test_public_search_view_model_has_distinct_limited_record_cards(self) -> None:
        result = run_public_alpha_reassess_03(from_local_apply_live_metadata_refresh_examples=True)
        view_models = result["public_search_view_models"]

        self.assertTrue(view_models["public_search_view_models_available"])
        self.assertTrue(view_models["required_states_available"])
        self.assertEqual(1, view_models["reviewed_metadata_record_cards"])
        self.assertEqual(2, view_models["reviewed_source_lead_cards"])
        self.assertTrue(view_models["limited_reviewed_records_visible"])
        self.assertTrue(view_models["limited_records_distinct_from_verified_artifacts"])
        self.assertFalse(view_models["launch_sufficient"])

    def test_boundary_flags_remain_false(self) -> None:
        result = run_public_alpha_reassess_03(from_local_apply_live_metadata_refresh_examples=True)

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
            "operator_instance_mutated",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "artifact_verified_claim_created",
            "verified_download_claim_created",
            "malware_clean_claim_created",
            "rights_clearance_claim_created",
        ):
            self.assertFalse(result["boundary_report"][key], key)


if __name__ == "__main__":
    unittest.main()
