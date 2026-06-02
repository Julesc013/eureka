from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_05


class SnapshotRefreshNoResultsProjectionTests(unittest.TestCase):
    def test_no_results_and_text_projection_are_read_only(self) -> None:
        result = run_snapshot_refresh_05(from_public_search_ux_examples=True)
        no_results = result["no_results_section"]
        text_projection = result["text_projection_section"]
        reassess = result["public_alpha_reassess_input"]

        self.assertEqual("snapshot_no_results_section.v0", no_results["schema_version"])
        self.assertEqual(1, no_results["no_results_sections_count"])
        self.assertTrue(no_results["known_need_projection_visible"])
        self.assertFalse(no_results["public_mutation_enabled"])
        self.assertFalse(no_results["live_source_fanout_enabled"])

        self.assertEqual("snapshot_text_projection_section.v0", text_projection["schema_version"])
        self.assertTrue(text_projection["text_projection_available"])
        self.assertTrue(text_projection["classic_html_examples_available"])
        self.assertTrue(text_projection["public_read_only"])

        self.assertTrue(reassess["public_search_ux_integrated"])
        self.assertTrue(reassess["no_js_required"])
        self.assertTrue(reassess["public_projection_read_only"])
        self.assertFalse(reassess["public_launch_readiness_claimed"])


if __name__ == "__main__":
    unittest.main()
