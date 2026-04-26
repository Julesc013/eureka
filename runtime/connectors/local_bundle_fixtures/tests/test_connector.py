from __future__ import annotations

from pathlib import Path
import unittest
from zipfile import ZipFile

from runtime.connectors.local_bundle_fixtures import LocalBundleFixturesConnector
from runtime.engine.acquisition.service import DeterministicAcquisitionService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.decomposition.service import DeterministicDecompositionService
from runtime.engine.interfaces.extract import extract_local_bundle_source_record
from runtime.engine.interfaces.normalize import normalize_local_bundle_record
from runtime.engine.interfaces.public import DecompositionRequest, MemberAccessRequest
from runtime.engine.members.service import DeterministicMemberAccessService


class LocalBundleFixturesConnectorTestCase(unittest.TestCase):
    def test_fixture_manifest_loads_bundles_and_repo_relative_payloads(self) -> None:
        records = LocalBundleFixturesConnector().load_source_records()

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].target_ref, "local-bundle-fixture:windows-utility-bundle@1.0")
        self.assertEqual(records[1].target_ref, "local-bundle-fixture:driver-support-cd@1.0")
        for record in records:
            locator = record.payload["bundle"]["payload_fixture"]["locator"]
            self.assertFalse(Path(locator).is_absolute())
            self.assertTrue(Path(locator).as_posix().startswith("runtime/connectors/local_bundle_fixtures/"))

    def test_zip_payloads_are_tiny_and_expose_expected_members(self) -> None:
        root = Path(__file__).resolve().parents[1] / "fixtures" / "payloads"
        windows_zip = root / "windows_utility_bundle.zip"
        driver_zip = root / "driver_support_cd.zip"

        self.assertLess(windows_zip.stat().st_size, 4096)
        self.assertLess(driver_zip.stat().st_size, 4096)
        with ZipFile(driver_zip, "r") as archive:
            self.assertIn(
                "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
                archive.namelist(),
            )
        with ZipFile(windows_zip, "r") as archive:
            self.assertIn("utilities/7z920.exe.txt", archive.namelist())

    def test_normalized_bundle_preserves_source_parent_and_member_hints(self) -> None:
        record = next(
            item
            for item in LocalBundleFixturesConnector().load_source_records()
            if item.target_ref == "local-bundle-fixture:driver-support-cd@1.0"
        )
        normalized = normalize_local_bundle_record(extract_local_bundle_source_record(record))

        self.assertEqual(normalized.source_family, "local_bundle_fixtures")
        self.assertEqual(normalized.source_family_label, "Local Bundle Fixtures")
        self.assertEqual(normalized.representations[0].representation_kind, "fixture_archive")
        self.assertTrue(normalized.representations[0].is_fetchable)
        self.assertTrue(
            any(
                evidence.claim_kind == "member_listing"
                and evidence.claim_value == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
                for evidence in normalized.evidence
            )
        )

    def test_existing_decomposition_and_member_access_can_use_committed_zip_fixture(self) -> None:
        records = tuple(
            normalize_local_bundle_record(extract_local_bundle_source_record(record))
            for record in LocalBundleFixturesConnector().load_source_records()
        )
        catalog = NormalizedCatalog(records)
        acquisition_service = DeterministicAcquisitionService(catalog)
        decomposition_service = DeterministicDecompositionService(acquisition_service)
        member_service = DeterministicMemberAccessService(acquisition_service, decomposition_service)

        decomposition = decomposition_service.decompose_representation(
            DecompositionRequest.from_parts(
                "local-bundle-fixture:driver-support-cd@1.0",
                "rep.local-bundle.driver-support-cd.zip",
            )
        )
        self.assertEqual(decomposition.decomposition_status, "decomposed")
        self.assertIn(
            "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
            [member.member_path for member in decomposition.members],
        )

        member = member_service.read_member(
            MemberAccessRequest.from_parts(
                "local-bundle-fixture:driver-support-cd@1.0",
                "rep.local-bundle.driver-support-cd.zip",
                "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
            )
        )
        self.assertEqual(member.member_access_status, "read")
        self.assertEqual(member.reason_codes, ("member_readback_succeeded",))
        self.assertIn(b"Windows 2000", member.payload or b"")


if __name__ == "__main__":
    unittest.main()
