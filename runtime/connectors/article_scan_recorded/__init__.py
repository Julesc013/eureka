"""Recorded article/scan fixture connector for bounded article evidence."""

from runtime.connectors.article_scan_recorded.connector import ArticleScanRecordedConnector
from runtime.connectors.article_scan_recorded.source import (
    DEFAULT_ARTICLE_SCAN_RECORDED_FIXTURE_PATH,
    article_scan_recorded_target_ref,
    load_article_scan_recorded_source_records,
)

__all__ = [
    "ArticleScanRecordedConnector",
    "DEFAULT_ARTICLE_SCAN_RECORDED_FIXTURE_PATH",
    "article_scan_recorded_target_ref",
    "load_article_scan_recorded_source_records",
]
