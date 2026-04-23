from __future__ import annotations

import unittest

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record


class BoundaryTransformTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.source_record = SyntheticSoftwareConnector().load_source_records()[0]

    def test_extract_step_exposes_bounded_fixture_sections(self) -> None:
        extracted = extract_synthetic_source_record(self.source_record)

        self.assertEqual(extracted.target_ref, "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(extracted.object_record["id"], "obj.synthetic-demo-app")
        self.assertEqual(extracted.state_record["kind"], "release")
        self.assertEqual(extracted.representation_record["kind"], "fixture_artifact")
        self.assertEqual(extracted.access_path_record["kind"], "inspect")
        self.assertEqual(len(extracted.representation_records), 3)
        self.assertEqual(extracted.representation_records[1]["kind"], "fixture_record")
        self.assertEqual(extracted.representation_records[2]["kind"], "fixture_archive")

    def test_normalize_step_emits_engine_consumable_record(self) -> None:
        extracted = extract_synthetic_source_record(self.source_record)
        normalized = normalize_extracted_record(extracted)

        self.assertEqual(normalized.target_ref, "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(normalized.object_id, "obj.synthetic-demo-app")
        self.assertEqual(normalized.object_kind, "software")
        self.assertEqual(normalized.object_label, "Synthetic Demo App")
        self.assertEqual(normalized.state_kind, "release")
        self.assertEqual(normalized.representation_kind, "fixture_artifact")
        self.assertEqual(len(normalized.representations), 3)
        self.assertEqual(normalized.representations[1].representation_kind, "fixture_record")
        self.assertEqual(normalized.representations[2].representation_kind, "fixture_archive")
        self.assertEqual(
            normalized.access_path_locator,
            "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
        )
