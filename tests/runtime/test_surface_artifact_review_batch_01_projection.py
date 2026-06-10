from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.artifact_observations.batch_01 import BASELINE_PROFILES, FORBIDDEN_PUBLIC_ACTIONS
from evals.hard_queries.artifact_reviews.batch_01 import (
    load_review_decision_backed_outcomes,
    outcome_records,
    project_review_outcome,
)


class SurfaceArtifactReviewBatchOneProjectionTests(unittest.TestCase):
    def test_review_outcomes_project_status_and_truth_boundary(self) -> None:
        for outcome in outcome_records(load_review_decision_backed_outcomes()):
            for profile in BASELINE_PROFILES:
                with self.subTest(outcome=outcome["outcome_id"], profile=profile):
                    result = project_review_outcome(outcome, profile)
                    payload = result["view_model"]["payload"]

                    self.assertEqual(result["view_model"]["canonical_status"], outcome["outcome_status"])
                    self.assertEqual(payload["artifact_claim_status"], outcome["artifact_claim_status"])
                    self.assertFalse(payload["verified_artifact"])
                    self.assertFalse(result["surface_kernel_called_source_provider"])
                    self.assertFalse(result["surface_kernel_mutated_reviewed_index"])
                    self.assertFalse(result["surface_kernel_mutated_public_index"])
                    self.assertFalse(result["surface_kernel_mutated_master_index"])

    def test_reviewed_record_outcomes_are_not_verified_artifacts(self) -> None:
        promoted = [item for item in outcome_records(load_review_decision_backed_outcomes()) if item["decision"] == "promote"]

        self.assertEqual(len(promoted), 2)
        for outcome in promoted:
            result = project_review_outcome(outcome, "json_v0")
            payload = result["view_model"]["payload"]

            self.assertEqual(result["view_model"]["canonical_status"], "verified")
            self.assertEqual(payload["artifact_claim_status"], "reviewed_artifact_record")
            self.assertFalse(payload["verified_artifact"])

    def test_public_projection_strips_operator_only_actions(self) -> None:
        action_ids = []
        for outcome in outcome_records(load_review_decision_backed_outcomes()):
            for profile in BASELINE_PROFILES:
                result = project_review_outcome(outcome, profile)
                action_ids.extend(action["action_id"] for action in result["view_model"]["actions"])

        for action in FORBIDDEN_PUBLIC_ACTIONS:
            self.assertNotIn(action, action_ids)

    def test_html_renderer_escapes_review_outcome_text(self) -> None:
        outcome = deepcopy(outcome_records(load_review_decision_backed_outcomes())[0])
        outcome["title"] = "7-Zip <Windows> \"identity\""

        html = project_review_outcome(outcome, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;Windows&gt;", html)
        self.assertIn("&quot;identity&quot;", html)
        self.assertNotIn("<Windows>", html)
        self.assertNotIn('"identity"', html)

    def test_renderer_does_not_call_sources_or_mutate_indexes(self) -> None:
        for outcome in outcome_records(load_review_decision_backed_outcomes()):
            for profile in BASELINE_PROFILES:
                result = project_review_outcome(outcome, profile)
                renderer = result["renderer_result"]

                self.assertFalse(renderer["renderer_called_source_provider"])
                self.assertFalse(renderer["renderer_created_verified_state"])
                self.assertFalse(renderer["renderer_mutated_reviewed_index"])
                self.assertFalse(renderer["renderer_mutated_public_index"])
                self.assertFalse(renderer["renderer_mutated_master_index"])


if __name__ == "__main__":
    unittest.main()
