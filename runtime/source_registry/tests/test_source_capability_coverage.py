from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.source_registry import (
    COVERAGE_DEPTHS,
    MalformedSourceRecordError,
    SOURCE_CAPABILITY_FIELDS,
    load_source_registry,
)


class SourceCapabilityCoverageTestCase(unittest.TestCase):
    def test_all_seed_records_load_capability_and_coverage_objects(self) -> None:
        registry = load_source_registry()

        for record in registry.records:
            with self.subTest(source_id=record.source_id):
                self.assertEqual(set(record.capabilities.to_dict()), set(SOURCE_CAPABILITY_FIELDS))
                self.assertIn(record.coverage.coverage_depth, COVERAGE_DEPTHS)
                self.assertIsInstance(record.coverage.indexed_scopes, tuple)
                self.assertIsInstance(record.coverage.current_limitations, tuple)

    def test_coverage_depths_and_postures_are_truthful_for_seed_sources(self) -> None:
        records = {record.source_id: record for record in load_source_registry().records}

        synthetic = records["synthetic-fixtures"]
        self.assertEqual(synthetic.status, "active_fixture")
        self.assertEqual(synthetic.coverage.coverage_depth, "action_indexed")
        self.assertTrue(synthetic.capabilities.fixture_backed)
        self.assertTrue(synthetic.capabilities.supports_member_listing)
        self.assertFalse(synthetic.capabilities.live_supported)

        github = records["github-releases-recorded-fixtures"]
        self.assertEqual(github.status, "active_recorded_fixture")
        self.assertEqual(github.coverage.coverage_depth, "representation_indexed")
        self.assertTrue(github.capabilities.recorded_fixture_backed)
        self.assertEqual(github.coverage.connector_mode, "recorded_fixture_only")
        self.assertFalse(github.capabilities.live_supported)

        internet_archive_recorded = records["internet-archive-recorded-fixtures"]
        self.assertEqual(internet_archive_recorded.status, "active_recorded_fixture")
        self.assertEqual(internet_archive_recorded.coverage.coverage_depth, "representation_indexed")
        self.assertTrue(internet_archive_recorded.capabilities.recorded_fixture_backed)
        self.assertTrue(internet_archive_recorded.capabilities.supports_file_listing)
        self.assertFalse(internet_archive_recorded.capabilities.live_supported)
        self.assertTrue(internet_archive_recorded.capabilities.live_deferred)

        article_scan = records["article-scan-recorded-fixtures"]
        self.assertEqual(article_scan.status, "active_recorded_fixture")
        self.assertEqual(article_scan.coverage.coverage_depth, "content_or_member_indexed")
        self.assertTrue(article_scan.capabilities.recorded_fixture_backed)
        self.assertTrue(article_scan.capabilities.supports_content_text)
        self.assertTrue(article_scan.capabilities.supports_member_listing)
        self.assertFalse(article_scan.capabilities.live_supported)
        self.assertTrue(article_scan.capabilities.live_deferred)

        local_bundle = records["local-bundle-fixtures"]
        self.assertEqual(local_bundle.status, "active_fixture")
        self.assertEqual(local_bundle.coverage.coverage_depth, "action_indexed")
        self.assertTrue(local_bundle.capabilities.fixture_backed)
        self.assertTrue(local_bundle.capabilities.supports_member_listing)
        self.assertTrue(local_bundle.capabilities.supports_action_paths)
        self.assertFalse(local_bundle.capabilities.local_private)
        self.assertFalse(local_bundle.capabilities.live_supported)

        for source_id in (
            "internet-archive-placeholder",
            "wayback-memento-placeholder",
            "software-heritage-placeholder",
        ):
            with self.subTest(source_id=source_id):
                record = records[source_id]
                self.assertEqual(record.status, "placeholder")
                self.assertEqual(record.coverage.coverage_depth, "source_known")
                self.assertFalse(record.capabilities.live_supported)
                self.assertTrue(record.capabilities.live_deferred)

        local_files = records["local-files-placeholder"]
        self.assertEqual(local_files.status, "local_private_future")
        self.assertEqual(local_files.coverage.coverage_depth, "source_known")
        self.assertTrue(local_files.capabilities.local_private)
        self.assertFalse(local_files.capabilities.supports_action_paths)

    def test_registry_filters_by_coverage_capability_and_connector_mode(self) -> None:
        registry = load_source_registry()

        self.assertEqual(
            {record.source_id for record in registry.list_records(coverage_depth="source_known")},
            {
                "internet-archive-placeholder",
                "local-files-placeholder",
                "software-heritage-placeholder",
                "wayback-memento-placeholder",
            },
        )
        self.assertEqual(
            {
                record.source_id
                for record in registry.list_records(capability="recorded_fixture_backed")
            },
            {
                "article-scan-recorded-fixtures",
                "github-releases-recorded-fixtures",
                "internet-archive-recorded-fixtures",
                "manual-document-recorded-fixtures",
                "package-registry-recorded-fixtures",
                "review-description-recorded-fixtures",
                "software-heritage-recorded-fixtures",
                "sourceforge-recorded-fixtures",
                "wayback-memento-recorded-fixtures",
            },
        )
        self.assertEqual(
            {record.source_id for record in registry.list_records(connector_mode="fixture_only")},
            {"local-bundle-fixtures", "synthetic-fixtures"},
        )

    def test_invalid_coverage_depth_is_rejected(self) -> None:
        record = _load_seed_record("synthetic-fixtures.source.json")
        record["coverage"]["coverage_depth"] = "semantic_magic"

        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "invalid.source.json"
            source_path.write_text(json.dumps(record), encoding="utf-8")

            with self.assertRaises(MalformedSourceRecordError):
                load_source_registry(Path(temp_dir))

    def test_invalid_capability_shape_is_rejected(self) -> None:
        record = _load_seed_record("synthetic-fixtures.source.json")
        record["capabilities"]["supports_search"] = "yes"

        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "invalid.source.json"
            source_path.write_text(json.dumps(record), encoding="utf-8")

            with self.assertRaises(MalformedSourceRecordError):
                load_source_registry(Path(temp_dir))

    def test_unknown_coverage_field_is_rejected(self) -> None:
        record = _load_seed_record("synthetic-fixtures.source.json")
        record["coverage"]["semantic_score"] = "not-part-of-v0"

        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "invalid.source.json"
            source_path.write_text(json.dumps(record), encoding="utf-8")

            with self.assertRaises(MalformedSourceRecordError):
                load_source_registry(Path(temp_dir))


def _load_seed_record(filename: str) -> dict[str, object]:
    root = Path(__file__).resolve().parents[3]
    source_path = root / "control" / "inventory" / "sources" / filename
    return json.loads(source_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
