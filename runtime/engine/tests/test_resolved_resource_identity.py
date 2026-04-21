from __future__ import annotations

import unittest

from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.resolve import resolved_resource_id_for_record


class ResolvedResourceIdentityTestCase(unittest.TestCase):
    def test_resolved_resource_identity_is_stable_for_same_normalized_record(self) -> None:
        record = NormalizedResolutionRecord(
            target_ref="fixture:software/synthetic-demo-app@1.0.0",
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

        first = resolved_resource_id_for_record(record)
        second = resolved_resource_id_for_record(record)

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("resolved:sha256:"))
