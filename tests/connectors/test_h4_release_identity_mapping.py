import copy
from pathlib import Path
import unittest

from runtime.connectors.h4_code_source_release.normalizer_common import (
    build_h4_release_identity_candidate,
    detect_h4_truth_boundary_violations,
)
from runtime.connectors.h4_code_source_release.github_releases import normalize
from runtime.connectors.h4_code_source_release.fixture_loader import load_h4_code_source_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


class H4ReleaseIdentityMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = load_h4_code_source_fixture(REPO_ROOT / "examples/connectors/h4_code_source_release/fixtures/github_releases/release_record.json")
        cls.normalized = normalize(fixture)

    def test_release_identity_candidate_not_release_truth(self):
        candidate = build_h4_release_identity_candidate(self.normalized)
        self.assertFalse(candidate["truth_boundary"]["release_identity_candidate_is_accepted_release_truth"])
        self.assertFalse(candidate["truth_boundary"]["release_asset_metadata_grants_download_permission"])

    def test_release_notes_do_not_prove_installability(self):
        candidate = build_h4_release_identity_candidate(self.normalized)
        self.assertFalse(candidate["truth_boundary"]["release_notes_prove_installability"])

    def test_release_truth_claim_rejected(self):
        candidate = copy.deepcopy(build_h4_release_identity_candidate(self.normalized))
        candidate["truth_boundary"]["release_identity_candidate_is_accepted_release_truth"] = True
        self.assertTrue(detect_h4_truth_boundary_violations(candidate))

    def test_signature_authenticity_claim_rejected(self):
        candidate = copy.deepcopy(build_h4_release_identity_candidate(self.normalized))
        candidate["truth_boundary"]["signature_metadata_proves_authenticity"] = True
        self.assertTrue(detect_h4_truth_boundary_violations(candidate))


if __name__ == "__main__":
    unittest.main()
