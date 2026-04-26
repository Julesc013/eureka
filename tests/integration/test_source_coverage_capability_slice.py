from __future__ import annotations

import json
import unittest

from runtime.gateway import build_demo_source_registry_public_api
from runtime.gateway.public_api import SourceCatalogRequest, SourceReadRequest
from runtime.source_registry import load_source_registry
from surfaces.web.workbench import render_source_registry_html


class SourceCoverageCapabilitySliceTest(unittest.TestCase):
    def test_registry_gateway_and_web_projection_preserve_coverage(self) -> None:
        registry = load_source_registry()
        synthetic = registry.get_record("synthetic-fixtures")
        self.assertEqual(synthetic.coverage.coverage_depth, "action_indexed")
        self.assertTrue(synthetic.capabilities.supports_action_paths)

        public_api = build_demo_source_registry_public_api()
        response = public_api.get_source(SourceReadRequest.from_parts("synthetic-fixtures"))
        source = response.body["sources"][0]
        self.assertEqual(source["coverage_depth"], "action_indexed")
        self.assertTrue(source["capabilities"]["supports_action_paths"])

        html = render_source_registry_html(response.body)
        self.assertIn("action_indexed", html)
        self.assertIn("supports_action_paths", html)

    def test_placeholder_source_stays_honest_across_public_projection(self) -> None:
        public_api = build_demo_source_registry_public_api()
        response = public_api.get_source(SourceReadRequest.from_parts("internet-archive-placeholder"))
        source = response.body["sources"][0]
        serialized = json.dumps(response.body, sort_keys=True)

        self.assertEqual(source["status"], "placeholder")
        self.assertEqual(source["coverage_depth"], "source_known")
        self.assertEqual(source["connector"]["status"], "unimplemented")
        self.assertFalse(source["capabilities"]["live_supported"])
        self.assertIn("Placeholder only", source["placeholder_warning"])
        self.assertNotIn("C:\\", serialized)
        self.assertNotIn("D:\\", serialized)

    def test_public_filters_can_select_recorded_fixture_capability(self) -> None:
        response = build_demo_source_registry_public_api().list_sources(
            SourceCatalogRequest.from_parts(capability="recorded_fixture_backed")
        )

        self.assertEqual(response.body["source_count"], 2)
        self.assertEqual(
            {source["source_id"] for source in response.body["sources"]},
            {"github-releases-recorded-fixtures", "internet-archive-recorded-fixtures"},
        )


if __name__ == "__main__":
    unittest.main()
