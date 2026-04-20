from __future__ import annotations

from io import BytesIO
import json
import unittest
import zipfile

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.snapshots import ResolutionBundleExportService


class ResolutionBundleExportServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        source_records = SyntheticSoftwareConnector().load_source_records()
        normalized_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in source_records
        )
        self.service = ResolutionBundleExportService(NormalizedCatalog(normalized_records))

    def test_bundle_export_for_known_target_is_deterministic(self) -> None:
        first = self.service.export_bundle("fixture:software/synthetic-demo-app@1.0.0")
        second = self.service.export_bundle("fixture:software/synthetic-demo-app@1.0.0")

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        assert first is not None
        assert second is not None
        self.assertEqual(first.filename, "eureka-resolution-bundle-fixture-software-synthetic-demo-app-1.0.0.zip")
        self.assertEqual(first.content_type, "application/zip")
        self.assertEqual(first.payload, second.payload)

        with zipfile.ZipFile(BytesIO(first.payload)) as bundle:
            self.assertEqual(
                bundle.namelist(),
                [
                    "README.txt",
                    "bundle.json",
                    "manifest.json",
                    "records/normalized_record.json",
                ],
            )

    def test_bundle_export_contains_expected_bounded_files(self) -> None:
        bundle_artifact = self.service.export_bundle("fixture:software/synthetic-demo-app@1.0.0")

        self.assertIsNotNone(bundle_artifact)
        assert bundle_artifact is not None

        with zipfile.ZipFile(BytesIO(bundle_artifact.payload)) as bundle:
            bundle_json = json.loads(bundle.read("bundle.json").decode("utf-8"))
            manifest_json = json.loads(bundle.read("manifest.json").decode("utf-8"))
            normalized_record_json = json.loads(bundle.read("records/normalized_record.json").decode("utf-8"))
            readme_text = bundle.read("README.txt").decode("utf-8")

        self.assertEqual(bundle_json["bundle_kind"], "eureka.resolution_bundle")
        self.assertEqual(bundle_json["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(manifest_json["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(manifest_json["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(normalized_record_json["record_kind"], "normalized_resolution_record")
        self.assertEqual(normalized_record_json["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
        self.assertIn("not a final snapshot, restore, or installer contract", readme_text)

    def test_bundle_export_for_unknown_target_returns_none(self) -> None:
        bundle_artifact = self.service.export_bundle("fixture:software/missing-demo-app@0.0.1")

        self.assertIsNone(bundle_artifact)
