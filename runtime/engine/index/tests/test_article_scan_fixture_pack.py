from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.article_scan_recorded import ArticleScanRecordedConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.index import LocalIndexEngineService, LocalIndexSqliteStore, build_index_records
from runtime.engine.interfaces.extract import extract_article_scan_recorded_source_record
from runtime.engine.interfaces.normalize import normalize_article_scan_recorded_record
from runtime.engine.interfaces.public import LocalIndexBuildRequest, LocalIndexQueryRequest
from runtime.source_registry import load_source_registry


def _article_scan_catalog() -> NormalizedCatalog:
    return NormalizedCatalog(
        tuple(
            normalize_article_scan_recorded_record(
                extract_article_scan_recorded_source_record(record)
            )
            for record in ArticleScanRecordedConnector().load_source_records()
        )
    )


class ArticleScanFixtureIndexTestCase(unittest.TestCase):
    def test_article_segment_indexes_lineage_and_evidence(self) -> None:
        records = build_index_records(_article_scan_catalog(), load_source_registry())
        article = next(
            record
            for record in records
            if record.record_kind == "synthetic_member"
            and record.source_id == "article-scan-recorded-fixtures"
        )

        self.assertEqual(
            article.target_ref,
            "article-scan-recorded:pc-magazine-1994-ray-tracing-article",
        )
        self.assertEqual(
            article.member_path,
            "articles/ray-tracing-on-the-desktop/pages-123-128.ocr.txt",
        )
        self.assertEqual(article.member_kind, "article_segment")
        self.assertEqual(article.primary_lane, "inside_bundles")
        self.assertIn("best_direct_answer", article.result_lanes)
        self.assertIn("article_segment_has_page_locator", article.user_cost_reasons)
        self.assertTrue(any("ocr_text_fixture" in evidence for evidence in article.evidence))
        self.assertNotIn(str(Path.home()), article.search_text())

    def test_local_index_query_finds_article_segment(self) -> None:
        catalog = _article_scan_catalog()
        service = LocalIndexEngineService(
            catalog=catalog,
            source_registry=load_source_registry(),
            sqlite_store=LocalIndexSqliteStore(),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "article-scan.sqlite3")
            service.build_index(LocalIndexBuildRequest.from_parts(index_path))
            result = service.query_index(
                LocalIndexQueryRequest.from_parts(index_path, "1994 ray tracing")
            )

        self.assertTrue(result.results)
        top = result.results[0]
        self.assertEqual(top.source_id, "article-scan-recorded-fixtures")
        self.assertEqual(top.record_kind, "synthetic_member")
        self.assertEqual(top.member_kind, "article_segment")
        self.assertIn("pages-123-128.ocr.txt", top.member_path or "")
        self.assertIn("best_direct_answer", top.result_lanes)


if __name__ == "__main__":
    unittest.main()
