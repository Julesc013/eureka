from __future__ import annotations

import copy
import importlib
import unittest

from runtime.connectors.h11_storefront.live_probe_common import (
    SOURCE_CONFIGS,
    build_h11_storefront_live_probe_blocked_result,
    build_h11_storefront_live_probe_request,
    build_h11_storefront_live_probe_result,
    detect_h11_storefront_live_probe_product_boundary_violations,
    detect_h11_storefront_live_probe_truth_boundary_violations,
    load_h11_storefront_live_probe_policy_bundle,
    validate_h11_storefront_live_probe_request,
    validate_h11_source_approval,
)


class H11StorefrontLiveProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_h11_storefront_live_probe_policy_bundle()
        self.request = build_h11_storefront_live_probe_request("fdroid_metadata", "example_app_metadata", self.bundle, live_requested=True)

    def test_policy_pending_blocks_live_calls(self) -> None:
        result = validate_h11_storefront_live_probe_request(self.request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_missing_approval")

    def test_source_not_in_allowlist_blocks_live_call(self) -> None:
        request = dict(self.request, source_id="unknown_source")
        result = validate_h11_storefront_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("known H11 storefront source", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self) -> None:
        result = validate_h11_source_approval("fdroid_metadata", "not_approved", self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("request key is not approved for this source", result["blocked_reasons"])

    def test_kill_switch_blocks_live_call_when_otherwise_approved(self) -> None:
        bundle = copy.deepcopy(self.bundle)
        source = _source(bundle, "allowed_requests", "fdroid_metadata")
        source.update({"approval_status": "approved_for_bounded_metadata_probe", "live_access_approved": True, "metadata_probe_approved": True, "allowed_request_keys": ["example_app_metadata"]})
        _source(bundle, "endpoint_policy", "fdroid_metadata")["allowlisted_endpoint_or_metadata_classes_current"] = [SOURCE_CONFIGS["fdroid_metadata"]["endpoint"]]
        _source(bundle, "rate_limit_policy", "fdroid_metadata").update({"decision_status": "approved_for_bounded_metadata_probe", "max_requests_per_run": 1, "max_requests_per_minute": 1, "user_agent_contact_posture": "approved_not_required_for_mock", "auth_posture": "approved_no_auth"})
        _source(bundle, "cache_policy", "fdroid_metadata").update({"decision_status": "approved_for_bounded_metadata_probe", "no_cache_decision": "approved"})
        result = validate_h11_source_approval("fdroid_metadata", "example_app_metadata", bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_metadata_class_blocks_live_call(self) -> None:
        request = dict(self.request, endpoint_or_metadata_class="package_download_forbidden_current")
        result = validate_h11_storefront_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_forbidden_request_flags_are_rejected(self) -> None:
        cases = {
            "storefront_search_requested": "blocked_by_missing_approval",
            "product_page_fetch_requested": "blocked_by_missing_approval",
            "screenshot_fetch_requested": "blocked_by_download_policy",
            "media_fetch_requested": "blocked_by_download_policy",
            "app_download_requested": "blocked_by_download_policy",
            "package_download_requested": "blocked_by_download_policy",
            "installer_download_requested": "blocked_by_download_policy",
            "account_access_requested": "blocked_by_account_policy",
            "credential_or_token_handling_requested": "blocked_by_account_policy",
            "receipt_license_entitlement_handling_requested": "blocked_by_entitlement_policy",
            "purchase_automation_requested": "blocked_by_purchase_policy",
            "checkout_automation_requested": "blocked_by_purchase_policy",
            "cart_wishlist_automation_requested": "blocked_by_purchase_policy",
            "redemption_subscription_requested": "blocked_by_purchase_policy",
            "install_execute_requested": "blocked_by_install_launch_policy",
            "launch_execute_requested": "blocked_by_install_launch_policy",
            "review_rating_write_requested": "blocked_by_review_write_policy",
            "scraping_or_crawling_requested": "blocked_by_missing_approval",
            "restricted_source_requested": "blocked_by_restricted_source_policy",
            "bypass_or_automation_requested": "blocked_by_bypass_policy",
        }
        for flag, status in cases.items():
            with self.subTest(flag=flag):
                request = dict(self.request, **{flag: True})
                result = validate_h11_storefront_live_probe_request(request, self.bundle)
                self.assertFalse(result["approved"])
                self.assertEqual(result["result_status"], status)

    def test_dry_preflight_blocked_result_does_not_call_network(self) -> None:
        blocked = build_h11_storefront_live_probe_blocked_result(self.request, ["missing approval"], self.bundle)
        self.assertFalse(blocked["network_used"])
        self.assertEqual(blocked["request_count"], 0)
        self.assertFalse(blocked["product_boundary"]["network_calls_made"])

    def test_mocked_response_builds_live_probe_result_for_representative_modules(self) -> None:
        payload = {"source_native_id": "org.example.app", "app_or_product_name": "Example App", "listing_title": "Example App", "package_name_candidate": "org.example.app", "version_candidate": "1.0"}
        for source_id in ("fdroid_metadata", "steam_store_metadata", "chrome_web_store_metadata"):
            with self.subTest(source_id=source_id):
                module = importlib.import_module(f"runtime.connectors.h11_storefront.live_probe_{source_id}")
                normalized = module.normalize_response_payload(payload, self.bundle)
                self.assertEqual(normalized["source_id"], source_id)
                result = build_h11_storefront_live_probe_result(source_id, payload, {"network_used": False, "result_status": "dry_run_preflight_pass"}, self.bundle)
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertFalse(result["network_used"])

    def test_candidates_and_previews_remain_non_truth(self) -> None:
        result = build_h11_storefront_live_probe_blocked_result(self.request, ["missing approval"], self.bundle)
        for key in (
            "storefront_listing_identity_candidate",
            "app_product_identity_candidate",
            "version_release_channel_candidate",
            "price_availability_region_candidate",
            "acquisition_path_candidate",
            "review_rating_metadata_candidate",
            "account_entitlement_boundary_candidate",
            "storefront_rights_safety_candidate",
            "source_cache_candidate_preview",
            "evidence_candidate_preview",
            "review_queue_seed_preview",
        ):
            self.assertIn("truth_boundary", result[key])
        self.assertFalse(detect_h11_storefront_live_probe_truth_boundary_violations(result, self.bundle))
        self.assertFalse(detect_h11_storefront_live_probe_product_boundary_violations(result, self.bundle))

    def test_truth_and_product_mutation_claims_are_rejected(self) -> None:
        result = build_h11_storefront_live_probe_blocked_result(self.request, ["missing approval"], self.bundle)
        result["truth_boundary"]["current_price_claimed"] = True
        result["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(detect_h11_storefront_live_probe_truth_boundary_violations(result, self.bundle))
        self.assertTrue(detect_h11_storefront_live_probe_product_boundary_violations(result, self.bundle))


def _source(bundle: dict, section: str, source_id: str) -> dict:
    for item in bundle[section]["sources"]:
        if item["source_id"] == source_id:
            return item
    raise AssertionError(source_id)
