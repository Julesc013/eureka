from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_02


class PublicAlphaReassessReviewPreviewTests(unittest.TestCase):
    def test_review_preview_metrics_do_not_count_as_reviewed_records(self) -> None:
        result = run_public_alpha_reassess_02(from_live_metadata_review_refresh_examples=True)

        self.assertEqual("PUBLIC-ALPHA-REASSESS-02", result["task"])
        self.assertEqual(1, result["reviewed_record_count"])
        self.assertEqual(28, result["fixture_candidate_count"])
        self.assertEqual(8, result["live_metadata_candidate_count"])
        self.assertEqual(36, result["total_candidate_count"])
        self.assertEqual(1, result["reviewed_metadata_record_preview_count"])
        self.assertEqual(2, result["reviewed_source_lead_preview_count"])
        self.assertEqual(1, result["useful_lead_count"])
        self.assertEqual(2, result["needs_more_evidence_count"])
        self.assertEqual(2, result["rejected_or_duplicate_count"])
        self.assertFalse(result["launch_recommended"])
        self.assertTrue(result["demo_mode_recommended"])
        self.assertTrue(result["internal_review_recommended"])
        self.assertTrue(result["needs_local_apply_of_review_previews"])
        self.assertTrue(result["needs_snapshot_refresh_after_apply"])
        self.assertTrue(result["needs_public_alpha_reassess_after_apply"])

    def test_review_previews_remain_preview_only(self) -> None:
        result = run_public_alpha_reassess_02(from_live_metadata_review_refresh_examples=True)
        previews = result["review_preview_usefulness"]

        self.assertEqual(3, previews["review_preview_count"])
        self.assertFalse(previews["review_previews_counted_as_reviewed_records"])
        self.assertFalse(previews["review_previews_applied"])
        self.assertTrue(previews["local_apply_required"])
        self.assertTrue(previews["prohibited_claims_absent"])
        self.assertEqual(1, result["metrics"]["reviewed_record_count"])

    def test_public_search_view_model_preview_signals_are_available(self) -> None:
        result = run_public_alpha_reassess_02(from_live_metadata_review_refresh_examples=True)
        view_models = result["public_search_view_models"]

        self.assertTrue(view_models["public_search_view_models_available"])
        self.assertTrue(view_models["required_states_available"])
        self.assertTrue(view_models["preview_related_cards_available"])
        self.assertTrue(view_models["review_previews_visible_as_source_leads"])
        self.assertFalse(view_models["launch_sufficient"])

    def test_boundary_flags_remain_false(self) -> None:
        result = run_public_alpha_reassess_02(from_live_metadata_review_refresh_examples=True)

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
            "live_metadata_candidate_promoted",
            "review_preview_applied",
            "raw_live_response_included",
            "verified_download_claim_created",
            "malware_clean_claim_created",
            "rights_clearance_claim_created",
        ):
            self.assertFalse(result["boundary_report"][key], key)


if __name__ == "__main__":
    unittest.main()
