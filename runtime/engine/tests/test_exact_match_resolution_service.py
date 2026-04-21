from __future__ import annotations

import unittest

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.public import ResolutionRequest
from runtime.engine.resolve import (
    ExactMatchResolutionService,
    normalized_record_to_object_summary,
    resolved_resource_id_for_record,
)


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


class ExactMatchResolutionServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.record = NormalizedResolutionRecord(
            target_ref=KNOWN_TARGET_REF,
            source_name="synthetic_software_fixture",
            source_locator="contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
            object_id="obj.synthetic-demo-app",
            object_kind="software",
            object_label="Synthetic Demo App",
            state_id="state.synthetic-demo-app.release",
            state_kind="release",
            representation_id="rep.synthetic-demo-app.source",
            representation_kind="source_archive",
            access_path_id="access.synthetic-demo-app.fixture",
            access_path_kind="fixture_path",
            access_path_locator="contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
        )
        self.catalog = NormalizedCatalog((self.record,))
        self.service = ExactMatchResolutionService(self.catalog)

    def test_exact_match_resolution_returns_completed_outcome(self) -> None:
        outcome = self.service.resolve(ResolutionRequest.from_parts(KNOWN_TARGET_REF))

        self.assertEqual(outcome.status, "completed")
        assert outcome.result is not None
        self.assertEqual(
            outcome.result.resolved_resource_id,
            resolved_resource_id_for_record(self.record),
        )
        self.assertEqual(
            outcome.result.primary_object.to_dict(),
            {
                "id": "obj.synthetic-demo-app",
                "kind": "software",
                "label": "Synthetic Demo App",
            },
        )
        self.assertEqual(outcome.notices, ())

    def test_missing_target_returns_blocked_notice(self) -> None:
        outcome = self.service.resolve(
            ResolutionRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(outcome.status, "blocked")
        self.assertIsNone(outcome.result)
        self.assertEqual(outcome.notices[0].code, "fixture_target_not_found")

    def test_normalized_record_maps_to_object_summary(self) -> None:
        summary = normalized_record_to_object_summary(self.record)

        self.assertEqual(
            summary.to_dict(),
            {
                "id": "obj.synthetic-demo-app",
                "kind": "software",
                "label": "Synthetic Demo App",
            },
        )
