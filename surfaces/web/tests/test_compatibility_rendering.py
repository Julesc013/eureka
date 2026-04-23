from __future__ import annotations

import unittest

from runtime.gateway.public_api import build_demo_compatibility_public_api
from surfaces.web.server import render_compatibility_page


class CompatibilityRenderingTestCase(unittest.TestCase):
    def test_compatibility_page_renders_host_status_and_reasons(self) -> None:
        html = render_compatibility_page(
            build_demo_compatibility_public_api(),
            "fixture:software/archive-viewer@0.9.0",
            "linux-x86_64",
        )

        self.assertIn("Eureka Compatibility Check", html)
        self.assertIn("fixture:software/archive-viewer@0.9.0", html)
        self.assertIn("linux-x86_64", html)
        self.assertIn("Compatibility status", html)
        self.assertIn("incompatible", html)
        self.assertIn("os_family_not_supported", html)
        self.assertIn("Synthetic Fixture", html)
