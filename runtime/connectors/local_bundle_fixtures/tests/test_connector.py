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

        self.assertEqual(len(records), 5)
        self.assertEqual(records[0].target_ref, "local-bundle-fixture:windows-utility-bundle@1.0")
        self.assertEqual(records[1].target_ref, "local-bundle-fixture:driver-support-cd@1.0")
        self.assertIn(
            "local-bundle-fixture:windows-98-registry-repair-bundle@1.0",
            {record.target_ref for record in records},
        )
        self.assertIn(
            "local-bundle-fixture:windows-xp-browser-tools-bundle@1.0",
            {record.target_ref for record in records},
        )
        self.assertIn(
            "local-bundle-fixture:legacy-hardware-driver-support-bundle@1.0",
            {record.target_ref for record in records},
        )
        for record in records:
            locator = record.payload["bundle"]["payload_fixture"]["locator"]
            self.assertFalse(Path(locator).is_absolute())
            self.assertTrue(Path(locator).as_posix().startswith("runtime/connectors/local_bundle_fixtures/"))

    def test_zip_payloads_are_tiny_and_expose_expected_members(self) -> None:
        root = Path(__file__).resolve().parents[1] / "fixtures" / "payloads"
        payloads = {
            "windows_utility_bundle.zip": ("utilities/7z920.exe.txt",),
            "driver_support_cd.zip": ("drivers/wifi/thinkpad_t42/windows2000/driver.inf",),
            "windows_98_registry_repair_bundle.zip": (
                "utilities/registry-repair/registry-repair.exe.txt",
            ),
            "windows_xp_browser_tools_bundle.zip": (
                "browsers/firefox-xp-support/readme.txt",
            ),
            "legacy_hardware_driver_support_bundle.zip": (
                "drivers/sound/creative_ct1740/windows98/driver.inf",
                "drivers/network/3com_3c905/windows95/driver.inf",
            ),
        }

        for filename, expected_members in payloads.items():
            zip_path = root / filename
            self.assertLess(zip_path.stat().st_size, 4096)
            with ZipFile(zip_path, "r") as archive:
                names = set(archive.namelist())
            for expected_member in expected_members:
                self.assertIn(expected_member, names)

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

    def test_expanded_driver_bundle_preserves_creative_and_3com_member_hints(self) -> None:
        record = next(
            item
            for item in LocalBundleFixturesConnector().load_source_records()
            if item.target_ref == "local-bundle-fixture:legacy-hardware-driver-support-bundle@1.0"
        )
        normalized = normalize_local_bundle_record(extract_local_bundle_source_record(record))

        member_paths = {
            evidence.claim_value
            for evidence in normalized.evidence
            if evidence.claim_kind == "member_listing"
        }
        self.assertIn("drivers/sound/creative_ct1740/windows98/driver.inf", member_paths)
        self.assertIn("drivers/network/3com_3c905/windows95/driver.inf", member_paths)
        self.assertTrue(
            any("Windows 98" in evidence.claim_value for evidence in normalized.evidence)
        )
        self.assertTrue(
            any("Windows 95" in evidence.claim_value for evidence in normalized.evidence)
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
