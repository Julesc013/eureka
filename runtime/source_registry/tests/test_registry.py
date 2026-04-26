from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.source_registry import (
    DEFAULT_SOURCE_INVENTORY_DIR,
    DuplicateSourceIdError,
    MalformedSourceRecordError,
    MissingRequiredFieldError,
    SourceInventoryNotFoundError,
    SourceRecordNotFoundError,
    load_source_registry,
)


class SourceRegistryTestCase(unittest.TestCase):
    def test_load_source_registry_reads_all_seed_records(self) -> None:
        registry = load_source_registry()

        self.assertEqual(len(registry.records), 6)
        self.assertEqual(
            [record.source_id for record in registry.records],
            [
                "github-releases-recorded-fixtures",
                "internet-archive-placeholder",
                "local-files-placeholder",
                "software-heritage-placeholder",
                "synthetic-fixtures",
                "wayback-memento-placeholder",
            ],
        )

    def test_get_record_returns_known_source_and_unknown_source_raises_structured_error(self) -> None:
        registry = load_source_registry()

        record = registry.get_record("synthetic-fixtures")
        self.assertEqual(record.name, "Synthetic Fixtures")
        self.assertEqual(record.connector.entrypoint, "runtime.connectors.synthetic_software")

        with self.assertRaises(SourceRecordNotFoundError):
            registry.get_record("missing-source")

    def test_list_records_filters_by_status_source_family_role_and_surface(self) -> None:
        registry = load_source_registry()

        self.assertEqual(
            {record.source_id for record in registry.list_records(status="active_fixture")},
            {"synthetic-fixtures"},
        )
        self.assertEqual(
            {record.source_id for record in registry.list_records(status="active_recorded_fixture")},
            {"github-releases-recorded-fixtures"},
        )
        self.assertEqual(
            {record.source_id for record in registry.list_records(source_family="internet_archive")},
            {"internet-archive-placeholder"},
        )
        self.assertEqual(
            {record.source_id for record in registry.list_records(role="preservation_anchor")},
            {
                "internet-archive-placeholder",
                "software-heritage-placeholder",
                "wayback-memento-placeholder",
            },
        )
        self.assertEqual(
            {record.source_id for record in registry.list_records(surface="replay")},
            {"wayback-memento-placeholder"},
        )

    def test_missing_inventory_directory_raises_structured_error(self) -> None:
        missing_dir = DEFAULT_SOURCE_INVENTORY_DIR / "missing"

        with self.assertRaises(SourceInventoryNotFoundError):
            load_source_registry(missing_dir)

    def test_malformed_json_raises_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "broken.source.json"
            source_path.write_text("{not-json}", encoding="utf-8")

            with self.assertRaises(MalformedSourceRecordError):
                load_source_registry(Path(temp_dir))

    def test_duplicate_source_ids_raise_structured_error(self) -> None:
        valid_record = {
            "source_id": "duplicate",
            "name": "Duplicate",
            "source_family": "synthetic",
            "status": "active_fixture",
            "roles": ["fixture"],
            "surfaces": ["fixture_file"],
            "trust_lane": "fixture",
            "authority_class": "repo_governed_fixture",
            "protocols": ["fixture_json"],
            "object_types": ["software_release"],
            "artifact_types": ["fixture_artifact"],
            "identifier_types_emitted": ["target_ref"],
            "connector": {"label": "Fixture connector", "status": "fixture_backed"},
            "fixture_paths": [],
            "live_access": {"mode": "none"},
            "extraction_policy": {"mode": "fixture_only"},
            "rights_notes": "Fixtures only.",
            "legal_posture": "repo_governed_fixture",
            "freshness_model": "static_fixture",
            "capabilities": {
                "supports_search": True,
                "supports_item_metadata": True,
                "supports_file_listing": False,
                "supports_bulk_access": False,
                "supports_delta_or_feed": False,
                "supports_live_probe": False,
                "supports_member_listing": False,
                "supports_reviews_or_comments": False,
                "supports_hashes": False,
                "supports_signatures": False,
                "supports_content_text": False,
                "supports_temporal_captures": False,
                "supports_action_paths": False,
                "auth_required": False,
                "network_required": False,
                "local_private": False,
                "fixture_backed": True,
                "recorded_fixture_backed": False,
                "live_supported": False,
                "live_deferred": False
            },
            "coverage": {
                "coverage_depth": "metadata_indexed",
                "coverage_status": "active_fixture_scope",
                "indexed_scopes": ["catalog_records", "item_metadata"],
                "connector_mode": "fixture_only",
                "last_fixture_update": "static_fixture",
                "coverage_notes": "Temporary test fixture.",
                "current_limitations": ["test fixture only"],
                "next_coverage_step": "none"
            },
            "notes": "Demo record."
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            first_path = Path(temp_dir) / "one.source.json"
            second_path = Path(temp_dir) / "two.source.json"
            first_path.write_text(json.dumps(valid_record), encoding="utf-8")
            second_path.write_text(json.dumps(valid_record), encoding="utf-8")

            with self.assertRaises(DuplicateSourceIdError):
                load_source_registry(Path(temp_dir))

    def test_missing_required_field_raises_structured_error(self) -> None:
        invalid_record = {
            "source_id": "missing-name"
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "invalid.source.json"
            source_path.write_text(json.dumps(invalid_record), encoding="utf-8")

            with self.assertRaises(MissingRequiredFieldError):
                load_source_registry(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
