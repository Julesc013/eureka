from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_05


class SnapshotRefreshPublicSearchUxSectionTests(unittest.TestCase):
    def test_public_search_ux_section_is_no_js_read_only_projection(self) -> None:
        result = run_snapshot_refresh_05(from_public_search_ux_examples=True)
        section = result["public_search_ux_section"]
        route_section = result["public_route_section"]

        self.assertEqual("snapshot_public_search_ux_section.v0", section["schema_version"])
        self.assertEqual(8, section["route_count"])
        self.assertEqual(87, section["result_card_count"])
        self.assertTrue(section["no_js_required"])
        self.assertTrue(section["public_read_only"])
        self.assertFalse(section["mutation_enabled"])
        self.assertFalse(section["live_source_fanout_enabled"])
        self.assertFalse(section["download_enabled"])
        self.assertFalse(section["file_fetch_enabled"])
        self.assertFalse(section["ocr_enabled"])
        self.assertFalse(section["extraction_enabled"])
        self.assertFalse(section["model_provider_enabled"])

        self.assertEqual(8, route_section["route_count"])
        self.assertTrue(route_section["all_routes_get"])
        self.assertTrue(route_section["all_routes_no_js"])
        self.assertTrue(route_section["all_routes_read_only"])


if __name__ == "__main__":
    unittest.main()
