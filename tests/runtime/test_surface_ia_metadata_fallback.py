from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from evals.hard_queries.metadata_fallback_smoke.ia_00.loader import BASELINE_PROFILES, build_smoke_suite
from runtime.surface import SurfaceKernel, SurfaceRequest


REPO_ROOT = Path(__file__).resolve().parents[2]


class SurfaceIAMetadataFallbackTests(unittest.TestCase):
    def test_surface_renders_all_ia_fallback_states_through_baseline_renderers(self) -> None:
        suite = build_smoke_suite()
        expected = {
            "candidate_sound_blaster_manual": "candidate",
            "need_ray_tracing_magazine": "need",
            "near_miss_blue_ftp_client": "near_miss",
            "unavailable_firefox_malformed": "unavailable",
            "policy_blocked_disabled": "policy_blocked",
        }

        for case_id, expected_status in expected.items():
            for profile in BASELINE_PROFILES:
                with self.subTest(case_id=case_id, profile=profile):
                    projection = suite["cases"][case_id]["surface_projections"][profile]
                    output = projection["renderer_result"]["renderer_output"]

                    self.assertEqual(projection["view_model"]["canonical_status"], expected_status)
                    self.assertIn(expected_status, repr(output))
                    self.assertFalse(projection["surface_kernel_called_source_provider"])
                    self.assertFalse(projection["renderer_result"]["renderer_called_source_provider"])
                    self.assertFalse(projection["renderer_result"]["renderer_mutated_reviewed_index"])
                    self.assertFalse(projection["renderer_result"]["renderer_mutated_public_index"])
                    self.assertFalse(projection["renderer_result"]["renderer_mutated_master_index"])

    def test_public_projection_strips_operator_actions_from_ia_candidate(self) -> None:
        suite = build_smoke_suite()
        run = deepcopy(suite["cases"]["candidate_sound_blaster_manual"]["run"])
        fallback = run["fallback_summary"]
        fallback["public_action_posture"]["allowed"] = ["view", "inspect_evidence", "promote", "review_candidate"]
        fallback["candidates"][0]["public_actions"] = ["view", "promote", "download", "review_candidate"]

        projection = SurfaceKernel().project(
            SurfaceRequest(
                route_id="resolution_run",
                payload=run,
                requested_profile="json_v0",
                visibility_posture="public",
            )
        )

        filtered_fallback = projection["view_model"]["payload"]["fallback_summary"]
        candidate_actions = {
            item["action_id"]
            for item in filtered_fallback["candidates"][0]["public_actions"]
        }
        posture_actions = set(filtered_fallback["public_action_posture"]["allowed"])

        self.assertEqual(candidate_actions, {"view"})
        self.assertEqual(posture_actions, {"view", "inspect_evidence"})
        self.assertFalse(projection["view_model"]["reviewed_record_created"])
        self.assertFalse(projection["view_model"]["reviewed_index_mutated"])

    def test_html_renderer_escapes_unsafe_ia_metadata_title(self) -> None:
        projection = build_smoke_suite()["cases"]["candidate_sound_blaster_manual"]["surface_projections"]["html_basic_v0"]
        html = projection["renderer_result"]["renderer_output"]["content"]

        self.assertIn("Sound Blaster &lt;CT1740&gt; &quot;manual&quot; metadata candidate", html)
        self.assertNotIn('Sound Blaster <CT1740> "manual" metadata candidate', html)

    def test_snapshot_output_is_deterministic(self) -> None:
        first = build_smoke_suite()["cases"]["candidate_sound_blaster_manual"]["surface_projections"]["snapshot_v0"]
        second = build_smoke_suite()["cases"]["candidate_sound_blaster_manual"]["surface_projections"]["snapshot_v0"]

        self.assertEqual(first["renderer_result"]["renderer_output"], second["renderer_result"]["renderer_output"])
        digest = first["renderer_result"]["renderer_output"]["content"]["content_digest"]
        self.assertRegex(digest, r"^[0-9a-f]{24}$")

    def test_reviewed_and_verified_artifact_counts_remain_unchanged(self) -> None:
        suite = build_smoke_suite()

        self.assertEqual(suite["reviewed_artifact_records_created"], 0)
        self.assertEqual(suite["verified_artifacts_created"], 0)
        for case in suite["cases"].values():
            boundary = case["truth_boundary"]
            self.assertFalse(boundary["accepted_truth"])
            self.assertFalse(boundary["verified"])
            self.assertFalse(boundary["reviewed_record_created"])
            self.assertFalse(boundary["reviewed_index_mutated"])


if __name__ == "__main__":
    unittest.main()
