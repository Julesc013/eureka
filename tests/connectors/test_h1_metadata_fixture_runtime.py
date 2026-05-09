import copy
from pathlib import Path
import unittest


from runtime.connectors.h1_metadata_wave.fixture_loader import load_h1_fixture
from runtime.connectors.h1_metadata_wave.normalizer_common import (
    H1_SOURCE_IDS,
    build_h1_evidence_candidate_preview,
    build_h1_fixture_replay_result,
    build_h1_source_cache_candidate_preview,
    detect_h1_product_boundary_violations,
    detect_h1_truth_boundary_violations,
)
from scripts.validate_h1_metadata_fixture_runtime import validate_normalized_record, validate_replay_result


REPO_ROOT = Path(__file__).resolve().parents[2]


def normalizer(source_id):
    module = __import__(f"runtime.connectors.h1_metadata_wave.{source_id}", fromlist=["normalize"])
    return module.normalize


class H1MetadataFixtureRuntimeTests(unittest.TestCase):
    def fixture(self, source_id, kind):
        return load_h1_fixture(REPO_ROOT / f"examples/connectors/h1_metadata_wave/fixtures/{source_id}/{kind}_record.json")

    def test_all_seven_normalizers_handle_minimal_fixtures(self):
        for source_id in H1_SOURCE_IDS:
            record = normalizer(source_id)(self.fixture(source_id, "minimal"))
            self.assertEqual(record["source_id"], source_id)
            self.assertEqual(record["schema_version"], "h1_metadata_normalized_record.v0")

    def test_all_seven_normalizers_handle_typical_fixtures(self):
        for source_id in H1_SOURCE_IDS:
            record = normalizer(source_id)(self.fixture(source_id, "typical"))
            self.assertEqual(validate_normalized_record(record, source_id), [])
            self.assertNotEqual(record["description_summary"], "unknown")

    def test_all_seven_normalizers_handle_policy_blocked_fixtures(self):
        for source_id in H1_SOURCE_IDS:
            record = normalizer(source_id)(self.fixture(source_id, "policy_blocked"))
            self.assertIn("policy-blocked fixture", " ".join(record["source_limitations"]))
            replay = build_h1_fixture_replay_result(self.fixture(source_id, "policy_blocked"), record)
            self.assertEqual(replay["replay_status"], "policy_blocked_fixture")

    def test_missing_optional_fields_produce_limitations_not_fabricated_data(self):
        record = normalizer("pypi")(self.fixture("pypi", "minimal"))
        self.assertEqual(record["version_or_state"], "unknown")
        self.assertTrue(any("optional field absent or unknown" in item for item in record["source_limitations"]))

    def test_title_version_package_fields_do_not_become_accepted_truth(self):
        record = normalizer("pypi")(self.fixture("pypi", "typical"))
        truth = record["truth_boundary"]
        self.assertFalse(truth["title_match_is_verified_identity"])
        self.assertFalse(truth["version_field_is_accepted_release_truth"])
        self.assertFalse(truth["package_metadata_is_installability_verification"])

    def test_release_asset_file_fields_do_not_become_download_permission(self):
        record = normalizer("github_releases")(self.fixture("github_releases", "typical"))
        self.assertFalse(record["truth_boundary"]["release_asset_entry_is_download_permission"])
        self.assertFalse(record["truth_boundary"]["file_listing_is_local_availability_proof"])

    def test_vulnerability_fields_do_not_become_security_conclusion(self):
        record = normalizer("osv")(self.fixture("osv", "typical"))
        self.assertTrue(record["vulnerability_or_advisory_summary"])
        self.assertFalse(record["truth_boundary"]["vulnerability_record_is_security_conclusion"])

    def test_source_locator_fields_do_not_become_rights_clearance(self):
        record = normalizer("software_heritage")(self.fixture("software_heritage", "typical"))
        self.assertFalse(record["truth_boundary"]["source_locator_is_rights_clearance"])

    def test_source_cache_preview_is_not_accepted_source(self):
        record = normalizer("repology")(self.fixture("repology", "typical"))
        preview = build_h1_source_cache_candidate_preview(record)
        self.assertFalse(preview["accepted_source_truth"])
        self.assertFalse(preview["truth_boundary"]["source_cache_preview_is_accepted_source"])

    def test_evidence_preview_is_not_accepted_evidence(self):
        record = normalizer("osv")(self.fixture("osv", "typical"))
        preview = build_h1_evidence_candidate_preview(record)
        self.assertFalse(preview["accepted_evidence"])
        self.assertFalse(preview["truth_boundary"]["evidence_preview_is_accepted_evidence"])

    def test_public_index_mutation_claim_is_rejected(self):
        record = normalizer("pypi")(self.fixture("pypi", "typical"))
        mutated = copy.deepcopy(record)
        mutated["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(detect_h1_product_boundary_violations(mutated))

    def test_master_index_mutation_claim_is_rejected(self):
        record = normalizer("pypi")(self.fixture("pypi", "typical"))
        mutated = copy.deepcopy(record)
        mutated["truth_boundary"]["master_index_mutated"] = True
        self.assertTrue(detect_h1_truth_boundary_violations(mutated))

    def test_download_permission_claim_is_rejected(self):
        record = normalizer("github_releases")(self.fixture("github_releases", "typical"))
        mutated = copy.deepcopy(record)
        mutated["truth_boundary"]["release_asset_entry_is_download_permission"] = True
        self.assertTrue(detect_h1_truth_boundary_violations(mutated))

    def test_replay_result_validates(self):
        fixture = self.fixture("wayback_cdx_memento", "typical")
        record = normalizer("wayback_cdx_memento")(fixture)
        result = build_h1_fixture_replay_result(fixture, record)
        self.assertEqual(validate_replay_result(result, "wayback_cdx_memento"), [])


if __name__ == "__main__":
    unittest.main()
