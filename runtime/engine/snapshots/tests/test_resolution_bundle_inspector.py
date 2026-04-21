from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.interfaces.service import ResolutionBundleInspectionRequest
from runtime.engine.resolve import resolved_resource_id_for_record
from runtime.engine.snapshots import ResolutionBundleExportService, ResolutionBundleInspectionEngineService


class ResolutionBundleInspectionEngineServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        source_records = SyntheticSoftwareConnector().load_source_records()
        self.normalized_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in source_records
        )
        catalog = NormalizedCatalog(self.normalized_records)
        self.export_service = ResolutionBundleExportService(catalog)
        self.inspection_service = ResolutionBundleInspectionEngineService()

    def test_bundle_inspection_succeeds_for_valid_deterministic_bundle(self) -> None:
        bundle_artifact = self.export_service.export_bundle("fixture:software/synthetic-demo-app@1.0.0")
        assert bundle_artifact is not None

        result = self.inspection_service.inspect_bundle(
            ResolutionBundleInspectionRequest.from_bundle_bytes(
                bundle_artifact.payload,
                source_name=bundle_artifact.filename,
            )
        )

        self.assertEqual(result.status, "inspected")
        self.assertTrue(result.inspected_offline)
        self.assertEqual(result.bundle_kind, "eureka.resolution_bundle")
        self.assertEqual(result.target_ref, "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(
            result.resolved_resource_id,
            resolved_resource_id_for_record(self.normalized_records[0]),
        )
        self.assertEqual(
            result.member_list,
            (
                "README.txt",
                "bundle.json",
                "manifest.json",
                "records/normalized_record.json",
            ),
        )
        self.assertEqual(result.primary_object.id, "obj.synthetic-demo-app")
        self.assertEqual(result.notices[0].code, "bundle_inspected_locally_offline")

    def test_bundle_inspection_fails_cleanly_for_malformed_zip(self) -> None:
        result = self.inspection_service.inspect_bundle(
            ResolutionBundleInspectionRequest.from_bundle_bytes(
                b"not-a-zip",
                source_name="bad-bundle.zip",
            )
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.notices[0].code, "bundle_archive_invalid")

    def test_bundle_inspection_fails_cleanly_for_missing_expected_members(self) -> None:
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, mode="w") as bundle:
            bundle.writestr("bundle.json", json.dumps({"bundle_kind": "eureka.resolution_bundle"}))

        result = self.inspection_service.inspect_bundle(
            ResolutionBundleInspectionRequest.from_bundle_bytes(
                buffer.getvalue(),
                source_name="missing-members.zip",
            )
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.notices[0].code, "bundle_member_missing")

    def test_bundle_inspection_reads_local_bundle_path_without_live_fixture_access(self) -> None:
        bundle_artifact = self.export_service.export_bundle("fixture:software/synthetic-demo-app@1.0.0")
        assert bundle_artifact is not None

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = Path(temp_dir) / bundle_artifact.filename
            bundle_path.write_bytes(bundle_artifact.payload)
            result = self.inspection_service.inspect_bundle(
                ResolutionBundleInspectionRequest.from_bundle_path(str(bundle_path))
            )

        self.assertEqual(result.status, "inspected")
        self.assertEqual(result.source_kind, "local_path")
        self.assertEqual(result.target_ref, "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(
            result.resolved_resource_id,
            resolved_resource_id_for_record(self.normalized_records[0]),
        )
