from __future__ import annotations

import unittest

from runtime.gateway import build_demo_decomposition_public_api
from runtime.gateway.public_api import DecompositionInspectionRequest


class DecompositionPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_decomposition_public_api()

    def test_public_decomposition_boundary_returns_member_listing_for_supported_representation(self) -> None:
        response = self.public_api.decompose_representation(
            DecompositionInspectionRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["decomposition_status"], "decomposed")
        self.assertEqual(response.body["representation_kind"], "fixture_archive")
        self.assertEqual(response.body["members"][0]["member_path"], "config/settings.json")
        self.assertEqual(response.body["members"][2]["member_path"], "README.txt")

    def test_public_decomposition_boundary_returns_unsupported_shape_for_binary_representation(self) -> None:
        response = self.public_api.decompose_representation(
            DecompositionInspectionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.v2.65.0.asset.0",
            )
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.body["decomposition_status"], "unsupported")
        self.assertEqual(response.body["reason_codes"][0], "representation_format_unsupported")

    def test_public_decomposition_boundary_returns_blocked_shape_for_unknown_representation(self) -> None:
        response = self.public_api.decompose_representation(
            DecompositionInspectionRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.unknown",
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["decomposition_status"], "blocked")
        self.assertEqual(response.body["reason_codes"][0], "representation_not_found")


if __name__ == "__main__":
    unittest.main()
