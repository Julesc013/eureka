from __future__ import annotations

import unittest

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.actions import ResolutionManifestExportService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record


class ResolutionManifestExportServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        source_records = SyntheticSoftwareConnector().load_source_records()
        normalized_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in source_records
        )
        self.service = ResolutionManifestExportService(NormalizedCatalog(normalized_records))

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
                "primary_object": {
                    "id": "obj.synthetic-demo-app",
                    "kind": "software",
                    "label": "Synthetic Demo App",
                },
                "matched_state": {
                    "id": "state.synthetic-demo-app.release",
                    "kind": "release",
                },
                "representations": [
                    {
                        "id": "rep.synthetic-demo-app.source",
                        "kind": "source_archive",
                        "access_path": {
                            "id": "access.synthetic-demo-app.fixture",
                            "kind": "fixture_path",
                            "locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        },
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
