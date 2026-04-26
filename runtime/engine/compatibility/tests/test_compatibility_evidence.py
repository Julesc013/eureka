from __future__ import annotations

from dataclasses import replace
import unittest

from runtime.gateway.public_api.demo_support import _build_demo_normalized_catalog
from runtime.engine.compatibility import (
    compatibility_evidence_verdict,
    extract_compatibility_evidence,
    normalize_platform,
)


class CompatibilityEvidenceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = _build_demo_normalized_catalog()

    def test_normalizes_old_platform_aliases(self) -> None:
        windows7 = normalize_platform("Windows NT 6.1")
        self.assertIsNotNone(windows7)
        assert windows7 is not None
        self.assertEqual(windows7.name, "Windows 7")
        self.assertEqual(windows7.version, "NT 6.1")

        windows2000 = normalize_platform("Win2k")
        self.assertIsNotNone(windows2000)
        assert windows2000 is not None
        self.assertEqual(windows2000.name, "Windows 2000")

        vista = normalize_platform("Windows NT 6.0")
        self.assertIsNotNone(vista)
        assert vista is not None
        self.assertEqual(vista.name, "Windows Vista")

    def test_thinkpad_driver_member_gets_windows2000_driver_evidence(self) -> None:
        record = self._record_by_member_path("drivers/wifi/thinkpad_t42/windows2000/driver.inf")

        self.assertTrue(record.compatibility_evidence)
        first = record.compatibility_evidence[0]
        self.assertEqual(first.source_id, "local-bundle-fixtures")
        self.assertEqual(first.source_family, "local_bundle_fixtures")
        self.assertEqual(first.claim_type, "driver_for_hardware")
        self.assertEqual(first.platform.name, "Windows 2000")
        self.assertIn(first.confidence, {"low", "medium"})

    def test_windows7_compatibility_note_gets_source_backed_evidence(self) -> None:
        record = self._record_by_member_path("compatibility/windows7.txt")

        evidence = record.compatibility_evidence
        self.assertTrue(evidence)
        self.assertEqual(evidence[0].platform.name, "Windows 7")
        self.assertEqual(evidence[0].evidence_kind, "compatibility_note")
        self.assertEqual(evidence[0].claim_type, "supports_platform")

    def test_unrelated_record_keeps_unknown_compatibility(self) -> None:
        record = self.catalog.find_by_target_ref("fixture:software/synthetic-demo-app@1.0.0")
        self.assertIsNotNone(record)
        assert record is not None

        self.assertEqual(extract_compatibility_evidence(record), ())
        verdict = compatibility_evidence_verdict(record)
        self.assertEqual(verdict.verdict, "unknown")
        self.assertIn("no_source_backed_compatibility_evidence", verdict.reasons)

    def test_no_false_incompatible_claim_from_fixture_limit_wording(self) -> None:
        record = self.catalog.find_by_target_ref("internet-archive-recorded:ia-firefox-xp-support-fixture")
        self.assertIsNotNone(record)
        assert record is not None

        claim_types = {item.claim_type for item in record.compatibility_evidence}
        self.assertNotIn("does_not_work_on", claim_types)
        self.assertIn("supports_platform", claim_types)

    def test_evidence_ids_are_stable_after_reextraction(self) -> None:
        record = self._record_by_member_path("drivers/wifi/thinkpad_t42/windows2000/readme.txt")
        reextracted = extract_compatibility_evidence(replace(record, compatibility_evidence=()))

        self.assertEqual(
            [item.evidence_id for item in record.compatibility_evidence],
            [item.evidence_id for item in reextracted],
        )

    def _record_by_member_path(self, member_path: str):
        for record in self.catalog.records:
            if record.member_path == member_path:
                return record
        self.fail(f"member_path not found: {member_path}")


if __name__ == "__main__":
    unittest.main()
