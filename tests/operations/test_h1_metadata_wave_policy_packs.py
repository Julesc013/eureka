import copy
import json
from pathlib import Path
import unittest


from scripts import validate_h1_metadata_wave_policy_packs as validator


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel):
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class H1MetadataWavePolicyPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        errors = []
        cls.known = validator.load_h0_known_values(REPO_ROOT, errors)
        if errors:
            raise AssertionError(errors)

    def test_all_seven_source_records_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_source_record(load_json(paths["source_record"]), source_id, self.known)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_seven_policy_packs_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_policy_pack(load_json(paths["policy_pack"]), source_id)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_seven_coverage_previews_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_coverage_preview(load_json(paths["coverage"]), source_id, self.known)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_seven_scorecard_previews_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_scorecard_preview(load_json(paths["scorecard"]), source_id)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_source_with_live_access_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["pypi"]["source_record"])
        record["live_access_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "pypi", self.known))

    def test_source_with_source_sync_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["pypi"]["source_record"])
        record["source_sync_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "pypi", self.known))

    def test_source_with_connector_runtime_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["pypi"]["source_record"])
        record["connector_runtime_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "pypi", self.known))

    def test_policy_pack_granting_live_access_fails(self):
        pack = load_json(validator.EXPECTED_SOURCES["github_releases"]["policy_pack"])
        pack["policy_pack_grants_live_access"] = True
        self.assertTrue(validator.validate_policy_pack(pack, "github_releases"))

    def test_policy_pack_with_forbidden_current_operation_fails(self):
        pack = load_json(validator.EXPECTED_SOURCES["github_releases"]["policy_pack"])
        pack["allowed_current_operations"] = list(pack["allowed_current_operations"]) + ["live_probe_result"]
        self.assertTrue(validator.validate_policy_pack(pack, "github_releases"))

    def test_coverage_preview_claiming_exhaustive_coverage_fails(self):
        coverage = load_json(validator.EXPECTED_SOURCES["repology"]["coverage"])
        coverage = copy.deepcopy(coverage)
        coverage["truth_boundary"]["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage, "repology", self.known))

    def test_scorecard_claiming_production_readiness_fails(self):
        scorecard = load_json(validator.EXPECTED_SOURCES["osv"]["scorecard"])
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "osv"))

    def test_scorecard_auto_approving_future_connectors_fails(self):
        scorecard = load_json(validator.EXPECTED_SOURCES["osv"]["scorecard"])
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "osv"))

    def test_public_index_mutation_claim_fails(self):
        scorecard = load_json(validator.EXPECTED_SOURCES["osv"]["scorecard"])
        scorecard = copy.deepcopy(scorecard)
        scorecard["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "osv"))

    def test_master_index_mutation_claim_fails(self):
        coverage = load_json(validator.EXPECTED_SOURCES["repology"]["coverage"])
        coverage = copy.deepcopy(coverage)
        coverage["product_boundary"]["mutated_master_index"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage, "repology", self.known))

    def test_rights_malware_installability_claim_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["pypi"]["source_record"])
        record = copy.deepcopy(record)
        record["truth_boundary"]["source_record_can_claim_rights_clearance"] = True
        record["truth_boundary"]["source_record_can_claim_malware_safety"] = True
        record["truth_boundary"]["source_record_can_claim_verified_installability"] = True
        errors = validator.validate_source_record(record, "pypi", self.known)
        self.assertGreaterEqual(len(errors), 3)

    def test_credentials_api_token_fixture_fails_secret_scan(self):
        self.assertIsNotNone(validator.SECRET_KEY_RE.search('{"api_token": "not-allowed"}'))

    def test_validator_passes_current_repo(self):
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])


if __name__ == "__main__":
    unittest.main()
