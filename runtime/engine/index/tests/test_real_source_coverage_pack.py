from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.internet_archive_recorded import InternetArchiveRecordedConnector
from runtime.connectors.local_bundle_fixtures import LocalBundleFixturesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.index import LocalIndexSqliteStore, build_index_records
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_internet_archive_recorded_source_record,
    extract_local_bundle_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
    normalize_internet_archive_recorded_item,
    normalize_local_bundle_record,
)
from runtime.engine.synthetic_records import synthesize_member_normalized_records
from runtime.source_registry import load_source_registry


def _build_current_catalog() -> NormalizedCatalog:
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in SyntheticSoftwareConnector().load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in GitHubReleasesConnector().load_source_records()
    )
    internet_archive_records = tuple(
        normalize_internet_archive_recorded_item(
            extract_internet_archive_recorded_source_record(record)
        )
        for record in InternetArchiveRecordedConnector().load_source_records()
    )
    local_bundle_records = tuple(
        normalize_local_bundle_record(extract_local_bundle_source_record(record))
        for record in LocalBundleFixturesConnector().load_source_records()
    )
    synthetic_member_records = synthesize_member_normalized_records(local_bundle_records)
    return NormalizedCatalog(
        synthetic_records
        + github_records
        + internet_archive_records
        + local_bundle_records
        + synthetic_member_records
    )


class RealSourceCoveragePackIndexTestCase(unittest.TestCase):
    def test_current_corpus_index_finds_recorded_source_fixture_candidates(self) -> None:
        records = build_index_records(_build_current_catalog(), load_source_registry())
        store = LocalIndexSqliteStore()

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "local-index.sqlite3"
            store.build(index_path, records)
            _, windows_results, _ = store.query(index_path, "windows 7")
            _, thinkpad_results, _ = store.query(index_path, "thinkpad")
            _, seven_zip_results, _ = store.query(index_path, "7z920")
            _, driver_results, _ = store.query(index_path, "driver")

        self.assertTrue(
            any(result.source_id == "internet-archive-recorded-fixtures" for result in windows_results)
            or any(result.source_id == "local-bundle-fixtures" for result in windows_results)
        )
        self.assertTrue(
            any(result.source_id == "internet-archive-recorded-fixtures" for result in thinkpad_results)
            or any(result.source_id == "local-bundle-fixtures" for result in thinkpad_results)
        )
        self.assertTrue(any(result.source_id == "local-bundle-fixtures" for result in seven_zip_results))
        self.assertTrue(
            any(result.source_id == "internet-archive-recorded-fixtures" for result in driver_results)
            or any(result.source_id == "local-bundle-fixtures" for result in driver_results)
        )

    def test_member_records_preserve_parent_lineage_and_source_family(self) -> None:
        records = build_index_records(_build_current_catalog(), load_source_registry())

        driver_member = next(
            record
            for record in records
            if record.record_kind == "synthetic_member"
            and record.member_path == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )

        self.assertEqual(driver_member.source_id, "local-bundle-fixtures")
        self.assertEqual(driver_member.source_family, "local_bundle_fixtures")
        self.assertRegex(driver_member.target_ref or "", r"^member:sha256:[a-f0-9]{64}$")
        self.assertEqual(driver_member.parent_target_ref, "local-bundle-fixture:driver-support-cd@1.0")
        self.assertEqual(driver_member.parent_representation_id, "rep.local-bundle.driver-support-cd.zip")


if __name__ == "__main__":
    unittest.main()
