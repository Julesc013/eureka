from __future__ import annotations

import unittest

from runtime.gateway.public_api import build_demo_representation_selection_public_api
from surfaces.web.server import render_handoff_page


class HandoffRenderingTestCase(unittest.TestCase):
    def test_handoff_page_renders_preferred_available_and_unsuitable_entries(self) -> None:
        html = render_handoff_page(
            build_demo_representation_selection_public_api(),
            "github-release:cli/cli@v2.65.0",
            "linux-x86_64",
            "acquire",
        )

        self.assertIn("Eureka Representation Handoff", html)
        self.assertIn("github-release:cli/cli@v2.65.0", html)
        self.assertIn("linux-x86_64", html)
        self.assertIn("acquire", html)
        self.assertIn("Preferred bounded fit", html)
        self.assertIn("Available alternatives", html)
        self.assertIn("Unsuitable choices", html)
        self.assertIn("gh_2.65.0_checksums.txt", html)
        self.assertIn("gh_2.65.0_windows_amd64.msi", html)
        self.assertIn("host_incompatible_for_payload_representation", html)


if __name__ == "__main__":
    unittest.main()
