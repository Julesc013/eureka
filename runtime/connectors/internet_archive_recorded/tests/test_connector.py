from __future__ import annotations

import unittest

from runtime.connectors.internet_archive_recorded import InternetArchiveRecordedConnector
from runtime.engine.interfaces.extract import extract_internet_archive_recorded_source_record
from runtime.engine.interfaces.normalize import normalize_internet_archive_recorded_item


class InternetArchiveRecordedConnectorTestCase(unittest.TestCase):
    def test_fixture_loads_item_and_file_list_records(self) -> None:
        records = InternetArchiveRecordedConnector().load_source_records()

        self.assertEqual(len(records), 3)
        self.assertEqual(records[0].source_name, "internet_archive_recorded_fixture")
        self.assertEqual(records[0].target_ref, "internet-archive-recorded:ia-win7-utility-pack-fixture")
        self.assertEqual(
            records[0].source_locator,
            "runtime/connectors/internet_archive_recorded/fixtures/internet_archive_items_fixture.json",
        )
        self.assertIn("files", records[0].payload["item"])

    def test_normalized_records_preserve_source_and_evidence(self) -> None:
        record = next(
            item
            for item in InternetArchiveRecordedConnector().load_source_records()
            if item.target_ref == "internet-archive-recorded:ia-thinkpad-t42-wireless-support-fixture"
        )
        normalized = normalize_internet_archive_recorded_item(
            extract_internet_archive_recorded_source_record(record)
        )

        self.assertEqual(normalized.source_family, "internet_archive_recorded")
        self.assertEqual(normalized.source_family_label, "Internet Archive Recorded Fixtures")
        self.assertEqual(normalized.object_kind, "software")
        self.assertTrue(
            any(
                representation.filename == "DRIVERS/WIFI/THINKPAD_T42/WIN2000/DRIVER.INF"
                for representation in normalized.representations
            )
        )
        evidence_kinds = {evidence.evidence_kind for evidence in normalized.evidence}
        self.assertIn("source_metadata", evidence_kinds)
        self.assertIn("file_listing", evidence_kinds)
        self.assertTrue(
            any("Windows 2000" in evidence.claim_value for evidence in normalized.evidence)
        )

    def test_connector_has_no_live_network_path(self) -> None:
        connector = InternetArchiveRecordedConnector()
        record = connector.load_source_records()[0]
        normalized = normalize_internet_archive_recorded_item(
            extract_internet_archive_recorded_source_record(record)
        )

        self.assertFalse(any(representation.is_fetchable for representation in normalized.representations))
        self.assertTrue(
            all(
                representation.access_locator is None
                or representation.access_locator.startswith("ia-recorded://")
                for representation in normalized.representations
            )
        )


if __name__ == "__main__":
    unittest.main()
