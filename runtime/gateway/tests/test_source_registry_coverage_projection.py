from __future__ import annotations

import json
import unittest

from runtime.gateway import build_demo_source_registry_public_api
from runtime.gateway.public_api import SourceCatalogRequest, SourceReadRequest


class SourceRegistryCoverageProjectionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_source_registry_public_api()

    def test_list_projection_includes_capabilities_and_coverage(self) -> None:
        response = self.public_api.list_sources(SourceCatalogRequest.from_parts())

        self.assertEqual(response.status_code, 200)
        first_source = response.body["sources"][0]
        self.assertIn("capabilities", first_source)
        self.assertIn("capabilities_summary", first_source)
        self.assertIn("coverage", first_source)
        self.assertIn("coverage_depth", first_source)
        self.assertIn("connector_mode", first_source)

    def test_detail_projection_keeps_placeholder_honest(self) -> None:
        response = self.public_api.get_source(
            SourceReadRequest.from_parts("internet-archive-placeholder")
        )

        self.assertEqual(response.status_code, 200)
        source = response.body["sources"][0]
        self.assertEqual(source["status"], "placeholder")
        self.assertEqual(source["coverage_depth"], "source_known")
        self.assertEqual(source["connector_mode"], "not_implemented")
        self.assertFalse(source["capabilities"]["live_supported"])
        self.assertIn("Placeholder only", source["placeholder_warning"])

    def test_list_projection_filters_by_capability_and_coverage(self) -> None:
        recorded_response = self.public_api.list_sources(
            SourceCatalogRequest.from_parts(capability="recorded_fixture_backed")
        )
        self.assertEqual(
            [entry["source_id"] for entry in recorded_response.body["sources"]],
            [
                "github-releases-recorded-fixtures",
                "internet-archive-recorded-fixtures",
            ],
        )

        source_known_response = self.public_api.list_sources(
            SourceCatalogRequest.from_parts(coverage_depth="source_known")
        )
        self.assertEqual(source_known_response.body["source_count"], 4)

    def test_detail_projection_includes_new_recorded_fixture_sources(self) -> None:
        ia_response = self.public_api.get_source(
            SourceReadRequest.from_parts("internet-archive-recorded-fixtures")
        )
        local_response = self.public_api.get_source(
            SourceReadRequest.from_parts("local-bundle-fixtures")
        )

        self.assertEqual(ia_response.status_code, 200)
        self.assertEqual(ia_response.body["sources"][0]["status"], "active_recorded_fixture")
        self.assertEqual(ia_response.body["sources"][0]["coverage_depth"], "representation_indexed")
        self.assertFalse(ia_response.body["sources"][0]["capabilities"]["live_supported"])
        self.assertEqual(local_response.status_code, 200)
        self.assertEqual(local_response.body["sources"][0]["status"], "active_fixture")
        self.assertEqual(local_response.body["sources"][0]["coverage_depth"], "action_indexed")
        self.assertTrue(local_response.body["sources"][0]["capabilities"]["supports_member_listing"])

    def test_public_projection_does_not_expose_private_paths(self) -> None:
        response = self.public_api.get_source(SourceReadRequest.from_parts("local-files-placeholder"))
        serialized = json.dumps(response.body, sort_keys=True)

        self.assertNotIn("C:\\", serialized)
        self.assertNotIn("D:\\", serialized)
        self.assertNotIn("/Users/", serialized)
        self.assertTrue(response.body["sources"][0]["capabilities"]["local_private"])


if __name__ == "__main__":
    unittest.main()
