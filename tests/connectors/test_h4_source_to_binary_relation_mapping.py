import copy
from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import (
    build_h4_release_asset_candidates,
    build_h4_source_to_binary_relation_candidates,
    detect_h4_truth_boundary_violations,
)
from control.prototypes.legacy_runtime.connectors.h4_code_source_release.github_releases import normalize
from control.prototypes.legacy_runtime.connectors.h4_code_source_release.fixture_loader import load_h4_code_source_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


class H4SourceToBinaryRelationMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = load_h4_code_source_fixture(REPO_ROOT / "examples/connectors/h4_code_source_release/fixtures/github_releases/source_to_binary_record.json")
        cls.normalized = normalize(fixture)

    def test_relation_candidate_not_provenance(self):
        candidate = build_h4_source_to_binary_relation_candidates(self.normalized)[0]
        self.assertFalse(candidate["truth_boundary"]["relation_candidate_is_accepted_provenance"])
        self.assertFalse(candidate["truth_boundary"]["tag_release_match_proves_build_relation"])
        self.assertFalse(candidate["truth_boundary"]["asset_presence_proves_source_relationship"])
        self.assertFalse(candidate["truth_boundary"]["sbom_signature_metadata_proves_trust"])

    def test_release_asset_candidate_not_download_or_safety(self):
        assets = self.normalized["release_asset_candidate_preview"]
        self.assertTrue(assets)
        candidate = assets[0]
        self.assertFalse(candidate["download_allowed_current"])
        self.assertFalse(candidate["payload_available_current"])
        self.assertFalse(candidate["truth_boundary"]["asset_hash_proves_malware_safety"])
        self.assertFalse(candidate["truth_boundary"]["signature_metadata_proves_authenticity"])
        self.assertFalse(candidate["truth_boundary"]["sbom_metadata_is_provenance"])

    def test_relation_truth_claim_rejected(self):
        candidate = copy.deepcopy(build_h4_source_to_binary_relation_candidates(self.normalized)[0])
        candidate["truth_boundary"]["relation_candidate_is_accepted_provenance"] = True
        self.assertTrue(detect_h4_truth_boundary_violations(candidate))

    def test_asset_safety_claim_rejected(self):
        asset = copy.deepcopy(self.normalized["release_asset_candidate_preview"][0])
        asset["truth_boundary"]["asset_hash_proves_malware_safety"] = True
        self.assertTrue(detect_h4_truth_boundary_violations(asset))


if __name__ == "__main__":
    unittest.main()
