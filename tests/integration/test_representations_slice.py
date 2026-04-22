from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    RepresentationCatalogRequest,
    build_demo_representations_public_api,
    representations_envelope_to_view_model,
)
from surfaces.native.cli.formatters import format_representations


class RepresentationsSliceIntegrationTestCase(unittest.TestCase):
    def test_representation_slice_preserves_known_access_paths_into_surface_projection(self) -> None:
        public_api = build_demo_representations_public_api()
        response = public_api.list_representations(
            RepresentationCatalogRequest.from_parts("github-release:cli/cli@v2.65.0")
        )

        self.assertEqual(response.status_code, 200)
        view_model = representations_envelope_to_view_model(response.body)
        rendered = format_representations(view_model)

        self.assertEqual(view_model["status"], "available")
        self.assertEqual(view_model["target_ref"], "github-release:cli/cli@v2.65.0")
        self.assertEqual(len(view_model["representations"]), 3)
        self.assertEqual(view_model["representations"][0]["representation_kind"], "release_page")
        self.assertEqual(view_model["representations"][1]["access_kind"], "download")
        self.assertIn("GitHub CLI 2.65.0 release page", rendered)
        self.assertIn("gh_2.65.0_windows_amd64.msi", rendered)
        self.assertIn("access_kind: download", rendered)
