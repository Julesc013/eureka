from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    AcquisitionFetchRequest,
    acquisition_envelope_to_view_model,
    build_demo_acquisition_public_api,
)
from surfaces.native.cli.formatters import format_acquisition


class AcquisitionSliceIntegrationTestCase(unittest.TestCase):
    def test_acquisition_slice_preserves_bounded_fetch_result_into_surface_projection(self) -> None:
        public_api = build_demo_acquisition_public_api()
        response = public_api.fetch_representation(
            AcquisitionFetchRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.v2.65.0.asset.0",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.payload)
        view_model = acquisition_envelope_to_view_model(response.body)
        rendered = format_acquisition(view_model)

        self.assertEqual(view_model["status"], "fetched")
        self.assertEqual(view_model["representation_kind"], "release_asset")
        self.assertEqual(view_model["filename"], "gh_2.65.0_windows_amd64.msi")
        self.assertEqual(view_model["source_family"], "github_releases")
        self.assertIn("Acquisition", rendered)
        self.assertIn("status: fetched", rendered)
        self.assertIn("gh_2.65.0_windows_amd64.msi", rendered)


if __name__ == "__main__":
    unittest.main()
