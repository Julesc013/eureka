from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    SubjectStatesCatalogRequest,
    build_demo_subject_states_public_api,
    subject_states_envelope_to_view_model,
)
from surfaces.web.workbench import render_subject_states_html


class SubjectStatesSliceIntegrationTestCase(unittest.TestCase):
    def test_subject_states_slice_preserves_order_and_sources_into_surface_projection(self) -> None:
        public_api = build_demo_subject_states_public_api()
        response = public_api.list_subject_states(SubjectStatesCatalogRequest.from_parts("archivebox"))

        self.assertEqual(response.status_code, 200)
        view_model = subject_states_envelope_to_view_model(response.body)
        rendered = render_subject_states_html(view_model, subject_key="archivebox")

        self.assertEqual(view_model["subject"]["subject_key"], "archivebox")
        self.assertEqual(
            [state["target_ref"] for state in view_model["states"]],
            [
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
                "github-release:archivebox/archivebox@v0.8.4",
            ],
        )
        self.assertEqual(view_model["states"][1]["source"]["family"], "github_releases")
        self.assertEqual(view_model["states"][1]["evidence"][1]["claim_kind"], "version")
        self.assertIn("ArchiveBox", rendered)
        self.assertIn("ArchiveBox v0.8.4", rendered)
        self.assertIn("GitHub Releases", rendered)


if __name__ == "__main__":
    unittest.main()
