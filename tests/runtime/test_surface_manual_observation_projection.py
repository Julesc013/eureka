from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries.manual_observations.batch_00 import (
    BASELINE_PROFILES,
    load_observations,
    observation_records,
    project_observation,
)


FORBIDDEN_PUBLIC_ACTIONS = (
    "review_candidate",
    "promote",
    "reject",
    "supersede",
    "request_more_evidence",
    "rebuild_index",
    "freeze_review",
    "download",
    "install",
    "launch_emulator",
    "run_extraction",
    "submit_direct_evidence",
    "crawl_source",
    "arbitrary_live_lookup",
)


class SurfaceManualObservationProjectionTests(unittest.TestCase):
    def test_manual_observations_project_honest_statuses(self) -> None:
        for observation in observation_records(load_observations()):
            for profile in BASELINE_PROFILES:
                with self.subTest(observation_id=observation["observation_id"], profile=profile):
                    result = project_observation(observation, profile)
                    output = result["renderer_result"]["renderer_output"]

                    self.assertEqual(result["view_model"]["canonical_status"], observation["proposed_status"])
                    self.assertIn(observation["proposed_status"], repr(output))
                    fallback = result["view_model"]["payload"]["fallback_summary"]
                    self.assertFalse(fallback["verified"])
                    self.assertFalse(fallback["accepted_truth"])
                    self.assertNotEqual(result["view_model"]["canonical_status"], "verified")

    def test_public_projection_strips_operator_only_actions(self) -> None:
        for observation in observation_records(load_observations()):
            rendered = [project_observation(observation, profile) for profile in BASELINE_PROFILES]
            combined_output = repr([result["renderer_result"]["renderer_output"] for result in rendered])
            combined_view = repr([result["view_model"] for result in rendered])

            for action in FORBIDDEN_PUBLIC_ACTIONS:
                self.assertNotIn(action, combined_output, f"{observation['observation_id']} rendered {action}")
                self.assertNotIn(action, combined_view, f"{observation['observation_id']} view leaked {action}")

    def test_operator_projection_can_retain_review_handoff_actions(self) -> None:
        observation = next(item for item in observation_records(load_observations()) if item["query_id"] == "hq_firefox_last_xp")
        result = project_observation(observation, "json_v0", visibility_posture="operator_private")

        fallback = result["view_model"]["payload"]["fallback_summary"]
        self.assertIn("review_candidate", fallback["operator_actions"])
        self.assertIn("promote", fallback["operator_actions"])
        self.assertEqual(result["view_model"]["visibility_posture"], "operator_private")

    def test_unavailable_and_need_states_remain_visible(self) -> None:
        observations = {item["proposed_status"]: item for item in observation_records(load_observations())}

        need_text = project_observation(observations["need"], "text_v0")["renderer_result"]["renderer_output"]["content"]
        unavailable_text = project_observation(observations["unavailable"], "text_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("Status: need", need_text)
        self.assertIn("hardware_vendor", need_text)
        self.assertIn("Status: unavailable", unavailable_text)
        self.assertIn("manual_source_locator", unavailable_text)

    def test_policy_blocked_status_projects_honestly_when_supplied(self) -> None:
        observation = deepcopy(observation_records(load_observations())[0])
        observation["proposed_status"] = "policy_blocked"
        observation["review_blockers"] = ["policy_gate_example"]

        for profile in BASELINE_PROFILES:
            result = project_observation(observation, profile)
            self.assertEqual(result["view_model"]["canonical_status"], "policy_blocked")
            self.assertIn("policy_blocked", repr(result["renderer_result"]["renderer_output"]))

    def test_html_renderer_escapes_manual_observation_text(self) -> None:
        near_miss = next(item for item in observation_records(load_observations()) if item["proposed_status"] == "near_miss")
        html = project_observation(near_miss, "html_basic_v0")["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;client&gt;", html)
        self.assertIn("&quot;Blue&quot;", html)
        self.assertNotIn("<client>", html)
        self.assertNotIn('"Blue"', html)

    def test_snapshot_output_is_deterministic(self) -> None:
        observation = observation_records(load_observations())[0]

        first = project_observation(observation, "snapshot_v0")["renderer_result"]["renderer_output"]
        second = project_observation(observation, "snapshot_v0")["renderer_result"]["renderer_output"]

        self.assertEqual(first, second)
        self.assertEqual(first["content"]["canonical_status"], "candidate")

    def test_projection_does_not_call_sources_or_mutate_indexes(self) -> None:
        for observation in observation_records(load_observations()):
            for profile in BASELINE_PROFILES:
                result = project_observation(observation, profile)
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
