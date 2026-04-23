from __future__ import annotations

import unittest

from runtime.gateway.public_api import build_demo_member_access_public_api
from surfaces.web.server import render_member_access_page


class MemberAccessRenderingTestCase(unittest.TestCase):
    def test_member_access_page_renders_preview_for_known_member(self) -> None:
        html = render_member_access_page(
            build_demo_member_access_public_api(),
            "fixture:software/synthetic-demo-app@1.0.0",
            "rep.synthetic-demo-app.package",
            "README.txt",
        )

        self.assertIn("Eureka Member Access", html)
        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", html)
        self.assertIn("rep.synthetic-demo-app.package", html)
        self.assertIn("README.txt", html)
        self.assertIn("previewed", html)
        self.assertIn("Text preview", html)
        self.assertIn("Synthetic Demo App package", html)

    def test_member_access_page_renders_unsupported_reason_for_binary_representation(self) -> None:
        html = render_member_access_page(
            build_demo_member_access_public_api(),
            "github-release:cli/cli@v2.65.0",
            "rep.github-release.cli.cli.v2.65.0.asset.0",
            "README.txt",
        )

        self.assertIn("unsupported", html)
        self.assertIn("representation_format_unsupported", html)
