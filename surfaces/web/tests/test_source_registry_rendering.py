from __future__ import annotations

import unittest

from surfaces.web.workbench import render_source_registry_html


class SourceRegistryRenderingTestCase(unittest.TestCase):
    def test_source_registry_renders_active_and_placeholder_sources(self) -> None:
        html = render_source_registry_html(
            {
                "status": "listed",
                "source_count": 2,
                "sources": [
                    {
                        "source_id": "synthetic-fixtures",
                        "name": "Synthetic Fixtures",
                        "source_family": "synthetic",
                        "status": "active_fixture",
                        "status_summary": "Active fixture-backed source record.",
                        "roles": ["fixture", "discovery_index"],
                        "surfaces": ["item_record", "fixture_file"],
                        "trust_lane": "fixture",
                        "authority_class": "repo_governed_fixture",
                        "object_types": ["software_release"],
                        "artifact_types": ["fixture_artifact"],
                        "identifier_types_emitted": ["target_ref"],
                        "connector": {"label": "Synthetic software connector", "status": "fixture_backed"},
                        "live_access_mode": "none",
                        "extraction_mode": "fixture_only",
                        "legal_posture": "repo_governed_fixture",
                        "freshness_model": "static_fixture",
                        "rights_notes": "Repo-governed demo fixtures only.",
                        "notes": "Active local-only source."
                    },
                    {
                        "source_id": "internet-archive-placeholder",
                        "name": "Internet Archive",
                        "source_family": "internet_archive",
                        "status": "placeholder",
                        "status_summary": "Placeholder record only. No runtime connector is implemented yet.",
                        "roles": ["preservation_anchor", "discovery_index"],
                        "surfaces": ["search", "item_record"],
                        "trust_lane": "preservation",
                        "authority_class": "public_archive",
                        "object_types": ["software_release"],
                        "artifact_types": ["archive_item"],
                        "identifier_types_emitted": ["archive_org_identifier"],
                        "connector": {"label": "Internet Archive connector", "status": "unimplemented"},
                        "live_access_mode": "deferred",
                        "extraction_mode": "deferred",
                        "legal_posture": "deferred_placeholder",
                        "freshness_model": "deferred",
                        "rights_notes": "Rights vary by item.",
                        "notes": "Planning placeholder only."
                    }
                ],
            }
        )

        self.assertIn("Eureka Source Registry", html)
        self.assertIn("Synthetic Fixtures", html)
        self.assertIn("Internet Archive", html)
        self.assertIn("[active_fixture]", html)
        self.assertIn("[placeholder]", html)
        self.assertIn("/source?id=internet-archive-placeholder", html)

    def test_selected_source_renders_detail_fields(self) -> None:
        html = render_source_registry_html(
            {
                "status": "available",
                "source_count": 1,
                "selected_source_id": "local-files-placeholder",
                "sources": [
                    {
                        "source_id": "local-files-placeholder",
                        "name": "Local Files",
                        "source_family": "local_files",
                        "status": "future",
                        "status_summary": "Future source record only. Runtime behavior remains deferred.",
                        "roles": ["action_provider"],
                        "surfaces": ["item_record"],
                        "trust_lane": "unknown",
                        "authority_class": "local_private_user_controlled",
                        "object_types": ["software_release"],
                        "artifact_types": ["local_file"],
                        "identifier_types_emitted": ["filesystem_path"],
                        "connector": {"label": "Local files connector", "status": "deferred"},
                        "live_access_mode": "local_private_later",
                        "extraction_mode": "local_private_later",
                        "legal_posture": "local_private_user_controlled",
                        "freshness_model": "local_mutable",
                        "rights_notes": "Local paths are private by default.",
                        "notes": "Future local-private source only."
                    }
                ],
            }
        )

        self.assertIn("Selected Source", html)
        self.assertIn("local-files-placeholder", html)
        self.assertIn("local_private_later", html)
        self.assertIn("Local paths are private by default.", html)


if __name__ == "__main__":
    unittest.main()
