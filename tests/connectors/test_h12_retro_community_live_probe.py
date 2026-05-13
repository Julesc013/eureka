from __future__ import annotations

import copy
import importlib
import unittest

from control.prototypes.legacy_runtime.connectors.h12_retro_community.live_probe_common import (
    SOURCE_CONFIGS,
    build_h12_retro_community_live_probe_blocked_result,
    build_h12_retro_community_live_probe_request,
    build_h12_retro_community_live_probe_result,
    detect_h12_retro_community_live_probe_product_boundary_violations,
    detect_h12_retro_community_live_probe_truth_boundary_violations,
    load_h12_retro_community_live_probe_policy_bundle,
    validate_h12_retro_community_live_probe_request,
    validate_h12_source_approval,
)


class H12RetroCommunityLiveProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_h12_retro_community_live_probe_policy_bundle()
        self.request = build_h12_retro_community_live_probe_request("winworld_metadata", "example_catalog_item_metadata", self.bundle, live_requested=True)

    def test_policy_pending_blocks_live_calls(self) -> None:
        result = validate_h12_retro_community_live_probe_request(self.request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_missing_approval")

    def test_source_not_in_allowlist_blocks_live_call(self) -> None:
        request = dict(self.request, source_id="unknown_source")
        result = validate_h12_retro_community_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("known H12 retro/community source", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self) -> None:
        result = validate_h12_source_approval("winworld_metadata", "not_approved", self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("request key is not approved for this source", result["blocked_reasons"])

    def test_kill_switch_blocks_live_call_when_otherwise_approved(self) -> None:
        bundle = copy.deepcopy(self.bundle)
        source = _source(bundle, "allowed_requests", "winworld_metadata")
        source.update({"approval_status": "approved_for_bounded_metadata_probe", "live_access_approved": True, "metadata_probe_approved": True, "allowed_request_keys": ["example_catalog_item_metadata"]})
        _source(bundle, "endpoint_policy", "winworld_metadata")["allowlisted_endpoint_or_metadata_classes_current"] = [SOURCE_CONFIGS["winworld_metadata"]["endpoint"]]
        _source(bundle, "rate_limit_policy", "winworld_metadata").update({"decision_status": "approved_for_bounded_metadata_probe", "max_requests_per_run": 1, "max_requests_per_minute": 1, "request_budget": 1, "user_agent_contact_posture": "approved_not_required_for_mock", "auth_posture": "approved_no_auth"})
        _source(bundle, "cache_policy", "winworld_metadata").update({"decision_status": "approved_for_bounded_metadata_probe", "no_cache_decision": "approved"})
        result = validate_h12_source_approval("winworld_metadata", "example_catalog_item_metadata", bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_metadata_class_blocks_live_call(self) -> None:
        request = dict(self.request, endpoint_or_metadata_class="rom_download_forbidden_current")
        result = validate_h12_retro_community_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_forbidden_request_flags_are_rejected(self) -> None:
        cases = {
            "api_query_requested": "blocked_by_missing_approval",
            "catalog_fetch_requested": "blocked_by_missing_approval",
            "html_catalog_fetch_requested": "blocked_by_missing_approval",
            "forum_or_comment_fetch_requested": "blocked_by_missing_approval",
            "web_archive_trace_fetch_requested": "blocked_by_missing_approval",
            "gated_source_access_requested": "blocked_by_gated_source_policy",
            "account_access_requested": "blocked_by_gated_source_policy",
            "download_requested": "blocked_by_download_policy",
            "software_binary_download_requested": "blocked_by_download_policy",
            "rom_download_requested": "blocked_by_download_policy",
            "iso_download_requested": "blocked_by_download_policy",
            "disc_image_download_requested": "blocked_by_download_policy",
            "bios_firmware_download_requested": "blocked_by_download_policy",
            "driver_download_requested": "blocked_by_download_policy",
            "installer_download_requested": "blocked_by_download_policy",
            "patch_download_requested": "blocked_by_download_policy",
            "crack_key_serial_handling_requested": "blocked_by_download_policy",
            "archive_download_requested": "blocked_by_download_policy",
            "extraction_requested": "blocked_by_extraction_policy",
            "execution_requested": "blocked_by_execution_policy",
            "acquisition_action_requested": "blocked_by_acquisition_policy",
            "file_upload_requested": "blocked_by_upload_policy",
            "hash_submission_requested": "blocked_by_upload_policy",
            "scraping_or_crawling_requested": "blocked_by_bypass_policy",
            "restricted_source_requested": "blocked_by_restricted_source_policy",
            "bypass_or_automation_requested": "blocked_by_bypass_policy",
        }
        for flag, status in cases.items():
            with self.subTest(flag=flag):
                request = dict(self.request, **{flag: True})
                result = validate_h12_retro_community_live_probe_request(request, self.bundle)
                self.assertFalse(result["approved"])
                self.assertEqual(result["result_status"], status)

    def test_dry_preflight_blocked_result_does_not_call_network(self) -> None:
        blocked = build_h12_retro_community_live_probe_blocked_result(self.request, ["missing approval"], self.bundle)
        self.assertFalse(blocked["network_used"])
        self.assertEqual(blocked["request_count"], 0)
        self.assertFalse(blocked["product_boundary"]["network_calls_made"])

    def test_mocked_response_builds_live_probe_result_for_representative_modules(self) -> None:
        payload = {"source_native_id": "mock-item", "software_title": "Mock Retro Item", "platform": "DOS", "version_candidate": "1.0"}
        for source_id in ("winworld_metadata", "aminet_metadata", "betaarchive_public_metadata_policy_limited"):
            with self.subTest(source_id=source_id):
                module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h12_retro_community.live_probe_{source_id}")
                normalized = module.normalize_response_payload(payload, self.bundle)
                self.assertEqual(normalized["source_id"], source_id)
                result = build_h12_retro_community_live_probe_result(source_id, payload, {"network_used": False, "result_status": "dry_run_preflight_pass"}, self.bundle)
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertFalse(result["network_used"])

    def test_candidates_and_previews_remain_non_truth(self) -> None:
        result = build_h12_retro_community_live_probe_blocked_result(self.request, ["missing approval"], self.bundle)
        for key in (
            "retro_software_identity_candidate",
            "platform_version_edition_candidate",
            "archive_item_member_candidate",
            "compatibility_install_note_candidate",
            "community_review_comment_candidate",
            "hash_checksum_candidate",
            "ia_wayback_corroboration_candidate",
            "gated_source_boundary_candidate",
            "retro_rights_safety_candidate",
            "source_cache_candidate_preview",
            "evidence_candidate_preview",
            "review_queue_seed_preview",
        ):
            self.assertIn("truth_boundary", result[key])
        self.assertFalse(detect_h12_retro_community_live_probe_truth_boundary_violations(result, self.bundle))
        self.assertFalse(detect_h12_retro_community_live_probe_product_boundary_violations(result, self.bundle))

    def test_truth_and_product_mutation_claims_are_rejected(self) -> None:
        result = build_h12_retro_community_live_probe_blocked_result(self.request, ["missing approval"], self.bundle)
        result["truth_boundary"]["legal_acquisition_claimed"] = True
        result["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(detect_h12_retro_community_live_probe_truth_boundary_violations(result, self.bundle))
        self.assertTrue(detect_h12_retro_community_live_probe_product_boundary_violations(result, self.bundle))


def _source(bundle: dict, section: str, source_id: str) -> dict:
    for item in bundle[section]["sources"]:
        if item["source_id"] == source_id:
            return item
    raise AssertionError(source_id)
