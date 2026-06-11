from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from evals.hard_queries import BASELINE_PROFILES, fixture_case_by_query_id, render_fixture_case
from scripts.run_local_e2e_search_demo import (
    FORBIDDEN_PUBLIC_ACTIONS,
    build_demo_suite,
    build_profile_output,
    render_profile_html,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class SurfaceLocalE2EDemoTests(unittest.TestCase):
    def test_all_baseline_renderers_render_demo_outputs(self) -> None:
        suite = build_demo_suite(REPO_ROOT)

        for query_id, profile_results in suite["results"].items():
            for profile in BASELINE_PROFILES:
                with self.subTest(query_id=query_id, profile=profile):
                    result = profile_results[profile]
                    output = result["renderer_output"]

                    self.assertEqual(output["representation_profile"], profile)
                    self.assertIn(result["expected_status"], repr(output))
                    self.assertIn(result["expected_status"], repr(result["view_model"]))

    def test_public_outputs_strip_operator_only_actions(self) -> None:
        suite = build_demo_suite(REPO_ROOT)
        combined = repr(suite["results"])

        for action in FORBIDDEN_PUBLIC_ACTIONS:
            self.assertNotIn(action, combined, action)

    def test_html_demo_escapes_unsafe_fixture_text(self) -> None:
        suite = build_demo_suite(REPO_ROOT)
        html = render_profile_html(build_profile_output(suite, "html_basic_v0", "old blue FTP client for XP"))

        self.assertIn("&amp;lt;client&amp;gt;", html)
        self.assertIn("&amp;quot;blue&amp;quot;", html)
        self.assertNotIn("<client>", html)
        self.assertNotIn('"blue"', html)

    def test_snapshot_digest_is_stable(self) -> None:
        first = build_profile_output(build_demo_suite(REPO_ROOT), "snapshot_v0")
        second = build_profile_output(build_demo_suite(REPO_ROOT), "snapshot_v0")

        self.assertEqual(first, second)
        for item in first["queries"]:
            snapshot = item["renderer_output"]["content"]
            self.assertRegex(snapshot["content_digest"], r"^[0-9a-f]{24}$")

    def test_unknown_status_degrades_safely_through_surface_path(self) -> None:
        fixture = fixture_case_by_query_id("hq_ray_tracing_1994_magazine")
        unknown = deepcopy(fixture)
        unknown["expected_status"] = "unknown"
        unknown["fallback_summary"]["status"] = "not_a_known_status"

        rendered = render_fixture_case(unknown)

        for profile in BASELINE_PROFILES:
            with self.subTest(profile=profile):
                self.assertEqual(rendered[profile]["view_model"]["canonical_status"], "unknown")
                self.assertIn("unknown", repr(rendered[profile]["renderer_result"]["renderer_output"]))

    def test_artifact_gate_visible_for_each_profile_output(self) -> None:
        suite = build_demo_suite(REPO_ROOT)

        for profile in BASELINE_PROFILES:
            output = build_profile_output(suite, profile)
            self.assertEqual(output["artifact_gate"]["status"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
            self.assertEqual(output["artifact_gate"]["reviewed_artifact_record_count"], 4)
            self.assertEqual(output["artifact_gate"]["verified_artifact_count"], 0)


if __name__ == "__main__":
    unittest.main()
