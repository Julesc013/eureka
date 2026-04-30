from __future__ import annotations

import unittest

from runtime.connectors.source_expansion_recorded import SourceExpansionRecordedConnector
from runtime.engine.interfaces.extract import extract_source_expansion_recorded_source_record
from runtime.engine.interfaces.normalize import normalize_source_expansion_recorded_record


EXPECTED_FAMILIES = {
    "manual_document_recorded",
    "package_registry_recorded",
    "review_description_recorded",
    "software_heritage_recorded",
    "sourceforge_recorded",
    "wayback_memento_recorded",
}


class SourceExpansionRecordedConnectorTestCase(unittest.TestCase):
    def test_fixture_records_load_as_recorded_fixture_sources(self) -> None:
        records = SourceExpansionRecordedConnector().load_source_records()

        self.assertEqual(len(records), 15)
        self.assertEqual({record.payload["source_family"] for record in records}, EXPECTED_FAMILIES)
        for record in records:
            with self.subTest(target_ref=record.target_ref):
                self.assertIn("source_expansion_v2_fixture.json", record.source_locator)
                self.assertNotIn("http://", record.source_locator)
                self.assertNotIn("https://", record.source_locator)
                self.assertTrue(record.target_ref)
                self.assertEqual(record.payload["target_ref"], record.target_ref)

    def test_fixture_records_normalize_with_public_safe_evidence(self) -> None:
        normalized = tuple(
            normalize_source_expansion_recorded_record(
                extract_source_expansion_recorded_source_record(record)
            )
            for record in SourceExpansionRecordedConnector().load_source_records()
        )

        self.assertEqual({record.source_family for record in normalized}, EXPECTED_FAMILIES)
        firefox = next(
            record
            for record in normalized
            if record.target_ref == "wayback-memento-recorded:archived-firefox-xp-release-notes"
        )
        self.assertEqual(firefox.source_family, "wayback_memento_recorded")
        self.assertTrue(firefox.evidence)
        self.assertTrue(firefox.compatibility_evidence)
        self.assertFalse(firefox.representations[0].is_fetchable)
        self.assertIn("cite_fixture", firefox.action_hints)

        visual_cpp = next(
            record
            for record in normalized
            if record.target_ref == "package-registry-recorded:visual-cpp-6-service-pack-fixture"
        )
        self.assertEqual(visual_cpp.record_kind, "synthetic_member")
        self.assertEqual(visual_cpp.member_path, "vc6sp/README-SP.txt")
        self.assertEqual(visual_cpp.parent_target_ref, "package-registry-recorded:visual-cpp-6-service-pack-container")


if __name__ == "__main__":
    unittest.main()
