from __future__ import annotations

import unittest

from runtime.gateway.public_api import build_demo_decomposition_public_api
from surfaces.web.server import render_decomposition_page


class DecompositionRenderingTestCase(unittest.TestCase):
    def test_decomposition_page_renders_member_listing_for_supported_representation(self) -> None:
        html = render_decomposition_page(
            build_demo_decomposition_public_api(),
            "fixture:software/synthetic-demo-app@1.0.0",
            "rep.synthetic-demo-app.package",
        )

        self.assertIn("Eureka Bounded Decomposition", html)
        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", html)
        self.assertIn("rep.synthetic-demo-app.package", html)
        self.assertIn("decomposed", html)
        self.assertIn("config/settings.json", html)
        self.assertIn("docs/evidence.txt", html)
        self.assertIn("README.txt", html)
        self.assertIn("application/json", html)
        self.assertIn("application/zip", html)

    def test_decomposition_page_renders_unsupported_reason_for_binary_representation(self) -> None:
        html = render_decomposition_page(
            build_demo_decomposition_public_api(),
            "github-release:cli/cli@v2.65.0",
            "rep.github-release.cli.cli.v2.65.0.asset.0",
        )

        self.assertIn("unsupported", html)
        self.assertIn("representation_format_unsupported", html)
        self.assertIn("gh_2.65.0_windows_amd64.msi", html)


if __name__ == "__main__":
    unittest.main()
