from __future__ import annotations

import unittest

from runtime.gateway import build_demo_source_registry_public_api
from runtime.gateway.public_api import (
    SourceCatalogRequest,
    SourceReadRequest,
    source_registry_envelope_to_view_model,
)


class SourceRegistryViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_source_registry_public_api()

    def test_list_response_maps_to_shared_view_model(self) -> None:
        response = self.public_api.list_sources(
            SourceCatalogRequest.from_parts(status="active_fixture")
        )

        view_model = source_registry_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "listed")
        self.assertEqual(view_model["source_count"], 1)
        self.assertEqual(view_model["applied_filters"]["status"], "active_fixture")
        self.assertEqual(view_model["sources"][0]["connector"]["status"], "fixture_backed")

    def test_not_found_response_maps_to_blocked_view_model(self) -> None:
        response = self.public_api.get_source(SourceReadRequest.from_parts("missing-source"))

        view_model = source_registry_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "blocked")
        self.assertEqual(view_model["source_count"], 0)
        self.assertEqual(view_model["selected_source_id"], "missing-source")
        self.assertEqual(view_model["notices"][0]["code"], "source_id_not_found")
