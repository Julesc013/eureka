import copy
from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import (
    build_h4_source_identity_candidate,
    detect_h4_truth_boundary_violations,
)
from control.prototypes.legacy_runtime.connectors.h4_code_source_release.github_repository import normalize
from control.prototypes.legacy_runtime.connectors.h4_code_source_release.fixture_loader import load_h4_code_source_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


class H4SourceIdentityMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = load_h4_code_source_fixture(REPO_ROOT / "examples/connectors/h4_code_source_release/fixtures/github_repository/source_identity_record.json")
        cls.normalized = normalize(fixture)

    def test_source_identity_candidate_not_truth(self):
        candidate = build_h4_source_identity_candidate(self.normalized)
        self.assertFalse(candidate["truth_boundary"]["source_identity_candidate_is_accepted_identity"])
        self.assertFalse(candidate["truth_boundary"]["repository_url_proves_official_status"])

    def test_git_object_candidate_not_provenance_truth(self):
        candidate = build_h4_source_identity_candidate(self.normalized)
        self.assertFalse(candidate["truth_boundary"]["git_object_candidate_is_accepted_provenance"])

    def test_swhid_candidate_not_object_truth(self):
        candidate = build_h4_source_identity_candidate(self.normalized)
        candidate["swhid_candidate"] = "swh:1:dir:fixture"
        self.assertFalse(candidate["truth_boundary"]["swhid_candidate_is_accepted_object_truth"])

    def test_source_identity_truth_claim_rejected(self):
        candidate = copy.deepcopy(build_h4_source_identity_candidate(self.normalized))
        candidate["truth_boundary"]["source_identity_candidate_is_accepted_identity"] = True
        self.assertTrue(detect_h4_truth_boundary_violations(candidate))

    def test_public_master_index_claim_rejected(self):
        candidate = copy.deepcopy(build_h4_source_identity_candidate(self.normalized))
        candidate["truth_boundary"]["public_index_mutated"] = True
        candidate["truth_boundary"]["master_index_mutated"] = True
        self.assertGreaterEqual(len(detect_h4_truth_boundary_violations(candidate)), 2)


if __name__ == "__main__":
    unittest.main()
