from __future__ import annotations

import unittest

from runtime.gateway import build_demo_representations_public_api
from runtime.gateway.public_api import RepresentationCatalogRequest


class RepresentationsPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_representations_public_api()

    def test_public_representations_boundary_returns_bounded_representation_listing(self) -> None:
        response = self.public_api.list_representations(
            RepresentationCatalogRequest.from_parts("github-release:cli/cli@v2.65.0")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "available")
        self.assertEqual(response.body["target_ref"], "github-release:cli/cli@v2.65.0")
        self.assertEqual(response.body["primary_object"]["label"], "GitHub CLI 2.65.0")
        self.assertEqual(len(response.body["representations"]), 3)
        self.assertEqual(response.body["representations"][0]["representation_kind"], "release_page")
        self.assertEqual(response.body["representations"][1]["access_kind"], "download")

    def test_public_representations_boundary_returns_blocked_shape_for_missing_target(self) -> None:
        response = self.public_api.list_representations(
            RepresentationCatalogRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["target_ref"], "fixture:software/missing-demo-app@0.0.1")
        self.assertEqual(response.body["notices"][0]["code"], "target_ref_not_found")
