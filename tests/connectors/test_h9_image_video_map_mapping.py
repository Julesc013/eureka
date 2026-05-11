from __future__ import annotations

from pathlib import Path
import unittest

from runtime.connectors.h9_media_metadata.fixture_loader import load_h9_media_metadata_fixture
from runtime.connectors.h9_media_metadata.image_video_map_identity import build_h9_image_video_map_identity_candidate
from runtime.connectors.h9_media_metadata.normalizer_common import detect_h9_truth_boundary_violations, normalize_h9_media_metadata_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


class H9ImageVideoMapMappingTests(unittest.TestCase):
    def test_visual_map_candidate_is_not_object_or_geospatial_truth(self) -> None:
        fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures/david_rumsey_maps/image_video_map_record.json")
        normalized = normalize_h9_media_metadata_fixture(fixture, "david_rumsey_maps")
        candidate = build_h9_image_video_map_identity_candidate(normalized)
        self.assertFalse(candidate["truth_boundary"]["image_video_map_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["rights_license_candidate_is_rights_truth"])
        self.assertFalse(detect_h9_truth_boundary_violations(candidate))


if __name__ == "__main__":
    unittest.main()
