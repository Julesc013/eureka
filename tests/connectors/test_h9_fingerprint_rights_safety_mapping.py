from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h9_media_metadata.fixture_loader import load_h9_media_metadata_fixture
from control.prototypes.legacy_runtime.connectors.h9_media_metadata.normalizer_common import normalize_h9_media_metadata_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


class H9FingerprintRightsSafetyMappingTests(unittest.TestCase):
    def test_fingerprint_rights_safety_candidates_do_not_overclaim(self) -> None:
        fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures/acoustid_policy_limited/fingerprint_metadata_record.json")
        normalized = normalize_h9_media_metadata_fixture(fixture, "acoustid_policy_limited")
        fingerprint = normalized["media_fingerprint_candidate"]
        rights = normalized["media_rights_license_candidate"]
        safety = normalized["media_safety_privacy_candidate"]
        self.assertFalse(fingerprint["truth_boundary"]["fingerprint_match_candidate_is_truth"])
        self.assertFalse(fingerprint["truth_boundary"]["fingerprint_candidate_grants_upload_or_submission_permission"])
        self.assertFalse(rights["truth_boundary"]["license_metadata_is_rights_clearance"])
        self.assertFalse(rights["truth_boundary"]["public_domain_metadata_is_public_domain_truth"])
        self.assertFalse(rights["truth_boundary"]["creative_commons_metadata_is_license_truth"])
        self.assertFalse(safety["truth_boundary"]["safety_privacy_candidate_is_safety_truth"])
        self.assertFalse(safety["truth_boundary"]["content_safety_claimed"])
        self.assertFalse(safety["truth_boundary"]["privacy_safety_claimed"])

    def test_source_cache_and_evidence_previews_are_not_acceptance(self) -> None:
        fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures/musicbrainz/rights_license_record.json")
        normalized = normalize_h9_media_metadata_fixture(fixture, "musicbrainz")
        self.assertFalse(normalized["source_cache_candidate_preview"]["accepted_source"])
        self.assertFalse(normalized["evidence_candidate_preview"]["accepted_evidence"])


if __name__ == "__main__":
    unittest.main()
