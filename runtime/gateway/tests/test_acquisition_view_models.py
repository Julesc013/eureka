from __future__ import annotations

import unittest

from runtime.gateway import build_demo_acquisition_public_api
from runtime.gateway.public_api import (
    AcquisitionFetchRequest,
    acquisition_envelope_to_view_model,
)


class AcquisitionViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_acquisition_public_api()

    def test_acquisition_envelope_maps_to_shared_view_model(self) -> None:
        response = self.public_api.fetch_representation(
            AcquisitionFetchRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.v2.65.0.asset.1",
            )
        )

        view_model = acquisition_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "fetched")
        self.assertEqual(view_model["representation_id"], "rep.github-release.cli.cli.v2.65.0.asset.1")
        self.assertEqual(view_model["filename"], "gh_2.65.0_checksums.txt")
        self.assertEqual(view_model["content_type"], "text/plain")
        self.assertEqual(view_model["source_family"], "github_releases")
        self.assertEqual(view_model["access_kind"], "download")


if __name__ == "__main__":
    unittest.main()
