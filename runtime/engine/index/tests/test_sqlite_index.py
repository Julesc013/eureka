from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.index import LocalIndexSqliteStore, build_index_records
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.source_registry import load_source_registry


def _build_catalog() -> NormalizedCatalog:
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in SyntheticSoftwareConnector().load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in GitHubReleasesConnector().load_source_records()
    )
    return NormalizedCatalog(synthetic_records + github_records)


class LocalIndexSqliteStoreTestCase(unittest.TestCase):
    def test_build_status_and_query_work_in_temp_directory(self) -> None:
        records = build_index_records(_build_catalog(), load_source_registry())
        store = LocalIndexSqliteStore()

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "local-index.sqlite3"
            build_metadata = store.build(index_path, records)
            status_metadata = store.read_metadata(index_path)
            query_metadata, query_results, query_notices = store.query(index_path, "synthetic")

        self.assertEqual(build_metadata.record_count, status_metadata.record_count)
        self.assertEqual(build_metadata.fts_mode, status_metadata.fts_mode)
        self.assertIn(build_metadata.fts_mode, {"fts5", "fallback_like"})
        self.assertGreater(status_metadata.record_count, 0)
        self.assertTrue(query_results)
        self.assertEqual(query_notices, ())
        self.assertEqual(query_metadata.index_path, str(index_path))

    def test_archive_query_and_no_result_query_are_bounded(self) -> None:
        records = build_index_records(_build_catalog(), load_source_registry())
        store = LocalIndexSqliteStore()

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "local-index.sqlite3"
            store.build(index_path, records)
            _, archive_results, _ = store.query(index_path, "archive")
            _, missing_results, missing_notices = store.query(index_path, "no such result at all")

        self.assertTrue(archive_results)
        self.assertFalse(missing_results)
        self.assertEqual(missing_notices[0].code, "local_index_no_results")


if __name__ == "__main__":
    unittest.main()
