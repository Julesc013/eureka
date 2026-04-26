from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    ExplainResolveMissRequest,
    absence_envelope_to_view_model,
    build_demo_absence_public_api,
)
from surfaces.web.workbench import render_absence_report_html


class AbsenceSliceIntegrationTestCase(unittest.TestCase):
    def test_absence_slice_preserves_bounded_reasoning_into_surface_projection(self) -> None:
        public_api = build_demo_absence_public_api()
        response = public_api.explain_resolution_miss(
            ExplainResolveMissRequest.from_parts("fixture:software/archivebox@9.9.9"),
        )

        self.assertEqual(response.status_code, 200)
        view_model = absence_envelope_to_view_model(response.body)
        rendered = render_absence_report_html(
            view_model,
            request_kind="resolve",
            requested_value="fixture:software/archivebox@9.9.9",
        )

        self.assertEqual(view_model["likely_reason_code"], "known_subject_different_state")
        self.assertEqual(
            view_model["checked_source_families"],
            [
                "synthetic_fixture",
                "github_releases",
                "internet_archive_recorded",
                "local_bundle_fixtures",
            ],
        )
        self.assertEqual(
            [entry["target_ref"] for entry in view_model["near_matches"]],
            [
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
                "github-release:archivebox/archivebox@v0.8.4",
            ],
        )
        self.assertIn("known_subject_different_state", rendered)
        self.assertIn("fixture:software/archivebox@0.8.5", rendered)
        self.assertIn("github-release:archivebox/archivebox@v0.8.5", rendered)


if __name__ == "__main__":
    unittest.main()
