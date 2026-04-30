from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.source_expansion_recorded import SourceExpansionRecordedConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.index import LocalIndexSqliteStore, build_index_records
from runtime.engine.interfaces.extract import extract_source_expansion_recorded_source_record
from runtime.engine.interfaces.normalize import normalize_source_expansion_recorded_record
from runtime.source_registry import load_source_registry


def _build_source_expansion_catalog() -> NormalizedCatalog:
    return NormalizedCatalog(
        tuple(
            normalize_source_expansion_recorded_record(
                extract_source_expansion_recorded_source_record(record)
            )
            for record in SourceExpansionRecordedConnector().load_source_records()
        )
    )


class SourceExpansionV2IndexTestCase(unittest.TestCase):
    def test_fixture_records_build_source_backed_index_entries(self) -> None:
        records = build_index_records(_build_source_expansion_catalog(), load_source_registry())
        source_ids = {record.source_id for record in records if record.source_id}

        self.assertGreaterEqual(
            source_ids,
            {
                "manual-document-recorded-fixtures",
                "package-registry-recorded-fixtures",
                "review-description-recorded-fixtures",
                "software-heritage-recorded-fixtures",
                "sourceforge-recorded-fixtures",
                "wayback-memento-recorded-fixtures",
            },
        )
        self.assertTrue(
            any(
                record.record_kind == "synthetic_member"
                and record.source_id == "package-registry-recorded-fixtures"
                and record.member_path == "vc6sp/README-SP.txt"
                for record in records
            )
        )

    def test_selected_queries_find_fixture_only_source_families(self) -> None:
        records = build_index_records(_build_source_expansion_catalog(), load_source_registry())
        store = LocalIndexSqliteStore()

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "source-expansion.sqlite3"
            store.build(index_path, records)
            query_results = {
                query: store.query(index_path, query)[1]
                for query in (
                    "archived Firefox XP release notes",
                    "Visual C++ 6 service pack readme",
                    "manual for Sound Blaster CT1740",
                    "software heritage source snapshot",
                    "classic Windows file transfer app blue globe",
                )
            }

        self.assertTrue(
            any(
                result.source_id == "wayback-memento-recorded-fixtures"
                and result.compatibility_evidence
                for result in query_results["archived Firefox XP release notes"]
            )
        )
        self.assertTrue(
            any(
                result.source_id == "package-registry-recorded-fixtures"
                and result.record_kind == "synthetic_member"
                for result in query_results["Visual C++ 6 service pack readme"]
            )
        )
        self.assertTrue(
            any(
                result.source_id == "manual-document-recorded-fixtures"
                and result.primary_lane == "documentation"
                for result in query_results["manual for Sound Blaster CT1740"]
            )
        )
        self.assertTrue(
            any(
                result.source_id == "software-heritage-recorded-fixtures"
                for result in query_results["software heritage source snapshot"]
            )
        )
        self.assertTrue(
            any(
                result.source_id == "sourceforge-recorded-fixtures"
                for result in query_results["classic Windows file transfer app blue globe"]
            )
        )


if __name__ == "__main__":
    unittest.main()
