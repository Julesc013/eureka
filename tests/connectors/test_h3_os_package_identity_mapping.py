import copy
from pathlib import Path
import unittest

from runtime.connectors.h3_os_package_archives.fixture_loader import load_h3_os_package_fixture
from runtime.connectors.h3_os_package_archives.normalizer_common import (
    build_h3_dependency_candidates,
    build_h3_os_package_identity_candidate,
    build_h3_package_file_candidates,
    detect_h3_truth_boundary_violations,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def record():
    fixture = load_h3_os_package_fixture(REPO_ROOT / "examples/connectors/h3_os_package_archives/fixtures/debian_snapshot/typical_record.json")
    module = __import__("runtime.connectors.h3_os_package_archives.debian_snapshot", fromlist=["normalize"])
    return module.normalize(fixture)


class H3OSPackageIdentityMappingTests(unittest.TestCase):
    def test_os_package_identity_fields_do_not_become_accepted_identity_truth(self):
        identity = build_h3_os_package_identity_candidate(record())
        self.assertFalse(identity["truth_boundary"]["identity_candidate_is_accepted_identity"])
        self.assertFalse(identity["truth_boundary"]["purl_candidate_is_accepted_identity"])

    def test_purl_candidate_does_not_become_truth(self):
        identity = record()["os_package_identity_candidate"]
        mutated = copy.deepcopy(identity)
        mutated["truth_boundary"]["purl_candidate_is_truth"] = True
        self.assertTrue(detect_h3_truth_boundary_violations(mutated))

    def test_dependency_conflict_provides_do_not_become_correctness(self):
        deps = build_h3_dependency_candidates(record())
        self.assertTrue(deps)
        self.assertFalse(deps[0]["truth_boundary"]["dependency_candidate_proves_correctness"])
        mutated = copy.deepcopy(deps[0])
        mutated["truth_boundary"]["dependency_correctness_claimed"] = True
        self.assertTrue(detect_h3_truth_boundary_violations(mutated))

    def test_hash_fields_do_not_become_malware_safety(self):
        files = build_h3_package_file_candidates(record())
        self.assertTrue(files)
        self.assertFalse(files[0]["truth_boundary"]["file_hash_candidate_is_malware_safety"])
        mutated = copy.deepcopy(files[0])
        mutated["truth_boundary"]["file_hash_candidate_is_malware_safety"] = True
        self.assertTrue(detect_h3_truth_boundary_violations(mutated))

    def test_license_and_repository_metadata_do_not_overclaim(self):
        normalized = record()
        self.assertFalse(normalized["truth_boundary"]["license_metadata_is_rights_clearance"])
        self.assertFalse(normalized["truth_boundary"]["repository_metadata_is_installability_verification"])

    def test_file_locator_fields_do_not_become_download_permission(self):
        files = build_h3_package_file_candidates(record())
        self.assertFalse(files[0]["download_allowed_current"])
        mutated = copy.deepcopy(files[0])
        mutated["download_allowed_current"] = True
        self.assertTrue(detect_h3_truth_boundary_violations(mutated))

    def test_source_cache_and_evidence_previews_are_not_accepted(self):
        normalized = record()
        self.assertFalse(normalized["source_cache_candidate_preview"]["accepted_source_truth"])
        self.assertFalse(normalized["evidence_candidate_preview"]["accepted_evidence"])


if __name__ == "__main__":
    unittest.main()
