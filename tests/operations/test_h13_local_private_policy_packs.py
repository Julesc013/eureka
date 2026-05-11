from __future__ import annotations

import copy
import unittest

from scripts import validate_h13_local_private_policy_packs as validator


class H13LocalPrivatePolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_source_enablement_flags_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/local_folder_metadata_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "local_access_enabled", "private_source_access_enabled", "user_supplied_url_access_enabled",
            "authenticated_source_access_enabled", "restricted_source_access_enabled", "source_sync_enabled",
            "connector_runtime_enabled", "filesystem_scan_enabled", "directory_listing_enabled",
            "archive_listing_enabled", "CAS_import_enabled", "pack_export_enabled", "pack_import_enabled",
            "extraction_enabled", "execution_enabled", "acquisition_action_enabled", "upload_enabled",
            "public_share_enabled",
        ):
            mutated = copy.deepcopy(record)
            mutated[key] = True
            self.assertTrue(validator.validate_source_record("local_folder_metadata", mutated, known), key)

    def test_policy_pack_granting_access_fails(self) -> None:
        pack = validator._load_json(validator.REPO_ROOT / "examples/connectors/h13_local_private/policies/local_folder_metadata_policy_pack_v0.json")
        mutated = copy.deepcopy(pack)
        mutated["policy_pack_grants_access"] = True
        self.assertTrue(validator.validate_policy_pack("local_folder_metadata", mutated))

    def test_preview_overclaims_fail(self) -> None:
        coverage = validator._load_json(validator.REPO_ROOT / "examples/connectors/h13_local_private/coverage/h13_local_private_coverage_preview_v0.json")
        coverage["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage))
        scorecard = validator._load_json(validator.REPO_ROOT / "examples/connectors/h13_local_private/scorecards/h13_local_private_scorecard_preview_v0.json")
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))
        scorecard["production_ready"] = False
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))

    def test_truth_and_private_payload_claims_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/local_folder_metadata_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "accepted_local_source_identity_truth", "accepted_private_source_truth",
            "accepted_user_supplied_url_truth", "accepted_authenticated_source_truth",
            "accepted_restricted_source_truth", "accepted_CAS_import_truth",
            "accepted_pack_export_import_truth", "accepted_privacy_redaction_truth",
            "accepted_rights_safety_truth", "public_index_mutated", "master_index_mutated",
            "rights_clearance_claimed", "ownership_truth_claimed", "user_authority_claimed",
            "legal_access_claimed", "publication_permission_claimed", "privacy_safety_claimed",
            "malware_safety_claimed", "source_safety_claimed", "verified_authenticity_claimed",
        ):
            mutated = copy.deepcopy(record)
            mutated["truth_boundary"][key] = True
            self.assertTrue(validator.validate_source_record("local_folder_metadata", mutated, known), key)
        for payload_key in (
            "api_token", "credential", "private_file_payload", "local_file_payload", "file_content",
            "private_source_payload", "account_data", "cas_blob", "exported_pack", "imported_pack",
            "source_cache_write", "public_index_write",
        ):
            errors: list[str] = []
            validator._scan_json_payload("synthetic", {payload_key: "not allowed"}, errors)
            self.assertTrue(errors, payload_key)
        errors = []
        validator._scan_json_payload("synthetic", {"path": "C:\\Users\\Example\\private.bin"}, errors)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
