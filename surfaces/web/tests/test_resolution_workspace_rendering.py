from __future__ import annotations

import unittest

from surfaces.web.workbench import render_resolution_workspace_html


class ResolutionWorkspaceRenderingTestCase(unittest.TestCase):
    def test_known_target_rendering_includes_completed_status_selected_object_and_action_link(self) -> None:
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
            },
            resolution_actions={
                "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                "actions": [
                    {
                        "action_id": "export_resolution_manifest",
                        "label": "Export resolution manifest",
                        "availability": "available",
                        "href": "/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                    }
                ],
            },
        )

        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", html)
        self.assertIn("completed", html)
        self.assertIn("obj.synthetic-demo-app", html)
        self.assertIn("Synthetic Demo App", html)
        self.assertIn("Export resolution manifest", html)
        self.assertIn("/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)

    def test_unknown_target_rendering_includes_blocked_status_notice_and_unavailable_action_state(self) -> None:
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
            },
            resolution_actions={
                "target_ref": "fixture:software/missing-demo-app@0.0.1",
                "actions": [
                    {
                        "action_id": "export_resolution_manifest",
                        "label": "Export resolution manifest",
                        "availability": "unavailable",
                    }
                ],
                "notices": [
                    {
                        "code": "resolution_manifest_not_available",
                        "severity": "warning",
                        "message": "No resolved synthetic record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
                    }
                ],
            },
        )

        self.assertIn("fixture:software/missing-demo-app@0.0.1", html)
        self.assertIn("blocked", html)
        self.assertIn("fixture_target_not_found", html)
        self.assertIn("No governed synthetic record matched target_ref", html)
        self.assertIn("No available actions are exposed for this target.", html)
        self.assertIn("Export resolution manifest (unavailable)", html)
        self.assertIn("resolution_manifest_not_available", html)
