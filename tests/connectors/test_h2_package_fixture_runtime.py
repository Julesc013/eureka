import copy
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h2_package_registries.fixture_loader import load_h2_package_fixture
from archive.prototypes.legacy_runtime.connectors.h2_package_registries.normalizer_common import (
    H2_SOURCE_IDS,
    build_h2_fixture_replay_result,
    detect_h2_package_product_boundary_violations,
    detect_h2_package_truth_boundary_violations,
)
from scripts.validate_h2_package_registry_fixture_runtime import validate_normalized_record, validate_replay_result


REPO_ROOT = Path(__file__).resolve().parents[2]


def normalizer(source_id):
    module = __import__(f"archive.prototypes.legacy_runtime.connectors.h2_package_registries.{source_id}", fromlist=["normalize"])
    return module.normalize


class H2PackageFixtureRuntimeTests(unittest.TestCase):
    def fixture(self, source_id, kind):
        return load_h2_package_fixture(REPO_ROOT / f"examples/connectors/h2_package_registries/fixtures/{source_id}/{kind}_record.json")

    def test_all_eight_normalizers_handle_minimal_fixtures(self):
        for source_id in H2_SOURCE_IDS:
            record = normalizer(source_id)(self.fixture(source_id, "minimal"))
            self.assertEqual(record["source_id"], source_id)
            self.assertEqual(record["schema_version"], "h2_package_normalized_record.v0")

    def test_all_eight_normalizers_handle_typical_fixtures(self):
        for source_id in H2_SOURCE_IDS:
            record = normalizer(source_id)(self.fixture(source_id, "typical"))
            self.assertEqual(validate_normalized_record(record, source_id), [])
            self.assertNotEqual(record["description_summary"], "unknown")

    def test_all_eight_normalizers_handle_dependency_fixtures(self):
        for source_id in H2_SOURCE_IDS:
            record = normalizer(source_id)(self.fixture(source_id, "dependency"))
            self.assertGreaterEqual(len(record["dependency_candidate_preview"]), 2)

    def test_all_eight_normalizers_handle_policy_blocked_fixtures(self):
        for source_id in H2_SOURCE_IDS:
            record = normalizer(source_id)(self.fixture(source_id, "policy_blocked"))
            self.assertIn("policy-blocked fixture", " ".join(record["source_limitations"]))
            replay = build_h2_fixture_replay_result(self.fixture(source_id, "policy_blocked"), record)
            self.assertEqual(replay["replay_status"], "policy_blocked_fixture")

    def test_missing_optional_fields_produce_limitations_not_fabricated_data(self):
        record = normalizer("crates_io")(self.fixture("crates_io", "minimal"))
        self.assertEqual(record["version"], "unknown")
        self.assertTrue(any("optional field absent or unknown" in item for item in record["source_limitations"]))

    def test_public_and_master_index_mutation_claims_are_rejected(self):
        record = normalizer("crates_io")(self.fixture("crates_io", "typical"))
        public = copy.deepcopy(record)
        public["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(detect_h2_package_product_boundary_violations(public))
        master = copy.deepcopy(record)
        master["truth_boundary"]["master_index_mutated"] = True
        self.assertTrue(detect_h2_package_truth_boundary_violations(master))

    def test_rights_malware_installability_claims_are_rejected(self):
        record = normalizer("crates_io")(self.fixture("crates_io", "typical"))
        for key in ("rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed"):
            mutated = copy.deepcopy(record)
            mutated["truth_boundary"][key] = True
            self.assertTrue(detect_h2_package_truth_boundary_violations(mutated))

    def test_replay_result_validates(self):
        fixture = self.fixture("crates_io", "typical")
        record = normalizer("crates_io")(fixture)
        result = build_h2_fixture_replay_result(fixture, record)
        self.assertEqual(validate_replay_result(result, "crates_io"), [])


if __name__ == "__main__":
    unittest.main()

