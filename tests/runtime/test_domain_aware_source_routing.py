from __future__ import annotations

import unittest

from runtime.search.query_plan import plan_query_to_source_actions


class DomainAwareSourceRoutingTests(unittest.TestCase):
    def test_frontier_media_routes_to_archive_wayback_wikidata(self) -> None:
        plan = plan_query_to_source_actions("New York 1993 D-Theater HD demo tape original source")

        self.assertEqual("frontier_resolution_media", plan["domain_pack"])
        self.assertGreaterEqual(
            set(plan["source_families"]),
            {"internet_archive_metadata", "wayback_cdx_metadata", "wikidata_metadata"},
        )

    def test_legacy_software_routes_to_software_sources(self) -> None:
        plan = plan_query_to_source_actions("Windows 7-compatible portable utilities, not Windows 7 ISO")

        self.assertEqual("legacy_software", plan["domain_pack"])
        self.assertGreaterEqual(
            set(plan["source_families"]),
            {"internet_archive_metadata", "github_releases_metadata", "package_registry_metadata"},
        )

    def test_driver_query_routes_to_support_media_sources(self) -> None:
        plan = plan_query_to_source_actions("StyleWriter 2500 Mac OS 8 driver")

        self.assertEqual("driver_support_media", plan["domain_pack"])
        self.assertGreaterEqual(
            set(plan["source_families"]),
            {"internet_archive_metadata", "wayback_cdx_metadata", "manual_source_pack"},
        )


if __name__ == "__main__":
    unittest.main()
