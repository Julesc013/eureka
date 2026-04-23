from __future__ import annotations

import unittest

from runtime.gateway import build_demo_acquisition_public_api
from runtime.gateway.public_api import AcquisitionFetchRequest


class AcquisitionPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_acquisition_public_api()

    def test_public_acquisition_boundary_returns_bytes_for_fetchable_representation(self) -> None:
        response = self.public_api.fetch_representation(
            AcquisitionFetchRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.source",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/vnd.eureka.synthetic.bundle")
        self.assertEqual(response.filename, "synthetic-demo-app.bundle")
        self.assertIsNotNone(response.payload)
        self.assertIn(b"EUREKA-SYNTHETIC-BUNDLE", response.payload or b"")
        self.assertEqual(response.body["acquisition_status"], "fetched")

    def test_public_acquisition_boundary_returns_unavailable_shape_for_non_fetchable_representation(self) -> None:
        response = self.public_api.fetch_representation(
            AcquisitionFetchRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.release-metadata",
            )
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.body["acquisition_status"], "unavailable")
        self.assertEqual(response.body["reason_codes"][0], "representation_not_fetchable")
        self.assertIsNone(response.payload)

    def test_public_acquisition_boundary_returns_blocked_shape_for_unknown_representation(self) -> None:
        response = self.public_api.fetch_representation(
            AcquisitionFetchRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.unknown",
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["acquisition_status"], "blocked")
        self.assertEqual(response.body["reason_codes"][0], "representation_not_found")


if __name__ == "__main__":
    unittest.main()
