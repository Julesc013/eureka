from __future__ import annotations

import unittest

from runtime.gateway import build_demo_search_public_api
from runtime.gateway.public_api import SearchCatalogRequest


class SearchPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_search_public_api()

    def test_public_search_boundary_returns_multiple_matches(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("synthetic"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["query"], "synthetic")
        self.assertEqual(response.body["result_count"], 2)
        self.assertEqual(
            [entry["target_ref"] for entry in response.body["results"]],
            [
                "fixture:software/synthetic-demo-app@1.0.0",
                "fixture:software/synthetic-demo-suite@2.0.0",
            ],
        )

    def test_public_search_boundary_returns_one_match(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("compatibility"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["result_count"], 1)
        self.assertEqual(response.body["results"][0]["target_ref"], "fixture:software/compatibility-lab@3.2.1")
        self.assertEqual(
            response.body["results"][0]["object"],
            {
                "id": "obj.compatibility-lab",
                "kind": "software",
                "label": "Compatibility Lab",
            },
        )
        self.assertTrue(response.body["results"][0]["resolved_resource_id"].startswith("resolved:sha256:"))

    def test_public_search_boundary_returns_structured_absence_for_no_matches(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("missing"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            {
                "query": "missing",
                "result_count": 0,
                "results": [],
                "absence": {
                    "code": "search_no_matches",
                    "message": "No governed synthetic records matched query 'missing'.",
                },
            },
        )
