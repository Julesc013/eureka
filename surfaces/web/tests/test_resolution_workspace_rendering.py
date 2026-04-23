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
                "evidence": [
                    {
                        "claim_kind": "label",
                        "claim_value": "Synthetic Demo App",
                        "asserted_by_family": "synthetic_fixture",
                        "asserted_by_label": "Synthetic Fixture",
                        "evidence_kind": "recorded_fixture",
                        "evidence_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    }
                ],
                "representations": [
                    {
                        "representation_id": "rep.synthetic-demo-app.source",
                        "representation_kind": "fixture_artifact",
                        "label": "Synthetic demo app fixture artifact",
                        "content_type": "application/vnd.eureka.synthetic.bundle",
                        "byte_length": 4096,
                        "source_family": "synthetic_fixture",
                        "source_label": "Synthetic Fixture",
                        "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "access_path_id": "access.synthetic-demo-app.fixture",
                        "access_kind": "inspect",
                        "access_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "is_direct": False,
                    },
                    {
                        "representation_id": "rep.synthetic-demo-app.fixture-record",
                        "representation_kind": "fixture_record",
                        "label": "Synthetic demo app fixture record",
                        "content_type": "application/json",
                        "byte_length": 1024,
                        "source_family": "synthetic_fixture",
                        "source_label": "Synthetic Fixture",
                        "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "access_path_id": "access.synthetic-demo-app.fixture-record",
                        "access_kind": "view",
                        "access_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json#fixture:software/synthetic-demo-app@1.0.0",
                        "is_direct": False,
                    },
                ],
            },
            action_plan={
                "status": "planned",
                "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                "strategy_profile": {
                    "strategy_id": "preserve",
                    "label": "Preserve",
                    "description": "Prioritize deterministic export and local preservation steps over more direct use.",
                    "emphasis_hints": ["prioritize_manifest_export", "prioritize_local_store"],
                },
                "strategy_rationale": [
                    "Preserve strategy emphasizes deterministic export and local-store steps without changing the resolved truth model."
                ],
                "actions": [
                    {
                        "action_id": "inspect_primary_representation",
                        "label": "View Synthetic demo app fixture record",
                        "kind": "view_source_page",
                        "status": "recommended",
                        "reason_codes": ["inspect_before_host_specific_choice"],
                        "reason_messages": [
                            "No host profile was supplied, so inspecting a bounded source-backed path is recommended before any host-specific choice."
                        ],
                        "representation_label": "Synthetic demo app fixture record",
                        "access_kind": "view",
                        "source_family": "synthetic_fixture",
                        "route_hint": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json#fixture:software/synthetic-demo-app@1.0.0",
                    },
                    {
                        "action_id": "export_resolution_manifest",
                        "label": "Export resolution manifest",
                        "kind": "export_manifest",
                        "status": "available",
                        "reason_codes": ["manifest_export_available_for_inspection"],
                        "reason_messages": [
                            "A deterministic manifest export is available as a bounded inspection and evidence-preserving step."
                        ],
                        "route_hint": "/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                    },
                    {
                        "action_id": "store_resolution_manifest",
                        "label": "Store resolution manifest locally",
                        "kind": "store_manifest",
                        "status": "unavailable",
                        "reason_codes": ["store_context_not_configured"],
                        "reason_messages": [
                            "No local store context was configured for this action-plan request."
                        ],
                    },
                ],
                "compatibility_reasons": [],
                "notices": [],
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
        self.assertIn("Evidence", html)
        self.assertIn("label = Synthetic Demo App", html)
        self.assertIn("Known Representations/Access Paths", html)
        self.assertIn("Synthetic demo app fixture artifact", html)
        self.assertIn("fixture_artifact", html)
        self.assertIn("inspect", html)
        self.assertIn("Synthetic demo app fixture record", html)
        self.assertIn("contracts/archive/fixtures/software/synthetic_resolution_fixture.json#fixture:software/synthetic-demo-app@1.0.0", html)
        self.assertIn("Recommended Next Steps", html)
        self.assertIn("Strategy: <strong>preserve</strong>", html)
        self.assertIn("Strategy rationale", html)
        self.assertIn("View Synthetic demo app fixture record", html)
        self.assertIn("Export resolution manifest", html)
        self.assertIn("Store resolution manifest locally", html)
        self.assertIn("/action-plan?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)
        self.assertIn("/?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0&amp;strategy=acquire", html)
        self.assertIn("Export resolution manifest", html)
        self.assertIn("/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)
        self.assertIn("Export resolution bundle", html)
        self.assertIn("/actions/export-resolution-bundle?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)
        self.assertIn("Store resolution manifest locally", html)
        self.assertIn("/store/manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)
        self.assertIn("Compatibility", html)
        self.assertIn("/compatibility?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0&amp;host=windows-x86_64", html)
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
            action_plan={
                "status": "blocked",
                "target_ref": "fixture:software/missing-demo-app@0.0.1",
                "actions": [],
                "compatibility_reasons": [],
                "notices": [
                    {
                        "code": "target_ref_not_found",
                        "severity": "warning",
                        "message": "No bounded record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
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
        self.assertIn("/absence/resolve?target_ref=fixture%3Asoftware%2Fmissing-demo-app%400.0.1", html)
        self.assertIn("Recommended Next Steps", html)
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
                "evidence": [
                    {
                        "claim_kind": "version",
                        "claim_value": "v2.65.0",
                        "asserted_by_family": "github_releases",
                        "asserted_by_label": "GitHub Releases",
                        "evidence_kind": "recorded_source_payload",
                        "evidence_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                        "asserted_at": "2024-11-13T00:00:00Z",
                    }
                ],
                "representations": [
                    {
                        "representation_id": "rep.github-release.cli.cli.v2.65.0.release-page",
                        "representation_kind": "release_page",
                        "label": "GitHub CLI 2.65.0 release page",
                        "content_type": "text/html",
                        "source_family": "github_releases",
                        "source_label": "GitHub Releases",
                        "source_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                        "access_path_id": "access.github-release.cli.cli.v2.65.0.release",
                        "access_kind": "view",
                        "access_locator": "https://github.com/cli/cli/releases/tag/v2.65.0",
                        "is_direct": False,
                    },
                    {
                        "representation_id": "rep.github-release.cli.cli.v2.65.0.asset.0",
                        "representation_kind": "release_asset",
                        "label": "gh_2.65.0_windows_amd64.msi",
                        "content_type": "application/x-msi",
                        "byte_length": 12123904,
                        "source_family": "github_releases",
                        "source_label": "GitHub Releases",
                        "source_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                        "access_path_id": "access.github-release.cli.cli.v2.65.0.asset.0",
                        "access_kind": "download",
                        "access_locator": "https://github.com/cli/cli/releases/download/v2.65.0/gh_2.65.0_windows_amd64.msi",
                        "is_direct": True,
                    },
                ],
            }
        )

        self.assertIn("github-release:cli/cli@v2.65.0", html)
        self.assertIn("GitHub CLI 2.65.0", html)
        self.assertIn("GitHub Releases", html)
        self.assertIn("https://github.com/cli/cli/releases/tag/v2.65.0", html)
        self.assertIn("version = v2.65.0", html)
        self.assertIn("Known Representations/Access Paths", html)
        self.assertIn("GitHub CLI 2.65.0 release page", html)
        self.assertIn("gh_2.65.0_windows_amd64.msi", html)

    def test_resolution_rendering_can_embed_representation_handoff_section(self) -> None:
        html = render_resolution_workspace_html(
            {
                "session_id": "session.handoff",
                "resolved_resource_id": "resolved:sha256:aafe4582e67ab6d1c720388ac70622ba4e6a9797d8e17926ab1458dee78c13d8",
                "active_job": {
                    "job_id": "job-0200",
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
                "evidence": [],
                "representations": [],
            },
            handoff={
                "status": "available",
                "target_ref": "github-release:cli/cli@v2.65.0",
                "preferred_representation_id": "rep.github-release.cli.cli.v2.65.0.asset.0",
                "compatibility_status": "compatible",
                "strategy_profile": {
                    "strategy_id": "acquire",
                    "label": "Acquire",
                    "description": "Prioritize direct access paths when bounded signals support them.",
                    "emphasis_hints": ["prioritize_direct_access"],
                },
                "host_profile": {
                    "host_profile_id": "windows-x86_64",
                    "os_family": "windows",
                    "architecture": "x86_64",
                    "features": [],
                },
                "compatibility_reasons": [
                    {
                        "code": "os_family_supported",
                        "message": "Host os_family 'windows' matches the bounded required_os_families.",
                    }
                ],
                "selections": [
                    {
                        "representation_id": "rep.github-release.cli.cli.v2.65.0.asset.0",
                        "representation_kind": "release_asset",
                        "label": "gh_2.65.0_windows_amd64.msi",
                        "selection_status": "preferred",
                        "reason_codes": ["strategy_acquire_prefers_host_fit_payload"],
                        "reason_messages": [
                            "The active acquire strategy prefers the bounded payload representation that best fits the selected host profile."
                        ],
                        "source_family": "github_releases",
                        "access_kind": "download",
                        "source_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                        "access_locator": "https://github.com/cli/cli/releases/download/v2.65.0/gh_2.65.0_windows_amd64.msi",
                    },
                    {
                        "representation_id": "rep.github-release.cli.cli.release-metadata",
                        "representation_kind": "release_page",
                        "label": "GitHub CLI 2.65.0 release page",
                        "selection_status": "available",
                        "reason_codes": ["metadata_representation_available"],
                        "reason_messages": [
                            "This bounded metadata-like representation remains available for inspection and explanation."
                        ],
                        "source_family": "github_releases",
                        "access_kind": "view",
                        "source_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                        "access_locator": "https://github.com/cli/cli/releases/tag/v2.65.0",
                    },
                    {
                        "representation_id": "rep.github-release.cli.cli.v2.65.0.asset.1",
                        "representation_kind": "release_asset",
                        "label": "gh_2.65.0_checksums.txt",
                        "selection_status": "unsuitable",
                        "reason_codes": ["strategy_not_preferred"],
                        "reason_messages": [
                            "This bounded representation remains visible as an alternative rather than the current preferred fit."
                        ],
                        "source_family": "github_releases",
                        "access_kind": "download",
                        "source_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                        "access_locator": "https://github.com/cli/cli/releases/download/v2.65.0/gh_2.65.0_checksums.txt",
                    },
                ],
                "notices": [],
                "evidence": [],
            },
        )

        self.assertIn("Representation Handoff", html)
        self.assertIn("Open the dedicated handoff page", html)
        self.assertIn("Preferred bounded fit", html)
        self.assertIn("Available alternatives", html)
        self.assertIn("Unsuitable choices", html)
        self.assertIn("gh_2.65.0_windows_amd64.msi", html)
        self.assertIn("/handoff?target_ref=github-release%3Acli%2Fcli%40v2.65.0&amp;host=windows-x86_64&amp;strategy=acquire", html)
