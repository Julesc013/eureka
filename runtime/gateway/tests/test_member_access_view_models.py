from __future__ import annotations

import unittest

from runtime.gateway import build_demo_member_access_public_api
from runtime.gateway.public_api import (
    MemberAccessReadRequest,
    member_access_envelope_to_view_model,
)


class MemberAccessViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_member_access_public_api()

    def test_member_access_envelope_maps_to_shared_view_model(self) -> None:
        response = self.public_api.read_member(
            MemberAccessReadRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
                "docs/evidence.txt",
            )
        )

        view_model = member_access_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "previewed")
        self.assertEqual(view_model["representation_id"], "rep.synthetic-demo-app.package")
        self.assertEqual(view_model["member_path"], "docs/evidence.txt")
        self.assertEqual(view_model["content_type"], "text/plain")
        self.assertIn("recorded fixture evidence summary", view_model["text_preview"])
