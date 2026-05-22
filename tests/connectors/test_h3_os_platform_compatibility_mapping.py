import copy
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.fixture_loader import load_h3_os_package_fixture
from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.normalizer_common import (
    build_h3_os_platform_compatibility_candidate,
    detect_h3_truth_boundary_violations,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def record():
    fixture = load_h3_os_package_fixture(REPO_ROOT / "examples/connectors/h3_os_package_archives/fixtures/debian_snapshot/compatibility_record.json")
    module = __import__("archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.debian_snapshot", fromlist=["normalize"])
    return module.normalize(fixture)


class H3OSPlatformCompatibilityMappingTests(unittest.TestCase):
    def test_compatibility_fields_do_not_become_verified_compatibility(self):
        candidate = build_h3_os_platform_compatibility_candidate(record())
        self.assertFalse(candidate["truth_boundary"]["compatibility_candidate_is_verified_compatibility"])
        mutated = copy.deepcopy(candidate)
        mutated["truth_boundary"]["compatibility_candidate_is_verified_compatibility"] = True
        self.assertTrue(detect_h3_truth_boundary_violations(mutated))

    def test_repository_presence_does_not_prove_installability(self):
        candidate = build_h3_os_platform_compatibility_candidate(record())
        self.assertFalse(candidate["truth_boundary"]["repository_presence_proves_installability"])

    def test_architecture_match_does_not_prove_runtime_compatibility(self):
        candidate = build_h3_os_platform_compatibility_candidate(record())
        self.assertFalse(candidate["truth_boundary"]["architecture_match_proves_runtime_compatibility"])

    def test_dependency_environment_does_not_prove_solvability(self):
        candidate = build_h3_os_platform_compatibility_candidate(record())
        mutated = copy.deepcopy(candidate)
        mutated["truth_boundary"]["compatibility_correctness_claimed"] = True
        self.assertTrue(detect_h3_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
