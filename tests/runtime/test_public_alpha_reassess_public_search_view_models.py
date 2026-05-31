from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_01


class PublicAlphaReassessPublicSearchViewModelTests(unittest.TestCase):
    def test_public_search_view_model_states_are_available(self) -> None:
        result = run_public_alpha_reassess_01(from_live_metadata_refresh_examples=True)
        view_models = result["public_search_view_models"]

        self.assertTrue(view_models["public_search_view_models_available"])
        self.assertTrue(view_models["required_states_available"])
        self.assertTrue(view_models["candidate_verified_separation_visible"])
        self.assertEqual("candidate", view_models["live_metadata_candidate_status"])
        self.assertFalse(view_models["launch_sufficient"])
        self.assertFalse(view_models["public_mutation_enabled"])

    def test_boundary_flags_remain_false(self) -> None:
        result = run_public_alpha_reassess_01(from_live_metadata_refresh_examples=True)

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
        ):
            self.assertFalse(result["boundary_report"][key], key)


if __name__ == "__main__":
    unittest.main()

