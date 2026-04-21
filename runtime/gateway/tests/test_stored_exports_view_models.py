from __future__ import annotations

import tempfile
import unittest

from runtime.gateway import build_demo_stored_exports_public_api
from runtime.gateway.public_api import (
    StoredExportsTargetRequest,
    stored_exports_envelope_to_view_model,
)


class StoredExportsViewModelsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.public_api = build_demo_stored_exports_public_api(self.temp_dir.name)

    def test_shared_stored_exports_view_model_maps_non_empty_artifact_list(self) -> None:
        self.public_api.store_resolution_manifest(
            StoredExportsTargetRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )
        envelope = self.public_api.list_stored_exports(
            StoredExportsTargetRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        ).body

        view_model = stored_exports_envelope_to_view_model(envelope)

        self.assertEqual(view_model["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(
            view_model["resolved_resource_id"],
            "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
        )
        self.assertEqual(len(view_model["store_actions"]), 2)
        self.assertEqual(len(view_model["artifacts"]), 1)
        self.assertEqual(view_model["artifacts"][0]["artifact_kind"], "resolution_manifest")
        self.assertEqual(
            view_model["artifacts"][0]["resolved_resource_id"],
            "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
        )

    def test_shared_stored_exports_view_model_maps_empty_or_blocked_result(self) -> None:
        envelope = self.public_api.list_stored_exports(
            StoredExportsTargetRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        ).body

        view_model = stored_exports_envelope_to_view_model(envelope)

        self.assertEqual(view_model["target_ref"], "fixture:software/missing-demo-app@0.0.1")
        self.assertEqual(view_model["artifacts"], [])
        self.assertEqual(
            [notice["code"] for notice in view_model["notices"]],
            [
                "stored_exports_target_not_available",
                "store_resolution_manifest_not_available",
                "store_resolution_bundle_not_available",
            ],
        )
