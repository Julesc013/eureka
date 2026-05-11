from __future__ import annotations

import copy
import unittest

from scripts import validate_h12_retro_community_policy_packs as validator


class H12RetroCommunityPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_source_enablement_flags_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/winworld_metadata_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "live_access_enabled",
            "source_sync_enabled",
            "connector_runtime_enabled",
            "api_query_enabled",
            "catalog_fetch_enabled",
            "html_catalog_fetch_enabled",
            "forum_or_comment_fetch_enabled",
            "gated_source_access_enabled",
            "account_access_enabled",
            "download_enabled",
            "extraction_enabled",
            "execution_enabled",
            "acquisition_action_enabled",
            "file_upload_enabled",
            "hash_submission_enabled",
            "scraping_enabled",
            "crawling_enabled",
            "bypass_or_automation_enabled",
        ):
            mutated = copy.deepcopy(record)
            mutated[key] = True
            errors = validator.validate_source_record("winworld_metadata", mutated, known)
            self.assertTrue(errors, key)

    def test_policy_pack_granting_live_access_fails(self) -> None:
        pack = validator._load_json(validator.REPO_ROOT / "examples/connectors/h12_retro_community/policies/winworld_metadata_policy_pack_v0.json")
        mutated = copy.deepcopy(pack)
        mutated["policy_pack_grants_live_access"] = True
        errors = validator.validate_policy_pack("winworld_metadata", mutated)
        self.assertTrue(errors)

    def test_preview_overclaims_fail(self) -> None:
        coverage = validator._load_json(validator.REPO_ROOT / "examples/connectors/h12_retro_community/coverage/h12_retro_community_coverage_preview_v0.json")
        coverage["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage))
        scorecard = validator._load_json(validator.REPO_ROOT / "examples/connectors/h12_retro_community/scorecards/h12_retro_community_scorecard_preview_v0.json")
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))
        scorecard["production_ready"] = False
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))

    def test_truth_and_payload_claims_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/winworld_metadata_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "accepted_retro_software_identity_truth",
            "accepted_platform_version_truth",
            "accepted_archive_item_member_truth",
            "accepted_compatibility_install_truth",
            "accepted_community_review_truth",
            "accepted_hash_checksum_truth",
            "accepted_ia_wayback_corroboration_truth",
            "accepted_gated_source_access_truth",
            "accepted_rights_safety_truth",
            "public_index_mutated",
            "master_index_mutated",
            "rights_clearance_claimed",
            "legal_acquisition_claimed",
            "file_authenticity_claimed",
            "checksum_correctness_claimed",
            "compatibility_correctness_claimed",
            "installability_claimed",
            "playability_claimed",
            "malware_safety_claimed",
            "content_safety_claimed",
            "privacy_safety_claimed",
            "community_reputation_claimed",
            "verified_authenticity_claimed",
        ):
            mutated = copy.deepcopy(record)
            mutated["truth_boundary"][key] = True
            self.assertTrue(validator.validate_source_record("winworld_metadata", mutated, known), key)
        for payload_key in (
            "api_token",
            "software_binary_payload",
            "rom_payload",
            "iso_payload",
            "bios_payload",
            "installer_payload",
            "patch_payload",
            "crack_payload",
            "serial_payload",
            "extraction_log",
            "execution_log",
            "acquisition_output",
            "gated_private_content",
            "scraping_output",
        ):
            errors: list[str] = []
            validator._scan_json_payload("synthetic", {payload_key: "not allowed"}, errors)
            self.assertTrue(errors, payload_key)


if __name__ == "__main__":
    unittest.main()
