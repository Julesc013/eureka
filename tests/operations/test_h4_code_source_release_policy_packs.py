import copy
import json
from pathlib import Path
import unittest


from scripts import validate_h4_code_source_release_policy_packs as validator


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(rel):
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class H4CodeSourceReleasePolicyPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        errors = []
        cls.known = validator.load_known_values(REPO_ROOT, errors)
        mapping = load_json("control/inventory/source_packs/h4_code_source_release_connector_families.json")
        validator.add_h4_planned_connector_families(mapping, cls.known)
        if errors:
            raise AssertionError(errors)

    def test_all_ten_source_records_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_source_record(load_json(paths["source_record"]), source_id, self.known)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_ten_policy_packs_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_policy_pack(load_json(paths["policy_pack"]), source_id)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_ten_coverage_previews_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_coverage_preview(load_json(paths["coverage"]), source_id, self.known)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_all_ten_scorecard_previews_validate(self):
        for source_id, paths in validator.EXPECTED_SOURCES.items():
            errors = validator.validate_scorecard_preview(load_json(paths["scorecard"]), source_id)
            self.assertEqual(errors, [], f"{source_id}: {errors}")

    def test_source_identity_policy_validates(self):
        errors = validator.validate_source_identity_policy(load_json("control/inventory/source_packs/h4_source_identity_policy.json"))
        self.assertEqual(errors, [])

    def test_release_identity_policy_validates(self):
        errors = validator.validate_release_identity_policy(load_json("control/inventory/source_packs/h4_release_identity_policy.json"))
        self.assertEqual(errors, [])

    def test_source_to_binary_relation_policy_validates(self):
        errors = validator.validate_relation_policy(load_json("control/inventory/source_packs/h4_source_to_binary_relation_policy.json"))
        self.assertEqual(errors, [])

    def test_source_with_live_access_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["software_heritage_identity"]["source_record"])
        record["live_access_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "software_heritage_identity", self.known))

    def test_source_with_source_sync_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["github_repository"]["source_record"])
        record["source_sync_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "github_repository", self.known))

    def test_source_with_connector_runtime_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["github_releases"]["source_record"])
        record["connector_runtime_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "github_releases", self.known))

    def test_source_with_repository_clone_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["gitlab_repository"]["source_record"])
        record["repository_clone_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "gitlab_repository", self.known))

    def test_source_with_source_archive_download_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["gitlab_releases"]["source_record"])
        record["source_archive_download_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "gitlab_releases", self.known))

    def test_source_with_release_asset_download_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["sourceforge"]["source_record"])
        record["release_asset_download_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "sourceforge", self.known))

    def test_source_with_git_command_invocation_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["fosshub"]["source_record"])
        record["git_command_invocation_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "fosshub", self.known))

    def test_source_with_build_tool_invocation_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["github_archive_program"]["source_record"])
        record["build_tool_invocation_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "github_archive_program", self.known))

    def test_source_with_install_execute_enabled_true_fails(self):
        record = load_json(validator.EXPECTED_SOURCES["generic_git_repository"]["source_record"])
        record["install_execute_enabled"] = True
        self.assertTrue(validator.validate_source_record(record, "generic_git_repository", self.known))

    def test_policy_pack_granting_live_access_fails(self):
        pack = load_json(validator.EXPECTED_SOURCES["generic_release_host"]["policy_pack"])
        pack["policy_pack_grants_live_access"] = True
        self.assertTrue(validator.validate_policy_pack(pack, "generic_release_host"))

    def test_coverage_preview_claiming_exhaustive_coverage_fails(self):
        coverage = copy.deepcopy(load_json(validator.EXPECTED_SOURCES["software_heritage_identity"]["coverage"]))
        coverage["truth_boundary"]["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage, "software_heritage_identity", self.known))

    def test_scorecard_claiming_production_readiness_fails(self):
        scorecard = load_json(validator.EXPECTED_SOURCES["github_repository"]["scorecard"])
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "github_repository"))

    def test_scorecard_auto_approving_future_connectors_fails(self):
        scorecard = load_json(validator.EXPECTED_SOURCES["github_releases"]["scorecard"])
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "github_releases"))

    def test_public_index_mutation_claim_fails(self):
        scorecard = copy.deepcopy(load_json(validator.EXPECTED_SOURCES["gitlab_repository"]["scorecard"]))
        scorecard["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard, "gitlab_repository"))

    def test_master_index_mutation_claim_fails(self):
        coverage = copy.deepcopy(load_json(validator.EXPECTED_SOURCES["gitlab_releases"]["coverage"]))
        coverage["product_boundary"]["mutated_master_index"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage, "gitlab_releases", self.known))

    def test_rights_malware_installability_claim_fails(self):
        record = copy.deepcopy(load_json(validator.EXPECTED_SOURCES["sourceforge"]["source_record"]))
        record["truth_boundary"]["rights_clearance_claimed"] = True
        record["truth_boundary"]["malware_safety_claimed"] = True
        record["truth_boundary"]["verified_installability_claimed"] = True
        errors = validator.validate_source_record(record, "sourceforge", self.known)
        self.assertGreaterEqual(len(errors), 3)

    def test_source_authenticity_claim_fails(self):
        pack = copy.deepcopy(load_json(validator.EXPECTED_SOURCES["fosshub"]["policy_pack"]))
        pack["truth_boundary"]["signature_metadata_proves_authenticity"] = True
        self.assertTrue(validator.validate_policy_pack(pack, "fosshub"))

    def test_release_authenticity_claim_fails(self):
        pack = copy.deepcopy(load_json(validator.EXPECTED_SOURCES["github_archive_program"]["policy_pack"]))
        pack["truth_boundary"]["release_metadata_is_release_truth"] = True
        self.assertTrue(validator.validate_policy_pack(pack, "github_archive_program"))

    def test_build_reproducibility_claim_fails(self):
        pack = copy.deepcopy(load_json(validator.EXPECTED_SOURCES["generic_git_repository"]["policy_pack"]))
        pack["truth_boundary"]["source_archive_asset_proves_build_reproducibility"] = True
        self.assertTrue(validator.validate_policy_pack(pack, "generic_git_repository"))

    def test_source_to_binary_provenance_truth_claim_fails(self):
        pack = copy.deepcopy(load_json(validator.EXPECTED_SOURCES["generic_release_host"]["policy_pack"]))
        pack["truth_boundary"]["source_to_binary_relation_candidate_is_provenance_truth"] = True
        self.assertTrue(validator.validate_policy_pack(pack, "generic_release_host"))

    def test_credential_api_token_fixture_fails_secret_scan(self):
        self.assertIsNotNone(validator.SECRET_KEY_RE.search('{"api_token": "not-allowed"}'))

    def test_repository_payload_fixture_fails_payload_scan(self):
        self.assertIsNotNone(validator.REPOSITORY_PAYLOAD_RE.search('{"repository_payload": "not-allowed"}'))

    def test_release_asset_payload_fixture_fails_payload_scan(self):
        self.assertIsNotNone(validator.REPOSITORY_PAYLOAD_RE.search('{"release_asset_payload": "not-allowed"}'))

    def test_validator_passes_current_repo(self):
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])


if __name__ == "__main__":
    unittest.main()
