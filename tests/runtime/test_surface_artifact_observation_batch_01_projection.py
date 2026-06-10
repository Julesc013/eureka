from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.artifact_observations.batch_01 import (
    BASELINE_PROFILES,
    FORBIDDEN_PUBLIC_ACTIONS,
    load_artifact_observations,
    load_renderer_expected_outputs,
    load_surface_projection_fixtures,
    observation_records,
    project_artifact_observation,
    validate_renderer_expected_outputs,
    validate_surface_projection_fixtures,
)


class SurfaceArtifactObservationBatchOneProjectionTests(unittest.TestCase):
    def test_surface_and_renderer_fixtures_validate(self) -> None:
        observations = load_artifact_observations()

        self.assertEqual(validate_surface_projection_fixtures(load_surface_projection_fixtures(), observations), ())
        self.assertEqual(validate_renderer_expected_outputs(load_renderer_expected_outputs(), observations), ())

    def test_observations_project_honest_status_and_artifact_level(self) -> None:
        for observation in observation_records(load_artifact_observations()):
            for profile in BASELINE_PROFILES:
                with self.subTest(observation=observation["observation_id"], profile=profile):
                    result = project_artifact_observation(observation, profile)
                    fallback = result["view_model"]["payload"]["fallback_summary"]

                    self.assertEqual(result["view_model"]["canonical_status"], observation["public_projection_status"])
                    self.assertEqual(fallback["artifact_level"], observation["artifact_level"])
                    self.assertFalse(fallback["verified"])
                    self.assertFalse(fallback["accepted_truth"])
                    self.assertFalse(fallback["reviewed_artifact_record_created"])
                    self.assertFalse(result["surface_kernel_called_source_provider"])

    def test_public_projection_strips_operator_only_actions(self) -> None:
        for observation in observation_records(load_artifact_observations()):
            rendered = [project_artifact_observation(observation, profile) for profile in BASELINE_PROFILES]
            combined_output = repr([result["renderer_result"]["renderer_output"] for result in rendered])
            combined_view = repr([result["view_model"] for result in rendered])

            for action in FORBIDDEN_PUBLIC_ACTIONS:
                self.assertNotIn(action, combined_output, f"{observation['observation_id']} rendered {action}")
                self.assertNotIn(action, combined_view, f"{observation['observation_id']} view leaked {action}")

    def test_operator_projection_can_retain_review_actions(self) -> None:
        observation = next(
            item
            for item in observation_records(load_artifact_observations())
            if item["review_recommendation"] == "review_candidate"
        )
        result = project_artifact_observation(observation, "json_v0", visibility_posture="operator_private")

        self.assertIn("review_candidate", result["view_model"]["payload"]["fallback_summary"]["operator_actions"])

    def test_blocked_driver_projects_as_need(self) -> None:
        blocker = next(item for item in observation_records(load_artifact_observations()) if item["query_id"] == "hq_driver_win98")
        text = project_artifact_observation(blocker, "text_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("Status: need", text)
        self.assertIn("hardware_vendor", text)

    def test_html_renderer_escapes_observation_text(self) -> None:
        observation = deepcopy(observation_records(load_artifact_observations())[0])
        observation["artifact_subject"] = "7-Zip <Windows> \"package\""

        html = project_artifact_observation(observation, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;Windows&gt;", html)
        self.assertIn("&quot;package&quot;", html)
        self.assertNotIn("<Windows>", html)
        self.assertNotIn('"package"', html)

    def test_projection_does_not_call_sources_or_mutate_indexes(self) -> None:
        for observation in observation_records(load_artifact_observations()):
            for profile in BASELINE_PROFILES:
                result = project_artifact_observation(observation, profile)
                renderer = result["renderer_result"]

                self.assertFalse(result["surface_kernel_called_source_provider"])
                self.assertFalse(result["surface_kernel_mutated_reviewed_index"])
                self.assertFalse(result["surface_kernel_mutated_public_index"])
                self.assertFalse(result["surface_kernel_mutated_master_index"])
                self.assertFalse(renderer["renderer_called_source_provider"])
                self.assertFalse(renderer["renderer_created_verified_state"])
                self.assertFalse(renderer["renderer_mutated_reviewed_index"])
                self.assertFalse(renderer["renderer_mutated_public_index"])
                self.assertFalse(renderer["renderer_mutated_master_index"])


if __name__ == "__main__":
    unittest.main()
