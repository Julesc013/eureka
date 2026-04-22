from __future__ import annotations

import unittest

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.public import ResolutionRequest
from runtime.engine.provenance import EvidenceSummary
from runtime.engine.representations import RepresentationSummary
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
            representations=(
                RepresentationSummary(
                    representation_id="rep.synthetic-demo-app.source",
                    representation_kind="fixture_artifact",
                    label="Synthetic demo app fixture artifact",
                    content_type="application/vnd.eureka.synthetic.bundle",
                    byte_length=4096,
                    source_family="synthetic_fixture",
                    source_label="Synthetic Fixture",
                    source_locator="contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    access_path_id="access.synthetic-demo-app.fixture",
                    access_kind="inspect",
                    access_locator="contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    is_direct=False,
                ),
                RepresentationSummary(
                    representation_id="rep.synthetic-demo-app.fixture-record",
                    representation_kind="fixture_record",
                    label="Synthetic demo app fixture record",
                    content_type="application/json",
                    byte_length=1024,
                    source_family="synthetic_fixture",
                    source_label="Synthetic Fixture",
                    source_locator="contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    access_path_id="access.synthetic-demo-app.fixture-record",
                    access_kind="view",
                    access_locator="contracts/archive/fixtures/software/synthetic_resolution_fixture.json#fixture:software/synthetic-demo-app@1.0.0",
                    is_direct=False,
                ),
            ),
            evidence=(
                EvidenceSummary(
                    claim_kind="label",
                    claim_value="Synthetic Demo App",
                    asserted_by_family="synthetic_fixture",
                    asserted_by_label="Synthetic Fixture",
                    evidence_kind="recorded_fixture",
                    evidence_locator="contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                ),
            ),
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
        self.assertEqual(outcome.result.evidence[0].claim_kind, "label")
        self.assertEqual(outcome.result.evidence[0].claim_value, "Synthetic Demo App")
        self.assertEqual(len(outcome.result.representations), 2)
        self.assertEqual(outcome.result.representations[0].representation_kind, "fixture_artifact")
        self.assertEqual(outcome.result.representations[1].access_kind, "view")
        self.assertEqual(outcome.notices, ())

    def test_missing_target_returns_blocked_notice(self) -> None:
        outcome = self.service.resolve(
            ResolutionRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(outcome.status, "blocked")
        self.assertIsNone(outcome.result)
        self.assertEqual(outcome.notices[0].code, "target_ref_not_found")

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
