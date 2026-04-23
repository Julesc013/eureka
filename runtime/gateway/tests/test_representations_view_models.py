from __future__ import annotations

import unittest

from runtime.gateway import build_demo_representations_public_api
from runtime.gateway.public_api import (
    RepresentationCatalogRequest,
    representations_envelope_to_view_model,
)


class RepresentationsViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_representations_public_api()

    def test_representations_envelope_maps_to_shared_view_model(self) -> None:
        response = self.public_api.list_representations(
            RepresentationCatalogRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        view_model = representations_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "available")
        self.assertEqual(view_model["resolved_resource_id"], "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2")
        self.assertEqual(view_model["representations"][0]["representation_kind"], "fixture_artifact")
        self.assertEqual(view_model["representations"][0]["access_kind"], "inspect")
        self.assertTrue(view_model["representations"][0]["is_fetchable"])
        self.assertEqual(view_model["representations"][0]["filename"], "synthetic-demo-app.bundle")
        self.assertEqual(view_model["representations"][1]["label"], "Synthetic demo app fixture record")
        self.assertFalse(view_model["representations"][1]["is_fetchable"])
