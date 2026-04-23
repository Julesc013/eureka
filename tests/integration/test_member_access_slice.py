from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    MemberAccessReadRequest,
    build_demo_member_access_public_api,
    member_access_envelope_to_view_model,
)
from surfaces.native.cli.formatters import format_member_access


class MemberAccessSliceIntegrationTestCase(unittest.TestCase):
    def test_member_access_slice_preserves_bounded_preview_into_surface_projection(self) -> None:
        public_api = build_demo_member_access_public_api()
        response = public_api.read_member(
            MemberAccessReadRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
                "docs/evidence.txt",
            )
        )

        self.assertEqual(response.status_code, 200)
        view_model = member_access_envelope_to_view_model(response.body)
        rendered = format_member_access(view_model)

        self.assertEqual(view_model["status"], "previewed")
        self.assertEqual(view_model["member_path"], "docs/evidence.txt")
        self.assertEqual(view_model["content_type"], "text/plain")
        self.assertIn("recorded fixture evidence summary", view_model["text_preview"])
        self.assertIn("Member access", rendered)
        self.assertIn("status: previewed", rendered)
        self.assertIn("docs/evidence.txt", rendered)
