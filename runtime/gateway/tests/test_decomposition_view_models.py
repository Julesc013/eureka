from __future__ import annotations

import unittest

from runtime.gateway import build_demo_decomposition_public_api
from runtime.gateway.public_api import (
    DecompositionInspectionRequest,
    decomposition_envelope_to_view_model,
)


class DecompositionViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_decomposition_public_api()

    def test_decomposition_envelope_maps_to_shared_view_model(self) -> None:
        response = self.public_api.decompose_representation(
            DecompositionInspectionRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
            )
        )

        view_model = decomposition_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "decomposed")
        self.assertEqual(view_model["representation_id"], "rep.synthetic-demo-app.package")
        self.assertEqual(view_model["content_type"], "application/zip")
        self.assertEqual(view_model["source_family"], "synthetic_fixture")
        self.assertEqual(len(view_model["members"]), 3)
        self.assertEqual(view_model["members"][1]["member_path"], "docs/evidence.txt")
        self.assertEqual(view_model["members"][1]["content_type"], "text/plain")


if __name__ == "__main__":
    unittest.main()
