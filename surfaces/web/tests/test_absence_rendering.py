from __future__ import annotations

import unittest

from runtime.gateway.public_api import build_demo_absence_public_api
from surfaces.web.server import render_resolve_absence_page, render_search_absence_page


class AbsenceRenderingTestCase(unittest.TestCase):
    def test_resolve_absence_page_renders_requested_value_likely_reason_and_near_matches(self) -> None:
        html = render_resolve_absence_page(
            build_demo_absence_public_api(),
            "fixture:software/archivebox@9.9.9",
        )

        self.assertIn("fixture:software/archivebox@9.9.9", html)
        self.assertIn("known_subject_different_state", html)
        self.assertIn("archivebox", html)
        self.assertIn("fixture:software/archivebox@0.8.5", html)
        self.assertIn("github-release:archivebox/archivebox@v0.8.5", html)
        self.assertIn("synthetic_fixture, github_releases", html)

    def test_search_absence_page_renders_reason_and_next_steps(self) -> None:
        html = render_search_absence_page(
            build_demo_absence_public_api(),
            "archive box",
        )

        self.assertIn("archive box", html)
        self.assertIn("related_subjects_exist", html)
        self.assertIn("Retry search with one of the near-match target_ref values or object labels.", html)
        self.assertIn("List known states for subject &#x27;archivebox&#x27;.", html)
