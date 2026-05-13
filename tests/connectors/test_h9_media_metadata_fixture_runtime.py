from __future__ import annotations

import importlib
from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h9_media_metadata.fixture_loader import load_h9_media_metadata_fixture
from control.prototypes.legacy_runtime.connectors.h9_media_metadata.normalizer_common import (
    H9_FIXTURE_KINDS,
    H9_SOURCE_IDS,
    build_h9_fixture_replay_result,
    detect_h9_product_boundary_violations,
    detect_h9_truth_boundary_violations,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class H9MediaMetadataFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_all_fixture_kinds(self) -> None:
        for source_id in H9_SOURCE_IDS:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h9_media_metadata.{source_id}")
            for kind in H9_FIXTURE_KINDS:
                filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
                fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures" / source_id / filename)
                normalized = module.normalize(fixture)
                self.assertEqual(normalized["source_id"], source_id)
                self.assertFalse(detect_h9_truth_boundary_violations(normalized))
                self.assertFalse(detect_h9_product_boundary_violations(normalized))

    def test_missing_optional_fields_produce_limitations_not_fabricated_data(self) -> None:
        fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures/musicbrainz/minimal_record.json")
        normalized = importlib.import_module("control.prototypes.legacy_runtime.connectors.h9_media_metadata.musicbrainz").normalize(fixture)
        self.assertEqual(normalized["rights_or_license_metadata"], {})
        self.assertTrue(any("optional field" in item for item in normalized["source_limitations"]))

    def test_replay_result_preserves_no_live_boundaries(self) -> None:
        fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures/musicbrainz/media_identity_record.json")
        normalized = importlib.import_module("control.prototypes.legacy_runtime.connectors.h9_media_metadata.musicbrainz").normalize(fixture)
        replay = build_h9_fixture_replay_result(fixture, normalized)
        self.assertTrue(replay["no_network_used"])
        self.assertTrue(replay["no_download_upload_fingerprint_used"])
        self.assertTrue(replay["no_truth_acceptance"])

    def test_public_and_master_index_claims_are_rejected(self) -> None:
        fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures/musicbrainz/media_identity_record.json")
        normalized = importlib.import_module("control.prototypes.legacy_runtime.connectors.h9_media_metadata.musicbrainz").normalize(fixture)
        normalized["truth_boundary"]["public_index_mutated"] = True
        self.assertTrue(detect_h9_truth_boundary_violations(normalized))
        normalized["truth_boundary"]["public_index_mutated"] = False
        normalized["product_boundary"]["mutated_master_index"] = True
        self.assertTrue(detect_h9_product_boundary_violations(normalized))


if __name__ == "__main__":
    unittest.main()
