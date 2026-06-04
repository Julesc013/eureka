from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries import BASELINE_PROFILES, fixture_case_by_query_id, fixture_cases, render_fixture_case


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


class SurfaceHardQueryEvalTests(unittest.TestCase):
    def test_fixture_statuses_remain_honest_across_renderers(self) -> None:
        for fixture in fixture_cases():
            rendered = render_fixture_case(fixture)
            for profile in BASELINE_PROFILES:
                with self.subTest(query_id=fixture["query_id"], profile=profile):
                    result = rendered[profile]
                    output = result["renderer_result"]["renderer_output"]

                    self.assertEqual(result["view_model"]["canonical_status"], fixture["expected_status"])
                    self.assertIn(fixture["expected_status"], repr(output))
                    self.assertFalse(result["view_model"]["payload"]["fallback_summary"]["verified"])
                    self.assertNotEqual(fixture["expected_status"], "verified")

    def test_public_renderer_output_strips_operator_and_future_actions(self) -> None:
        for fixture in fixture_cases():
            rendered = render_fixture_case(fixture)
            combined = repr([result["renderer_result"]["renderer_output"] for result in rendered.values()])

            for action in FORBIDDEN_PUBLIC_ACTIONS:
                self.assertNotIn(action, combined, f"{fixture['query_id']} leaked {action}")
            for result in rendered.values():
                action_ids = {item["action_id"] for item in result["view_model"]["actions"]}
                self.assertTrue(action_ids.issubset({"view", "inspect_evidence", "compare", "cite", "export_manifest"}))

    def test_html_renderer_escapes_hard_query_fixture_text(self) -> None:
        fixture = fixture_case_by_query_id("hq_blue_ftp_client_xp")
        html = render_fixture_case(fixture)["html_basic_v0"]["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;client&gt;", html)
        self.assertIn("&quot;blue&quot;", html)
        self.assertNotIn("<client>", html)
        self.assertNotIn('"blue"', html)

    def test_snapshot_output_is_deterministic_for_same_fixture(self) -> None:
        fixture = fixture_case_by_query_id("hq_windows_7_apps")

        first = render_fixture_case(fixture)["snapshot_v0"]["renderer_result"]["renderer_output"]
        second = render_fixture_case(fixture)["snapshot_v0"]["renderer_result"]["renderer_output"]

        self.assertEqual(first, second)
        self.assertEqual(first["content"]["canonical_status"], "candidate")

    def test_json_and_text_outputs_expose_status_and_uncertainty(self) -> None:
        fixture = fixture_case_by_query_id("hq_driver_win98")
        rendered = render_fixture_case(fixture)
        json_output = rendered["json_v0"]["renderer_result"]["renderer_output"]
        text_output = rendered["text_v0"]["renderer_result"]["renderer_output"]["content"]

        self.assertEqual(json_output["content"]["status"], "need")
        self.assertIn("Status: need", text_output)
        self.assertIn("hardware_identifier_missing", text_output)
        self.assertIn("Need vendor and device model", text_output)

    def test_unknown_status_degrades_honestly(self) -> None:
        fixture = fixture_case_by_query_id("hq_ray_tracing_1994_magazine")
        unknown_fixture = deepcopy(fixture)
        unknown_fixture["expected_status"] = "unknown"
        unknown_fixture["fallback_summary"]["status"] = "not_a_known_status"

        rendered = render_fixture_case(unknown_fixture)

        for profile in BASELINE_PROFILES:
            self.assertEqual(rendered[profile]["view_model"]["canonical_status"], "unknown")
            self.assertIn("unknown", repr(rendered[profile]["renderer_result"]["renderer_output"]))

    def test_eval_surface_path_does_not_call_sources_or_mutate_indexes(self) -> None:
        for fixture in fixture_cases():
            rendered = render_fixture_case(fixture)
            for profile, result in rendered.items():
                with self.subTest(query_id=fixture["query_id"], profile=profile):
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
