from __future__ import annotations

import unittest

from surfaces.web.workbench import render_resolution_workspace_html


class ResolutionWorkspaceRenderingTestCase(unittest.TestCase):
    def test_known_target_rendering_includes_completed_status_and_selected_object(self) -> None:
        html = render_resolution_workspace_html(
            {
                "session_id": "session.known",
                "active_job": {
                    "job_id": "job-0001",
                    "status": "completed",
                    "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                },
                "selected_object": {
                    "id": "obj.synthetic-demo-app",
                    "kind": "software",
                    "label": "Synthetic Demo App",
                },
            }
        )

        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", html)
        self.assertIn("completed", html)
        self.assertIn("obj.synthetic-demo-app", html)
        self.assertIn("Synthetic Demo App", html)

    def test_unknown_target_rendering_includes_blocked_status_and_notice(self) -> None:
        html = render_resolution_workspace_html(
            {
                "session_id": "session.blocked",
                "active_job": {
                    "job_id": "job-0002",
                    "status": "blocked",
                    "target_ref": "fixture:software/missing-demo-app@0.0.1",
                },
                "notices": [
                    {
                        "code": "fixture_target_not_found",
                        "severity": "warning",
                        "message": "No governed synthetic record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
                    }
                ],
            }
        )

        self.assertIn("fixture:software/missing-demo-app@0.0.1", html)
        self.assertIn("blocked", html)
        self.assertIn("fixture_target_not_found", html)
        self.assertIn("No governed synthetic record matched target_ref", html)
