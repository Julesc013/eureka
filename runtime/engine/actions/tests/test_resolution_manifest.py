from __future__ import annotations

import unittest

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.actions import ResolutionManifestExportService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.resolve import resolved_resource_id_for_record


class ResolutionManifestExportServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        source_records = SyntheticSoftwareConnector().load_source_records()
        self.normalized_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in source_records
        )
        self.service = ResolutionManifestExportService(NormalizedCatalog(self.normalized_records))

    def test_manifest_export_for_known_target_is_deterministic(self) -> None:
        manifest = self.service.export_manifest("fixture:software/synthetic-demo-app@1.0.0")

        self.assertEqual(
            manifest,
            {
                "manifest_kind": "eureka.resolution_manifest",
                "manifest_version": "0.1.0-draft",
                "generated_from": {
                    "kind": "normalized_resolution_record",
                    "source_name": "synthetic_software_fixture",
                    "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                },
                "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                "resolved_resource_id": resolved_resource_id_for_record(self.normalized_records[0]),
                "primary_object": {
                    "id": "obj.synthetic-demo-app",
                    "kind": "software",
                    "label": "Synthetic Demo App",
                },
                "source": {
                    "family": "synthetic_fixture",
                    "label": "Synthetic Fixture",
                    "locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                },
                "evidence": [
                    {
                        "claim_kind": "label",
                        "claim_value": "Synthetic Demo App",
                        "asserted_by_family": "synthetic_fixture",
                        "asserted_by_label": "Synthetic Fixture",
                        "evidence_kind": "recorded_fixture",
                        "evidence_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    },
                    {
                        "claim_kind": "source_locator",
                        "claim_value": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "asserted_by_family": "synthetic_fixture",
                        "asserted_by_label": "Synthetic Fixture",
                        "evidence_kind": "recorded_fixture",
                        "evidence_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    },
                ],
                "matched_state": {
                    "id": "state.synthetic-demo-app.release",
                    "kind": "release",
                },
                "representations": [
                    {
                        "representation_id": "rep.synthetic-demo-app.source",
                        "representation_kind": "fixture_artifact",
                        "label": "Synthetic demo app fixture artifact",
                        "content_type": "application/vnd.eureka.synthetic.bundle",
                        "byte_length": 4096,
                        "filename": "synthetic-demo-app.bundle",
                        "source_family": "synthetic_fixture",
                        "source_label": "Synthetic Fixture",
                        "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "access_path_id": "access.synthetic-demo-app.fixture",
                        "access_kind": "inspect",
                        "access_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "is_direct": False,
                        "is_fetchable": True,
                    },
                    {
                        "representation_id": "rep.synthetic-demo-app.fixture-record",
                        "representation_kind": "fixture_record",
                        "label": "Synthetic demo app fixture record",
                        "content_type": "application/json",
                        "byte_length": 1024,
                        "source_family": "synthetic_fixture",
                        "source_label": "Synthetic Fixture",
                        "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "access_path_id": "access.synthetic-demo-app.fixture-record",
                        "access_kind": "view",
                        "access_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json#fixture:software/synthetic-demo-app@1.0.0",
                        "is_direct": False,
                        "is_fetchable": False,
                    },
                    {
                        "representation_id": "rep.synthetic-demo-app.package",
                        "representation_kind": "fixture_archive",
                        "label": "Synthetic demo app package archive",
                        "content_type": "application/zip",
                        "byte_length": 501,
                        "filename": "synthetic-demo-app-package.zip",
                        "source_family": "synthetic_fixture",
                        "source_label": "Synthetic Fixture",
                        "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "access_path_id": "access.synthetic-demo-app.package",
                        "access_kind": "download",
                        "access_locator": "contracts/archive/fixtures/software/payloads/synthetic-demo-app-package.zip",
                        "is_direct": True,
                        "is_fetchable": True,
                    }
                ],
                "source_fixture": {
                    "kind": "synthetic_fixture",
                    "locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                },
                "notices": [],
            },
        )

    def test_manifest_export_for_unknown_target_returns_none(self) -> None:
        manifest = self.service.export_manifest("fixture:software/missing-demo-app@0.0.1")

        self.assertIsNone(manifest)
