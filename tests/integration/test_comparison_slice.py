from __future__ import annotations

import unittest

from runtime.gateway import build_demo_comparison_public_api
from runtime.gateway.public_api import CompareTargetsRequest, comparison_envelope_to_view_model
from surfaces.web.server import render_comparison_page


class ComparisonSliceIntegrationTestCase(unittest.TestCase):
    def test_comparison_boundary_and_surface_projection_preserve_side_by_side_claims(self) -> None:
        left_target_ref = "fixture:software/archivebox@0.8.5"
        right_target_ref = "github-release:archivebox/archivebox@v0.8.5"
        comparison_public_api = build_demo_comparison_public_api()

        response = comparison_public_api.compare_targets(
            CompareTargetsRequest.from_parts(left_target_ref, right_target_ref)
        )
        comparison = comparison_envelope_to_view_model(response.body)
        rendered = render_comparison_page(
            comparison_public_api,
            left_target_ref,
            right_target_ref,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(comparison["status"], "compared")
        self.assertEqual(comparison["left"]["evidence"][0]["claim_kind"], "label")
        self.assertEqual(comparison["right"]["evidence"][1]["claim_kind"], "version")
        self.assertEqual(comparison["agreements"][0]["category"], "subject_key")
        self.assertEqual(comparison["disagreements"][0]["category"], "object_label")
        self.assertIn("ArchiveBox 0.8.5", rendered)
        self.assertIn("ArchiveBox v0.8.5", rendered)
        self.assertIn("subject_key", rendered)
        self.assertIn("object_label", rendered)


if __name__ == "__main__":
    unittest.main()
