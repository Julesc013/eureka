from __future__ import annotations

import unittest

from runtime.gateway.public_api import build_demo_action_plan_public_api
from surfaces.web.server import render_action_plan_page


class ActionPlanRenderingTestCase(unittest.TestCase):
    def test_action_plan_page_renders_selected_strategy_host_status_and_grouped_actions(self) -> None:
        html = render_action_plan_page(
            build_demo_action_plan_public_api(),
            "github-release:cli/cli@v2.65.0",
            "windows-x86_64",
            "acquire",
        )

        self.assertIn("Eureka Action Plan", html)
        self.assertIn("github-release:cli/cli@v2.65.0", html)
        self.assertIn("windows-x86_64", html)
        self.assertIn("Strategy", html)
        self.assertIn("acquire", html)
        self.assertIn("Compatibility status", html)
        self.assertIn("compatible", html)
        self.assertIn("Recommended", html)
        self.assertIn("Access gh_2.65.0_windows_amd64.msi", html)
        self.assertIn("Available", html)
        self.assertIn("Unavailable", html)
