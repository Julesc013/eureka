from __future__ import annotations

import unittest

from runtime.connectors.article_scan_recorded import ArticleScanRecordedConnector
from runtime.engine.interfaces.extract import extract_article_scan_recorded_source_record
from runtime.engine.interfaces.normalize import normalize_article_scan_recorded_record


class ArticleScanRecordedConnectorTestCase(unittest.TestCase):
    def test_fixture_loads_article_segment_record(self) -> None:
        records = ArticleScanRecordedConnector().load_source_records()

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.source_name, "article_scan_recorded_fixture")
        self.assertEqual(
            record.target_ref,
            "article-scan-recorded:pc-magazine-1994-ray-tracing-article",
        )
        self.assertEqual(
            record.source_locator,
            "runtime/connectors/article_scan_recorded/fixtures/article_scan_fixture.json",
        )
        self.assertEqual(record.payload["article"]["page_range"], "123-128")
        self.assertIn("synthetic", " ".join(record.payload["fixture_notes"]).casefold())

    def test_normalized_record_preserves_article_lineage_and_evidence(self) -> None:
        source_record = ArticleScanRecordedConnector().load_source_records()[0]
        normalized = normalize_article_scan_recorded_record(
            extract_article_scan_recorded_source_record(source_record)
        )

        self.assertEqual(normalized.source_family, "article_scan_recorded")
        self.assertEqual(normalized.record_kind, "synthetic_member")
        self.assertEqual(normalized.object_kind, "document_article")
        self.assertEqual(normalized.member_kind, "article_segment")
        self.assertEqual(
            normalized.member_path,
            "articles/ray-tracing-on-the-desktop/pages-123-128.ocr.txt",
        )
        self.assertEqual(
            normalized.parent_target_ref,
            "article-scan-recorded:issue:pc.magazine.july.1994.fixture",
        )
        self.assertTrue(any(evidence.evidence_kind == "page_range" for evidence in normalized.evidence))
        self.assertTrue(any(evidence.evidence_kind == "ocr_text_fixture" for evidence in normalized.evidence))
        self.assertTrue(any("ray tracing" in evidence.claim_value.casefold() for evidence in normalized.evidence))

    def test_connector_has_no_live_network_or_scan_dependency(self) -> None:
        source_record = ArticleScanRecordedConnector().load_source_records()[0]
        normalized = normalize_article_scan_recorded_record(
            extract_article_scan_recorded_source_record(source_record)
        )

        for representation in normalized.representations:
            if representation.access_locator is not None:
                self.assertTrue(representation.access_locator.startswith("article-scan-recorded://"))
            if representation.fetch_locator is not None:
                self.assertTrue(
                    representation.fetch_locator.startswith(
                        "runtime/connectors/article_scan_recorded/fixtures/payloads/"
                    )
                )
        rendered = str(source_record.payload).casefold()
        self.assertIn("no real scan", rendered)
        self.assertIn("live source call", rendered)


if __name__ == "__main__":
    unittest.main()
