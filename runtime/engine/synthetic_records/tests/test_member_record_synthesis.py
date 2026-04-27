from __future__ import annotations

import re
import unittest

from runtime.connectors.local_bundle_fixtures import LocalBundleFixturesConnector
from runtime.engine.interfaces.extract import extract_local_bundle_source_record
from runtime.engine.interfaces.normalize import normalize_local_bundle_record
from runtime.engine.synthetic_records import (
    synthesize_member_normalized_records,
    synthesize_member_records,
    synthetic_member_target_ref,
)


def _local_bundle_records():
    return tuple(
        normalize_local_bundle_record(extract_local_bundle_source_record(record))
        for record in LocalBundleFixturesConnector().load_source_records()
    )


class SyntheticMemberRecordSynthesisTestCase(unittest.TestCase):
    def test_target_refs_are_deterministic_safe_and_path_free(self) -> None:
        target_ref = synthetic_member_target_ref(
            "local-bundle-fixture:driver-support-cd@1.0",
            "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
        )

        self.assertEqual(
            target_ref,
            synthetic_member_target_ref(
                "local-bundle-fixture:driver-support-cd@1.0",
                "drivers\\wifi\\thinkpad_t42\\windows2000\\driver.inf",
            ),
        )
        self.assertRegex(target_ref, r"^member:sha256:[a-f0-9]{64}$")
        self.assertNotIn("drivers/", target_ref)
        self.assertNotIn("\\", target_ref)

    def test_synthesis_preserves_member_path_parent_lineage_source_and_evidence(self) -> None:
        members = synthesize_member_records(_local_bundle_records())
        driver = next(
            member
            for member in members
            if member.member_path == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )

        self.assertEqual(driver.parent_target_ref, "local-bundle-fixture:driver-support-cd@1.0")
        self.assertEqual(driver.parent_representation_id, "rep.local-bundle.driver-support-cd.zip")
        self.assertEqual(driver.source_id, "local-bundle-fixtures")
        self.assertEqual(driver.source_family, "local_bundle_fixtures")
        self.assertEqual(driver.member_label, "driver.inf")
        self.assertEqual(driver.member_kind, "driver")
        self.assertEqual(driver.media_type, "text/plain")
        self.assertIsNotNone(driver.size_bytes)
        self.assertRegex(driver.content_hash or "", r"^sha256:[a-f0-9]{64}$")
        self.assertEqual(driver.parent_lineage["member_path"], driver.member_path)
        self.assertIn("read_member", driver.action_hints)
        self.assertTrue(any(item.claim_kind == "member_text" for item in driver.evidence))

    def test_normalized_records_are_first_class_synthetic_members(self) -> None:
        records = synthesize_member_normalized_records(_local_bundle_records())
        refs = [record.target_ref for record in records]

        self.assertEqual(len(refs), len(set(refs)))
        self.assertTrue(all(record.record_kind == "synthetic_member" for record in records))
        self.assertTrue(all(record.parent_target_ref for record in records))
        self.assertTrue(all(record.member_path for record in records))
        self.assertTrue(all(record.parent_representation_id for record in records))
        self.assertTrue(all(re.match(r"^member:sha256:[a-f0-9]{64}$", record.target_ref) for record in records))
        self.assertTrue(
            any(record.member_path == "utilities/7z920.exe.txt" for record in records)
        )
        self.assertTrue(
            any(record.member_path == "utilities/ftp-blue-client/readme.txt" for record in records)
        )
        self.assertTrue(
            any(
                record.member_path == "utilities/registry-repair/registry-repair.exe.txt"
                for record in records
            )
        )
        self.assertTrue(
            any(
                record.member_path == "browsers/firefox-xp-support/readme.txt"
                for record in records
            )
        )
        self.assertTrue(
            any(
                record.member_path == "drivers/sound/creative_ct1740/windows98/driver.inf"
                for record in records
            )
        )
        self.assertTrue(
            any(
                record.member_path == "drivers/network/3com_3c905/windows95/driver.inf"
                for record in records
            )
        )

    def test_expanded_fixture_synthesis_adds_expected_old_platform_members(self) -> None:
        members = synthesize_member_records(_local_bundle_records())
        by_path = {member.member_path: member for member in members}

        registry_repair = by_path["utilities/registry-repair/registry-repair.exe.txt"]
        self.assertEqual(
            registry_repair.parent_target_ref,
            "local-bundle-fixture:windows-98-registry-repair-bundle@1.0",
        )
        self.assertEqual(registry_repair.member_kind, "utility")
        self.assertIn("read_member", registry_repair.action_hints)

        creative_driver = by_path["drivers/sound/creative_ct1740/windows98/driver.inf"]
        self.assertEqual(
            creative_driver.parent_target_ref,
            "local-bundle-fixture:legacy-hardware-driver-support-bundle@1.0",
        )
        self.assertEqual(creative_driver.member_kind, "driver")
        self.assertRegex(creative_driver.content_hash or "", r"^sha256:[a-f0-9]{64}$")


if __name__ == "__main__":
    unittest.main()
