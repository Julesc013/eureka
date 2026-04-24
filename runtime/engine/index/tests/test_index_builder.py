from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.index import build_index_records
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


class LocalIndexRecordBuilderTestCase(unittest.TestCase):
    def test_builder_produces_bounded_records_for_current_corpus(self) -> None:
        records = build_index_records(_build_catalog(), load_source_registry())

        self.assertTrue(records)
        record_kinds = {record.record_kind for record in records}
        self.assertEqual(
            record_kinds,
            {
                "resolved_object",
                "state_or_release",
                "representation",
                "member",
                "evidence",
                "source_record",
            },
        )

    def test_builder_preserves_source_ids_and_resolved_resource_ids(self) -> None:
        records = build_index_records(_build_catalog(), load_source_registry())

        synthetic_object = next(
            record
            for record in records
            if record.record_kind == "resolved_object"
            and record.target_ref == "fixture:software/synthetic-demo-app@1.0.0"
        )
        github_object = next(
            record
            for record in records
            if record.record_kind == "resolved_object"
            and record.target_ref == "github-release:archivebox/archivebox@v0.8.5"
        )

        self.assertEqual(synthetic_object.source_id, "synthetic-fixtures")
        self.assertEqual(github_object.source_id, "github-releases-recorded-fixtures")
        self.assertIsNotNone(synthetic_object.resolved_resource_id)
        self.assertIsNotNone(github_object.resolved_resource_id)

    def test_builder_emits_representation_member_evidence_and_source_records(self) -> None:
        records = build_index_records(_build_catalog(), load_source_registry())

        representation_record = next(
            record
            for record in records
            if record.record_kind == "representation"
            and record.representation_id == "rep.synthetic-demo-app.package"
        )
        member_record = next(
            record
            for record in records
            if record.record_kind == "member" and record.member_path == "README.txt"
        )
        evidence_record = next(record for record in records if record.record_kind == "evidence")
        source_record = next(
            record
            for record in records
            if record.record_kind == "source_record"
            and record.source_id == "github-releases-recorded-fixtures"
        )

        self.assertEqual(representation_record.source_id, "synthetic-fixtures")
        self.assertEqual(member_record.representation_id, "rep.synthetic-demo-app.package")
        self.assertTrue(evidence_record.evidence)
        self.assertEqual(source_record.source_family, "github_releases")


if __name__ == "__main__":
    unittest.main()
