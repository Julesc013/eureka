from __future__ import annotations

import unittest

from runtime.gateway.public_api import representation_selection_envelope_to_view_model


class RepresentationSelectionViewModelsTestCase(unittest.TestCase):
    def test_representation_selection_envelope_maps_to_shared_view_model_shape(self) -> None:
        view_model = representation_selection_envelope_to_view_model(
            {
                "status": "available",
                "target_ref": "github-release:cli/cli@v2.65.0",
                "resolved_resource_id": "resolved:sha256:test",
                "compatibility_status": "compatible",
                "preferred_representation_id": "rep.github-release.cli.cli.v2.65.0.asset.0",
                "primary_object": {
                    "id": "obj.github-release.cli.cli",
                    "kind": "software",
                    "label": "GitHub CLI 2.65.0",
                },
                "source": {
                    "family": "github_releases",
                    "label": "GitHub Releases",
                    "locator": "https://github.com/cli/cli/releases/tag/v2.65.0",
                },
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
                "evidence": [
                    {
                        "claim_kind": "label",
                        "claim_value": "GitHub CLI 2.65.0",
                        "asserted_by_family": "github_releases",
                        "asserted_by_label": "GitHub Releases",
                        "evidence_kind": "recorded_source_payload",
                        "evidence_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                    }
                ],
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
                        "reason_messages": ["The active acquire strategy prefers the bounded payload representation that best fits the selected host profile."],
                        "source_family": "github_releases",
                        "source_label": "GitHub Releases",
                        "source_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                        "access_kind": "download",
                        "access_locator": "https://github.com/cli/cli/releases/download/v2.65.0/gh_2.65.0_windows_amd64.msi",
                        "content_type": "application/x-msi",
                        "byte_length": 12123904,
                        "is_direct": True,
                        "host_profile_id": "windows-x86_64",
                        "strategy_id": "acquire",
                    }
                ],
                "notices": [],
            }
        )

        self.assertEqual(view_model["status"], "available")
        self.assertEqual(view_model["compatibility_status"], "compatible")
        self.assertEqual(
            view_model["preferred_representation_id"],
            "rep.github-release.cli.cli.v2.65.0.asset.0",
        )
        self.assertEqual(view_model["host_profile"]["host_profile_id"], "windows-x86_64")
        self.assertEqual(view_model["strategy_profile"]["strategy_id"], "acquire")
        self.assertEqual(view_model["selections"][0]["selection_status"], "preferred")
        self.assertEqual(view_model["selections"][0]["access_kind"], "download")


if __name__ == "__main__":
    unittest.main()
