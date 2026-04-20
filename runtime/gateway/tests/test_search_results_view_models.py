from __future__ import annotations

import unittest

from runtime.gateway import build_demo_search_public_api
from runtime.gateway.public_api import SearchCatalogRequest, search_response_envelope_to_search_results_view_model


class SearchResultsViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_search_public_api()

    def test_non_empty_search_response_maps_to_shared_view_model(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("synthetic"))

        view_model = search_response_envelope_to_search_results_view_model(response.body)

        self.assertEqual(view_model["query"], "synthetic")
        self.assertEqual(view_model["result_count"], 2)
        self.assertEqual(view_model["results"][0]["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
        self.assertNotIn("absence", view_model)

    def test_empty_search_response_maps_to_absence_view_model(self) -> None:
        response = self.public_api.search_records(SearchCatalogRequest.from_parts("missing"))

        view_model = search_response_envelope_to_search_results_view_model(response.body)

        self.assertEqual(
            view_model,
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
