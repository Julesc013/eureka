import copy
import json
from pathlib import Path
import unittest


from scripts import validate_h2_package_registry_policy_packs as validator


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel):
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class H2PackageRegistryPolicyPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        errors = []
        cls.known = validator.load_h0_known_values(REPO_ROOT, errors)
        if errors:
            raise AssertionError(errors)

    def test_all_eight_source_records_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_source_record(load_json(paths["source_record"]), source_id, self.known)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_eight_policy_packs_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_policy_pack(load_json(paths["policy_pack"]), source_id)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_eight_coverage_previews_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_coverage_preview(load_json(paths["coverage"]), source_id, self.known)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_eight_scorecard_previews_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_scorecard_preview(load_json(paths["scorecard"]), source_id)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_package_identity_policy_validates(self):
        errors = validator.validate_identity_policy(load_json("control/inventory/source_packs/h2_package_registry_identity_policy.json"))
        self.assertEqual(errors, [])

    def test_source_with_live_access_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["maven_central"]["source_record"])
        record["live_access_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "maven_central", self.known))

    def test_source_with_source_sync_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["nuget"]["source_record"])
        record["source_sync_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "nuget", self.known))

    def test_source_with_connector_runtime_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["crates_io"]["source_record"])
        record["connector_runtime_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "crates_io", self.known))

    def test_source_with_package_download_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["rubygems"]["source_record"])
        record["package_download_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "rubygems", self.known))

    def test_source_with_install_execute_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["cpan"]["source_record"])
        record["install_execute_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "cpan", self.known))

    def test_policy_pack_granting_live_access_fails(self):
        pack = load_json(validator.EXPECTED_SOURCES["cran"]["policy_pack"])
        pack["policy_pack_grants_live_access"] = True
        self.assertTrue(validator.validate_policy_pack(pack, "cran"))

    def test_coverage_preview_claiming_exhaustive_coverage_fails(self):
        coverage = load_json(validator.EXPECTED_SOURCES["conda_forge"]["coverage"])
        coverage = copy.deepcopy(coverage)
        coverage["truth_boundary"]["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage, "conda_forge", self.known))

    def test_scorecard_claiming_production_readiness_fails(self):
        scorecard = load_json(validator.EXPECTED_SOURCES["oci_registry_metadata"]["scorecard"])
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "oci_registry_metadata"))

    def test_scorecard_auto_approving_future_connectors_fails(self):
        scorecard = load_json(validator.EXPECTED_SOURCES["oci_registry_metadata"]["scorecard"])
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "oci_registry_metadata"))

    def test_public_index_mutation_claim_fails(self):
        scorecard = load_json(validator.EXPECTED_SOURCES["nuget"]["scorecard"])
        scorecard = copy.deepcopy(scorecard)
        scorecard["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "nuget"))

    def test_master_index_mutation_claim_fails(self):
        coverage = load_json(validator.EXPECTED_SOURCES["maven_central"]["coverage"])
        coverage = copy.deepcopy(coverage)
        coverage["product_boundary"]["mutated_master_index"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage, "maven_central", self.known))

    def test_rights_malware_installability_claim_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["maven_central"]["source_record"])
        record = copy.deepcopy(record)
        record["truth_boundary"]["source_record_can_claim_rights_clearance"] = True
        record["truth_boundary"]["source_record_can_claim_malware_safety"] = True
        record["truth_boundary"]["source_record_can_claim_verified_installability"] = True
        errors = validator.validate_source_record(record, "maven_central", self.known)
        self.assertGreaterEqual(len(errors), 3)

    def test_dependency_correctness_claim_fails(self):
        pack = load_json(validator.EXPECTED_SOURCES["crates_io"]["policy_pack"])
        pack = copy.deepcopy(pack)
        pack["truth_boundary"]["dependency_metadata_proves_dependency_correctness"] = True
        self.assertTrue(validator.validate_policy_pack(pack, "crates_io"))

    def test_credentials_api_token_fixture_fails_secret_scan(self):
        self.assertIsNotNone(validator.SECRET_KEY_RE.search('{"api_token": "not-allowed"}'))

    def test_package_payload_fixture_fails_payload_scan(self):
        self.assertIsNotNone(validator.PACKAGE_PAYLOAD_RE.search('{"jar_bytes": "not-allowed"}'))

    def test_validator_passes_current_repo(self):
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])


if __name__ == "__main__":
    unittest.main()
