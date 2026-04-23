from __future__ import annotations

import unittest

from runtime.gateway import build_demo_member_access_public_api
from runtime.gateway.public_api import MemberAccessReadRequest


class MemberAccessPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_member_access_public_api()

    def test_public_member_access_boundary_returns_preview_for_known_member(self) -> None:
        response = self.public_api.read_member(
            MemberAccessReadRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
                "README.txt",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["member_access_status"], "previewed")
        self.assertEqual(response.body["member_path"], "README.txt")
        self.assertEqual(response.body["content_type"], "text/plain")
        self.assertIn("Synthetic Demo App package", response.body["text_preview"])
        self.assertIsNotNone(response.payload)

    def test_public_member_access_boundary_returns_structured_not_found_for_unknown_member(self) -> None:
        response = self.public_api.read_member(
            MemberAccessReadRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
                "missing/member.txt",
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["member_access_status"], "blocked")
        self.assertEqual(response.body["reason_codes"][0], "member_not_found")

    def test_public_member_access_boundary_returns_structured_unsupported_for_binary_representation(self) -> None:
        response = self.public_api.read_member(
            MemberAccessReadRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.v2.65.0.asset.0",
                "README.txt",
            )
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.body["member_access_status"], "unsupported")
        self.assertEqual(response.body["reason_codes"][0], "representation_format_unsupported")
