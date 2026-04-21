from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.snapshots import ResolutionBundleExportService
from runtime.gateway import build_demo_resolution_bundle_inspection_public_api
from runtime.gateway.public_api import InspectResolutionBundleRequest


class ResolutionBundleInspectionPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_resolution_bundle_inspection_public_api()
        source_records = SyntheticSoftwareConnector().load_source_records()
        normalized_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in source_records
        )
        self.export_service = ResolutionBundleExportService(NormalizedCatalog(normalized_records))

    def test_public_inspection_boundary_returns_success_envelope_for_valid_bundle(self) -> None:
        bundle_artifact = self.export_service.export_bundle("fixture:software/synthetic-demo-app@1.0.0")
        assert bundle_artifact is not None

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = Path(temp_dir) / bundle_artifact.filename
            bundle_path.write_bytes(bundle_artifact.payload)
            response = self.public_api.inspect_bundle(
                InspectResolutionBundleRequest.from_bundle_path(str(bundle_path))
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "inspected")
        self.assertEqual(
            response.body["resolved_resource_id"],
            "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
        )
        self.assertEqual(response.body["bundle"]["bundle_kind"], "eureka.resolution_bundle")
        self.assertEqual(response.body["bundle"]["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(response.body["primary_object"]["id"], "obj.synthetic-demo-app")

    def test_public_inspection_boundary_returns_structured_error_for_missing_path(self) -> None:
        response = self.public_api.inspect_bundle(
            InspectResolutionBundleRequest.from_bundle_path("D:/Projects/Eureka/eureka/does-not-exist.zip")
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["notices"][0]["code"], "bundle_path_not_found")
