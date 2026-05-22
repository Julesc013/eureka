from __future__ import annotations

import unittest

from surfaces.web.workbench.local_html import (
    build_search_hunt_detail_page_view,
    render_search_hunt_detail_page,
    validate_local_workbench_page,
)
from runtime.search_hunt import SearchHuntSession, SearchHuntTransition


class SearchHuntCommandUiTests(unittest.TestCase):
    def test_hunt_detail_ui_shows_operator_controls_when_enabled(self) -> None:
        hunt = SearchHuntSession.new("sampleproject")
        transition = SearchHuntTransition.new(hunt.id, None, hunt.state, "created")
        view = build_search_hunt_detail_page_view(
            hunt,
            [transition],
            {
                "command_controls_enabled": True,
                "steering_controls_enabled": True,
                "operator_token_required_for_mutations": True,
                "localhost_only_mutations": True,
                "lan_command_mutations_enabled": False,
                "commands": [
                    {
                        "command_id": "cmd_1",
                        "command_type": "pause",
                        "previous_state": "running",
                        "resulting_state": "paused",
                        "operator_label": "tester",
                        "reason": "test",
                        "policy_decision": "allowed",
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ],
                "steering_preferences": [
                    {
                        "steering_id": "steer_1",
                        "hunt_id": hunt.id,
                        "command_id": "cmd_2",
                        "command_type": "metadata_only",
                        "value": "",
                        "reason": "test",
                        "operator_label": "tester",
                        "active": True,
                        "created_at": "2026-01-01T00:00:00Z",
                        "updated_at": "2026-01-01T00:00:00Z",
                    }
                ],
            },
        )
        html = render_search_hunt_detail_page(view)
        validate_local_workbench_page(html, allow_operator_mutation_forms=True)
        lowered = html.lower()
        self.assertIn("operator state controls", lowered)
        self.assertIn("steering preferences", lowered)
        self.assertIn("command history", lowered)
        self.assertIn("operator token", lowered)
        self.assertIn("lan_command_mutations_enabled", lowered)
        self.assertIn("method=\"post\"", lowered)
        self.assertNotIn("create workunit", lowered)
        self.assertNotIn("source probe control", lowered)
        self.assertNotIn("ai escalation control", lowered)


if __name__ == "__main__":
    unittest.main()
