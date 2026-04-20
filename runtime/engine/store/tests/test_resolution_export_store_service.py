from __future__ import annotations

import json
from io import BytesIO
import tempfile
import unittest
import zipfile

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.actions import ResolutionManifestExportService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.snapshots import ResolutionBundleExportService
from runtime.engine.store import LocalExportStore, ResolutionExportStoreEngineService


class ResolutionExportStoreEngineServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        connector = SyntheticSoftwareConnector()
        records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in connector.load_source_records()
        )
        catalog = NormalizedCatalog(records)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.service = ResolutionExportStoreEngineService(
            manifest_service=ResolutionManifestExportService(catalog),
            bundle_service=ResolutionBundleExportService(catalog),
            store=LocalExportStore(self.temp_dir.name),
        )

    def test_manifest_store_operation_for_known_target_returns_stable_artifact_metadata(self) -> None:
        first = self.service.store_manifest("fixture:software/synthetic-demo-app@1.0.0")
        second = self.service.store_manifest("fixture:software/synthetic-demo-app@1.0.0")

        self.assertEqual(first.status, "stored")
        self.assertIsNotNone(first.artifact)
        assert first.artifact is not None
        self.assertEqual(first.artifact.artifact_kind, "resolution_manifest")
        self.assertEqual(first.artifact.content_type, "application/json; charset=utf-8")
        self.assertEqual(first.artifact.artifact_id, second.artifact.artifact_id if second.artifact else None)

    def test_bundle_store_operation_for_known_target_returns_stable_artifact_metadata_and_zip_bytes(self) -> None:
        result = self.service.store_bundle("fixture:software/synthetic-demo-app@1.0.0")
        assert result.artifact is not None

        content = self.service.get_artifact_content(result.artifact.artifact_id)
        self.assertEqual(result.status, "stored")
        self.assertEqual(result.artifact.artifact_kind, "resolution_bundle")
        self.assertEqual(content.status, "available")
        self.assertEqual(content.artifact, result.artifact)
        assert content.payload is not None
        with zipfile.ZipFile(BytesIO(content.payload)) as bundle:
            self.assertEqual(
                bundle.namelist(),
                [
                    "README.txt",
                    "bundle.json",
                    "manifest.json",
                    "records/normalized_record.json",
                ],
            )

    def test_listing_stored_exports_for_target_returns_expected_summaries(self) -> None:
        manifest_result = self.service.store_manifest("fixture:software/synthetic-demo-app@1.0.0")
        bundle_result = self.service.store_bundle("fixture:software/synthetic-demo-app@1.0.0")
        assert manifest_result.artifact is not None
        assert bundle_result.artifact is not None

        listed = self.service.list_artifacts("fixture:software/synthetic-demo-app@1.0.0")

        self.assertEqual(listed.status, "available")
        self.assertEqual(
            [artifact.artifact_kind for artifact in listed.artifacts],
            ["resolution_bundle", "resolution_manifest"],
        )
        self.assertEqual(
            {artifact.artifact_id for artifact in listed.artifacts},
            {manifest_result.artifact.artifact_id, bundle_result.artifact.artifact_id},
        )

    def test_fetching_stored_artifact_bytes_by_artifact_id_returns_expected_manifest_content(self) -> None:
        result = self.service.store_manifest("fixture:software/synthetic-demo-app@1.0.0")
        assert result.artifact is not None

        content = self.service.get_artifact_content(result.artifact.artifact_id)

        self.assertEqual(content.status, "available")
        assert content.payload is not None
        manifest = json.loads(content.payload.decode("utf-8"))
        self.assertEqual(manifest["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(manifest["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")

