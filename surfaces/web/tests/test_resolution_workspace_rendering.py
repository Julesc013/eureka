from __future__ import annotations

import unittest

from surfaces.web.workbench import render_resolution_workspace_html


class ResolutionWorkspaceRenderingTestCase(unittest.TestCase):
    def test_known_target_rendering_includes_completed_status_selected_object_export_links_and_stored_exports(self) -> None:
        html = render_resolution_workspace_html(
            {
                "session_id": "session.known",
                "resolved_resource_id": "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
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
                "source": {
                    "family": "synthetic_fixture",
                    "label": "Synthetic Fixture",
                    "locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
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
                    },
                    {
                        "action_id": "export_resolution_bundle",
                        "label": "Export resolution bundle",
                        "availability": "available",
                        "href": "/actions/export-resolution-bundle?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                    }
                ],
            },
            stored_exports={
                "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                "store_actions": [
                    {
                        "action_id": "store_resolution_manifest",
                        "label": "Store resolution manifest locally",
                        "availability": "available",
                        "href": "/store/manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                    },
                    {
                        "action_id": "store_resolution_bundle",
                        "label": "Store resolution bundle locally",
                        "availability": "available",
                        "href": "/store/bundle?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                    },
                ],
                "artifacts": [
                    {
                        "artifact_id": "sha256:1234",
                        "artifact_kind": "resolution_manifest",
                        "resolved_resource_id": "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
                        "content_type": "application/json; charset=utf-8",
                        "byte_length": 128,
                        "availability": "available",
                        "href": "/stored/artifact?artifact_id=sha256%3A1234",
                        "filename": "eureka-resolution-manifest-demo.json",
                    }
                ],
            },
        )

        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", html)
        self.assertIn("completed", html)
        self.assertIn("obj.synthetic-demo-app", html)
        self.assertIn("Synthetic Demo App", html)
        self.assertIn("resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2", html)
        self.assertIn("Synthetic Fixture", html)
        self.assertIn("contracts/archive/fixtures/software/synthetic_resolution_fixture.json", html)
        self.assertIn("Export resolution manifest", html)
        self.assertIn("/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)
        self.assertIn("Export resolution bundle", html)
        self.assertIn("/actions/export-resolution-bundle?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)
        self.assertIn("Store resolution manifest locally", html)
        self.assertIn("/store/manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)
        self.assertIn("Stored Exports", html)
        self.assertIn("sha256:1234", html)
        self.assertIn("/stored/artifact?artifact_id=sha256%3A1234", html)

    def test_unknown_target_rendering_includes_blocked_status_notice_and_unavailable_store_state(self) -> None:
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
                    },
                    {
                        "action_id": "export_resolution_bundle",
                        "label": "Export resolution bundle",
                        "availability": "unavailable",
                    }
                ],
                "notices": [
                    {
                        "code": "resolution_manifest_not_available",
                        "severity": "warning",
                        "message": "No resolved synthetic record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
                    },
                    {
                        "code": "resolution_bundle_not_available",
                        "severity": "warning",
                        "message": "No resolved synthetic record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
                    }
                ],
            },
            stored_exports={
                "target_ref": "fixture:software/missing-demo-app@0.0.1",
                "store_actions": [
                    {
                        "action_id": "store_resolution_manifest",
                        "label": "Store resolution manifest locally",
                        "availability": "unavailable",
                    },
                    {
                        "action_id": "store_resolution_bundle",
                        "label": "Store resolution bundle locally",
                        "availability": "unavailable",
                    }
                ],
                "artifacts": [],
                "notices": [
                    {
                        "code": "stored_exports_target_not_available",
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
        self.assertIn("Export resolution bundle (unavailable)", html)
        self.assertIn("resolution_manifest_not_available", html)
        self.assertIn("resolution_bundle_not_available", html)
        self.assertIn("No local store actions are exposed for this target.", html)
        self.assertIn("Store resolution manifest locally (unavailable)", html)
        self.assertIn("Store resolution bundle locally (unavailable)", html)
        self.assertIn("stored_exports_target_not_available", html)

    def test_resolution_rendering_shows_github_release_source_origin_summary(self) -> None:
        html = render_resolution_workspace_html(
            {
                "session_id": "session.github",
                "resolved_resource_id": "resolved:sha256:aafe4582e67ab6d1c720388ac70622ba4e6a9797d8e17926ab1458dee78c13d8",
                "active_job": {
                    "job_id": "job-0100",
                    "status": "completed",
                    "target_ref": "github-release:cli/cli@v2.65.0",
                },
                "selected_object": {
                    "id": "obj.github-release.cli.cli",
                    "kind": "software",
                    "label": "GitHub CLI 2.65.0",
                },
                "source": {
                    "family": "github_releases",
                    "label": "GitHub Releases",
                    "locator": "https://github.com/cli/cli/releases/tag/v2.65.0",
                },
            }
        )

        self.assertIn("github-release:cli/cli@v2.65.0", html)
        self.assertIn("GitHub CLI 2.65.0", html)
        self.assertIn("GitHub Releases", html)
        self.assertIn("https://github.com/cli/cli/releases/tag/v2.65.0", html)
