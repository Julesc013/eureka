from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.fixture_loader import load_h9_media_metadata_fixture
from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.media_object_identity import build_h9_media_object_identity_candidate
from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.normalizer_common import detect_h9_truth_boundary_violations, normalize_h9_media_metadata_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


class H9MediaObjectIdentityMappingTests(unittest.TestCase):
    def test_media_object_identity_candidate_is_not_truth(self) -> None:
        fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures/wikimedia_commons/media_identity_record.json")
        normalized = normalize_h9_media_metadata_fixture(fixture, "wikimedia_commons")
        candidate = build_h9_media_object_identity_candidate(normalized)
        self.assertFalse(candidate["truth_boundary"]["media_object_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["media_metadata_grants_download_permission"])
        self.assertFalse(detect_h9_truth_boundary_violations(candidate))


if __name__ == "__main__":
    unittest.main()
