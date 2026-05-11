from __future__ import annotations

import copy
import unittest

from scripts import validate_h10_games_emulation_policy_packs as validator


class H10GamesEmulationPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_source_enablement_flags_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/mobygames_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "live_access_enabled",
            "source_sync_enabled",
            "connector_runtime_enabled",
            "api_query_enabled",
            "catalog_fetch_enabled",
            "software_list_fetch_enabled",
            "hashset_fetch_enabled",
            "rom_download_enabled",
            "iso_download_enabled",
            "bios_firmware_download_enabled",
            "game_binary_download_enabled",
            "emulator_download_enabled",
            "file_upload_enabled",
            "hash_submission_enabled",
            "emulator_execution_enabled",
            "game_execution_enabled",
            "install_execute_enabled",
            "acquisition_action_enabled",
            "scraping_enabled",
            "crawling_enabled",
            "bypass_or_automation_enabled",
        ):
            mutated = copy.deepcopy(record)
            mutated[key] = True
            errors = validator.validate_source_record("mobygames", mutated, known)
            self.assertTrue(errors, key)

    def test_policy_pack_granting_live_access_fails(self) -> None:
        pack = validator._load_json(validator.REPO_ROOT / "examples/connectors/h10_games_emulation/policies/mobygames_policy_pack_v0.json")
        mutated = copy.deepcopy(pack)
        mutated["policy_pack_grants_live_access"] = True
        errors = validator.validate_policy_pack("mobygames", mutated)
        self.assertTrue(errors)

    def test_preview_overclaims_fail(self) -> None:
        coverage = validator._load_json(validator.REPO_ROOT / "examples/connectors/h10_games_emulation/coverage/h10_games_emulation_coverage_preview_v0.json")
        coverage["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage))
        scorecard = validator._load_json(validator.REPO_ROOT / "examples/connectors/h10_games_emulation/scorecards/h10_games_emulation_scorecard_preview_v0.json")
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))
        scorecard["production_ready"] = False
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))

    def test_truth_and_payload_claims_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/mobygames_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "accepted_game_identity_truth",
            "accepted_release_truth",
            "accepted_platform_truth",
            "accepted_emulator_compatibility_truth",
            "accepted_hashset_truth",
            "accepted_rom_disc_media_truth",
            "accepted_game_relation_truth",
            "accepted_action_permission",
            "accepted_rights_safety_truth",
            "public_index_mutated",
            "master_index_mutated",
            "rights_clearance_claimed",
            "legal_acquisition_claimed",
            "rom_authenticity_claimed",
            "disc_authenticity_claimed",
            "compatibility_correctness_claimed",
            "playability_claimed",
            "malware_safety_claimed",
            "content_safety_claimed",
            "privacy_safety_claimed",
            "verified_authenticity_claimed",
        ):
            mutated = copy.deepcopy(record)
            mutated["truth_boundary"][key] = True
            self.assertTrue(validator.validate_source_record("mobygames", mutated, known), key)
        errors: list[str] = []
        validator._scan_json_payload("synthetic", {"api_token": "secret"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("synthetic", {"rom_payload": "not allowed"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("synthetic", {"execution_log": "not allowed"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("synthetic", {"acquisition_output": "not allowed"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("synthetic", {"scraping_output": "not allowed"}, errors)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
