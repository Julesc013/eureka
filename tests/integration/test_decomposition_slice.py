from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    DecompositionInspectionRequest,
    build_demo_decomposition_public_api,
    decomposition_envelope_to_view_model,
)
from surfaces.native.cli.formatters import format_decomposition


class DecompositionSliceIntegrationTestCase(unittest.TestCase):
    def test_decomposition_slice_preserves_bounded_member_listing_into_surface_projection(self) -> None:
        public_api = build_demo_decomposition_public_api()
        response = public_api.decompose_representation(
            DecompositionInspectionRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
            )
        )

        self.assertEqual(response.status_code, 200)
        view_model = decomposition_envelope_to_view_model(response.body)
        rendered = format_decomposition(view_model)

        self.assertEqual(view_model["status"], "decomposed")
        self.assertEqual(view_model["representation_kind"], "fixture_archive")
        self.assertEqual(view_model["members"][0]["member_path"], "config/settings.json")
        self.assertEqual(view_model["members"][2]["member_path"], "README.txt")
        self.assertIn("Decomposition", rendered)
        self.assertIn("status: decomposed", rendered)
        self.assertIn("config/settings.json", rendered)


if __name__ == "__main__":
    unittest.main()
