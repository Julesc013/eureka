from __future__ import annotations

import copy
import importlib
from unittest import mock
import unittest

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.live_probe_common import (
    H10_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h10_games_emulation_live_probe_request,
    build_h10_games_emulation_live_probe_result,
    detect_h10_games_emulation_live_probe_product_boundary_violations,
    detect_h10_games_emulation_live_probe_truth_boundary_violations,
    load_h10_games_emulation_live_probe_policy_bundle,
    validate_h10_games_emulation_live_probe_request,
)
from scripts.run_h10_games_emulation_live_probe import run_probe


class H10GamesEmulationLiveProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_h10_games_emulation_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self) -> None:
        request = build_h10_games_emulation_live_probe_request("mobygames", "example_game_metadata", self.bundle, live_requested=True)
        result = validate_h10_games_emulation_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn(result["result_status"], {"blocked_by_missing_approval", "blocked_by_endpoint_policy", "blocked_by_kill_switch"})

    def test_source_not_in_allowlist_blocks_live_call(self) -> None:
        request = {"source_id": "not_h10", "approved_request_key": "x", "endpoint_or_metadata_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h10_games_emulation_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h10", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self) -> None:
        bundle = self._approved_bundle("mobygames")
        request = build_h10_games_emulation_live_probe_request("mobygames", "example_game_metadata", bundle, live_requested=True)
        self._source(bundle, "allowed_requests", "mobygames")["allowed_request_keys"] = []
        result = validate_h10_games_emulation_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self) -> None:
        bundle = self._approved_bundle("mobygames")
        request = build_h10_games_emulation_live_probe_request("mobygames", "example_game_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "mobygames")["default_enabled"] = False
        result = validate_h10_games_emulation_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self) -> None:
        bundle = self._approved_bundle("mobygames")
        request = build_h10_games_emulation_live_probe_request("mobygames", "example_game_metadata", bundle, live_requested=True)
        request["endpoint_or_metadata_class"] = "ROM_download_forbidden_current"
        result = validate_h10_games_emulation_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_forbidden_requests_are_rejected(self) -> None:
        bundle = self._approved_bundle("mobygames")
        request = build_h10_games_emulation_live_probe_request("mobygames", "example_game_metadata", bundle, live_requested=True)
        for key in (
            "api_query_requested",
            "catalog_fetch_requested",
            "software_list_fetch_requested",
            "hashset_fetch_requested",
            "rom_download_requested",
            "iso_download_requested",
            "disc_image_download_requested",
            "chd_download_requested",
            "bios_firmware_download_requested",
            "game_binary_download_requested",
            "emulator_download_requested",
            "installer_download_requested",
            "patch_download_requested",
            "asset_download_requested",
            "file_upload_requested",
            "hash_submission_requested",
            "emulator_execution_requested",
            "game_execution_requested",
            "install_execute_requested",
            "acquisition_action_requested",
            "scraping_or_crawling_requested",
            "restricted_source_requested",
            "bypass_or_automation_requested",
        ):
            with self.subTest(key=key):
                candidate = dict(request)
                candidate[key] = True
                self.assertFalse(validate_h10_games_emulation_live_probe_request(candidate, bundle)["approved"])

    def test_dry_preflight_does_not_call_network(self) -> None:
        request = build_h10_games_emulation_live_probe_request("mobygames", "example_game_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self) -> None:
        approved = self._approved_all_bundle()
        for source_id in H10_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                result = build_h10_games_emulation_live_probe_result(source_id, self._payload(source_id), {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])
                self.assertFalse(result["truth_boundary"]["game_software_identity_candidate_is_truth"])
                self.assertFalse(result["truth_boundary"]["rights_safety_candidate_is_rights_or_safety_truth"])

    def test_source_modules_normalize_payloads(self) -> None:
        for source_id in H10_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h10_games_emulation.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def test_candidate_boundaries(self) -> None:
        result = build_h10_games_emulation_live_probe_result("mobygames", self._payload("mobygames"), {"request_key": "example_game_metadata"}, self._approved_bundle("mobygames"))
        self.assertFalse(result["game_software_identity_candidate"]["truth_boundary"]["game_software_identity_candidate_is_truth"])
        self.assertFalse(result["platform_release_edition_candidate"]["truth_boundary"]["platform_release_edition_candidate_is_truth"])
        self.assertFalse(result["emulator_compatibility_candidate"]["truth_boundary"]["emulator_compatibility_candidate_is_truth"])
        self.assertFalse(result["emulator_compatibility_candidate"]["truth_boundary"]["compatibility_metadata_proves_playability"])
        self.assertFalse(result["preservation_hashset_candidate"]["truth_boundary"]["preservation_hashset_candidate_is_truth"])
        self.assertFalse(result["preservation_hashset_candidate"]["truth_boundary"]["hash_metadata_proves_authenticity"])
        self.assertFalse(result["rom_disc_media_identity_candidate"]["truth_boundary"]["rom_disc_media_identity_candidate_is_truth"])
        self.assertFalse(result["rom_disc_media_identity_candidate"]["truth_boundary"]["media_identity_grants_download_permission"])
        self.assertFalse(result["game_relation_candidate"][0]["truth_boundary"]["game_relation_candidate_is_truth"])
        self.assertFalse(result["emulator_action_candidate"]["truth_boundary"]["emulator_action_candidate_is_action_permission"])
        self.assertFalse(result["games_rights_safety_candidate"]["truth_boundary"]["rights_safety_candidate_is_rights_or_safety_truth"])
        self.assertFalse(result["games_rights_safety_candidate"]["truth_boundary"]["storefront_metadata_grants_acquisition_permission"])
        self.assertFalse(result["source_cache_candidate_preview"]["truth_boundary"].get("source_cache_preview_is_accepted_source"))
        self.assertFalse(result["evidence_candidate_preview"]["truth_boundary"].get("evidence_preview_is_accepted_evidence"))
        self.assertFalse(result["review_queue_seed_preview"]["review_seed_is_review_decision"])

    def test_public_master_rights_safety_authenticity_claims_are_rejected(self) -> None:
        record = {"truth_boundary": {"public_index_mutated": True, "master_index_mutated": True, "rights_clearance_claimed": True, "legal_acquisition_claimed": True, "rom_authenticity_claimed": True, "disc_authenticity_claimed": True, "compatibility_correctness_claimed": True, "playability_claimed": True, "malware_safety_claimed": True, "content_safety_claimed": True, "privacy_safety_claimed": True, "verified_authenticity_claimed": True}}
        self.assertGreaterEqual(len(detect_h10_games_emulation_live_probe_truth_boundary_violations(record)), 12)
        self.assertTrue(detect_h10_games_emulation_live_probe_product_boundary_violations({"product_boundary": {"mutated_master_index": True}}))

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H10_SOURCE_IDS:
            self._approve_source(bundle, source_id)
        return bundle

    def _approved_bundle(self, source_id):
        bundle = copy.deepcopy(self.bundle)
        self._approve_source(bundle, source_id)
        return bundle

    def _approve_source(self, bundle, source_id):
        cfg = SOURCE_CONFIGS[source_id]
        allowed = self._source(bundle, "allowed_requests", source_id)
        allowed["approval_status"] = "approved_for_bounded_metadata_probe"
        allowed["live_access_approved"] = True
        allowed["metadata_probe_approved"] = True
        allowed["allowed_request_keys"] = [cfg["request_key"]]
        allowed["max_requests_current"] = 1
        endpoint = self._source(bundle, "endpoint_policy", source_id)
        endpoint["allowlisted_endpoint_or_metadata_classes_current"] = [cfg["endpoint"]]
        rate = self._source(bundle, "rate_limit_policy", source_id)
        rate["decision_status"] = "approved_for_bounded_metadata_probe"
        rate["max_requests_per_run"] = 1
        rate["max_requests_per_minute"] = 1
        rate["user_agent_contact_posture"] = "approved_not_required_documented"
        rate["auth_posture"] = "approved_public_no_auth"
        cache = self._source(bundle, "cache_policy", source_id)
        cache["decision_status"] = "approved_for_bounded_metadata_probe"
        cache["no_cache_decision"] = "approved"
        kill = self._source(bundle, "kill_switch_policy", source_id)
        kill["decision_status"] = "approved_for_bounded_metadata_probe"
        kill["default_enabled"] = True
        kill["live_probe_kill_switch_engaged"] = False

    def _source(self, bundle, bundle_key, source_id):
        for item in bundle[bundle_key]["sources"]:
            if item["source_id"] == source_id:
                return item
        raise AssertionError(source_id)

    def _payload(self, source_id):
        cfg = SOURCE_CONFIGS[source_id]
        return {
            "source_record_kind": cfg["source_record_kind"],
            "source_native_id": f"{source_id}-mock-live-probe",
            "game_title": f"{source_id} metadata title",
            "developer": cfg["label"],
            "publisher": cfg["label"],
            "platform": "metadata-only-platform",
            "release_title": f"{source_id} release",
            "emulator_or_runtime": "metadata-only-runtime",
            "compatibility_status_candidate": "candidate_only",
            "hashset_name": "metadata-only-hashset",
            "hash_algorithm": "sha256-candidate",
            "hash_value_candidate": "candidate-only-not-authenticity-proof",
            "file_name_candidate": "metadata-only-file",
            "rights_safety_metadata": {"rights_statement_candidate": "candidate only", "rights_clearance_claimed": False, "legal_acquisition_claimed": False},
            "source_metadata": {"mocked_response": True},
        }


if __name__ == "__main__":
    unittest.main()
