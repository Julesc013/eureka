from __future__ import annotations

import copy
import unittest

from scripts import validate_h9_media_metadata_policy_packs as validator


class H9MediaMetadataPolicyPackTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_source_enablement_flags_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/wikimedia_commons_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "live_access_enabled",
            "source_sync_enabled",
            "connector_runtime_enabled",
            "api_query_enabled",
            "catalog_fetch_enabled",
            "media_download_enabled",
            "image_download_enabled",
            "video_download_enabled",
            "audio_download_enabled",
            "map_download_enabled",
            "thumbnail_fetch_enabled",
            "media_upload_enabled",
            "fingerprint_lookup_enabled",
            "fingerprint_submission_enabled",
            "fingerprint_generation_enabled",
            "scraping_enabled",
            "crawling_enabled",
            "bypass_or_automation_enabled",
        ):
            mutated = copy.deepcopy(record)
            mutated[key] = True
            errors = validator.validate_source_record("wikimedia_commons", mutated, known)
            self.assertTrue(errors, key)

    def test_policy_pack_granting_live_access_fails(self) -> None:
        pack = validator._load_json(validator.REPO_ROOT / "examples/connectors/h9_media_metadata/policies/wikimedia_commons_policy_pack_v0.json")
        mutated = copy.deepcopy(pack)
        mutated["policy_pack_grants_live_access"] = True
        errors = validator.validate_policy_pack("wikimedia_commons", mutated)
        self.assertTrue(errors)

    def test_preview_overclaims_fail(self) -> None:
        coverage = validator._load_json(validator.REPO_ROOT / "examples/connectors/h9_media_metadata/coverage/h9_media_metadata_coverage_preview_v0.json")
        coverage["coverage_manifest_is_exhaustive_global_coverage"] = True
        self.assertTrue(validator.validate_coverage_preview(coverage))
        scorecard = validator._load_json(validator.REPO_ROOT / "examples/connectors/h9_media_metadata/scorecards/h9_media_metadata_scorecard_preview_v0.json")
        scorecard["production_ready"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))
        scorecard["production_ready"] = False
        scorecard["auto_approves_future_connectors"] = True
        self.assertTrue(validator.validate_scorecard_preview(scorecard))

    def test_truth_and_payload_claims_fail(self) -> None:
        record = validator._load_json(validator.REPO_ROOT / "examples/sources/source_records/wikimedia_commons_source_v2.json")
        known = validator._load_known_values(validator.REPO_ROOT, [])
        for key in (
            "accepted_media_identity_truth",
            "accepted_music_identity_truth",
            "accepted_image_video_map_truth",
            "accepted_creator_collection_relation_truth",
            "accepted_fingerprint_identity_truth",
            "accepted_rights_license_truth",
            "accepted_safety_privacy_truth",
            "public_index_mutated",
            "master_index_mutated",
            "rights_clearance_claimed",
            "public_domain_truth_claimed",
            "creative_commons_truth_claimed",
            "content_safety_claimed",
            "privacy_safety_claimed",
            "malware_safety_claimed",
            "verified_authenticity_claimed",
        ):
            mutated = copy.deepcopy(record)
            mutated["truth_boundary"][key] = True
            self.assertTrue(validator.validate_source_record("wikimedia_commons", mutated, known), key)
        errors: list[str] = []
        validator._scan_json_payload("synthetic", {"api_token": "secret"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("synthetic", {"media_payload": "not allowed"}, errors)
        self.assertTrue(errors)
        errors = []
        validator._scan_json_payload("synthetic", {"fingerprint_submission_payload": "not allowed"}, errors)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
