import copy
import importlib
from unittest import mock
import unittest

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.live_probe_common import (
    H6_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h6_web_archive_live_probe_request,
    build_h6_web_archive_live_probe_result,
    detect_h6_web_archive_live_probe_product_boundary_violations,
    detect_h6_web_archive_live_probe_truth_boundary_violations,
    load_h6_web_archive_live_probe_policy_bundle,
    validate_h6_web_archive_live_probe_request,
)
from scripts.run_h6_web_archive_live_probe import run_probe


class H6WebArchiveLiveProbeTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_h6_web_archive_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self):
        request = build_h6_web_archive_live_probe_request("wayback_cdx_memento", "example_capture_metadata", self.bundle, live_requested=True)
        result = validate_h6_web_archive_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn(result["result_status"], {"blocked_by_missing_approval", "blocked_by_endpoint_policy", "blocked_by_kill_switch", "blocked_by_fetch_policy"})

    def test_source_not_in_allowlist_blocks_live_call(self):
        request = {"source_id": "not_h6", "approved_request_key": "x", "endpoint_or_metadata_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h6_web_archive_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h6", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self):
        bundle = self._approved_bundle("wayback_cdx_memento")
        request = build_h6_web_archive_live_probe_request("wayback_cdx_memento", "example_capture_metadata", bundle, live_requested=True)
        self._source(bundle, "allowed_requests", "wayback_cdx_memento")["allowed_request_keys"] = []
        result = validate_h6_web_archive_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self):
        bundle = self._approved_bundle("wayback_cdx_memento")
        request = build_h6_web_archive_live_probe_request("wayback_cdx_memento", "example_capture_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "wayback_cdx_memento")["default_enabled"] = False
        result = validate_h6_web_archive_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self):
        bundle = self._approved_bundle("wayback_cdx_memento")
        request = build_h6_web_archive_live_probe_request("wayback_cdx_memento", "example_capture_metadata", bundle, live_requested=True)
        request["endpoint_or_metadata_class"] = "archived_page_fetch_forbidden_current"
        result = validate_h6_web_archive_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_fetch_policy")

    def test_fetch_crawl_sensitive_bypass_attempts_are_rejected(self):
        bundle = self._approved_bundle("wayback_cdx_memento")
        request = build_h6_web_archive_live_probe_request("wayback_cdx_memento", "example_capture_metadata", bundle, live_requested=True)
        for key in (
            "warc_wacz_fetch_requested",
            "archived_page_fetch_requested",
            "live_page_fetch_requested",
            "media_download_requested",
            "transcript_download_requested",
            "public_document_fetch_requested",
            "scraping_or_crawling_requested",
            "restricted_sensitive_source_requested",
            "bypass_or_automation_requested",
        ):
            with self.subTest(key=key):
                candidate = dict(request)
                candidate[key] = True
                self.assertFalse(validate_h6_web_archive_live_probe_request(candidate, bundle)["approved"])

    def test_dry_preflight_does_not_call_network(self):
        request = build_h6_web_archive_live_probe_request("wayback_cdx_memento", "example_capture_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self):
        approved = self._approved_all_bundle()
        for source_id in H6_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                result = build_h6_web_archive_live_probe_result(source_id, self._payload(source_id), {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])
                self.assertFalse(result["truth_boundary"]["web_capture_candidate_is_truth"])
                self.assertFalse(result["truth_boundary"]["news_event_mention_candidate_is_event_truth"])

    def test_source_modules_normalize_payloads(self):
        for source_id in H6_SOURCE_IDS:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def test_candidate_boundaries(self):
        result = build_h6_web_archive_live_probe_result("wayback_cdx_memento", self._payload("wayback_cdx_memento"), {"request_key": "example_capture_metadata"}, self._approved_bundle("wayback_cdx_memento"))
        self.assertFalse(result["web_capture_identity_candidate"]["truth_boundary"]["web_capture_identity_candidate_is_accepted_capture_truth"])
        self.assertFalse(result["archived_url_time_state_candidate"]["truth_boundary"]["archived_time_state_candidate_is_historical_truth"])
        self.assertFalse(result["dead_link_trace_candidate"]["truth_boundary"]["dead_link_trace_grants_acquisition_permission"])
        self.assertFalse(result["source_cache_candidate_preview"]["truth_boundary"]["source_cache_preview_is_accepted_source"])
        self.assertFalse(result["evidence_candidate_preview"]["truth_boundary"]["evidence_preview_is_accepted_evidence"])
        self.assertFalse(result["review_queue_seed_preview"]["review_seed_is_review_decision"])

    def test_public_document_and_media_boundaries(self):
        public_result = build_h6_web_archive_live_probe_result("restricted_public_document_manifest", self._payload("restricted_public_document_manifest"), {"request_key": "example_manifest_metadata"}, self._approved_bundle("restricted_public_document_manifest"))
        self.assertFalse(public_result["public_document_trace_candidate"]["direct_fetch_allowed_current"])
        self.assertFalse(public_result["public_document_trace_candidate"]["truth_boundary"]["public_document_trace_is_public_truth"])
        media_result = build_h6_web_archive_live_probe_result("cspan_video_library", self._payload("cspan_video_library"), {"request_key": "example_video_event_metadata"}, self._approved_bundle("cspan_video_library"))
        self.assertFalse(media_result["media_transcript_metadata_candidate"]["download_allowed_current"])
        self.assertFalse(media_result["media_transcript_metadata_candidate"]["truth_boundary"]["transcript_metadata_proves_full_context"])

    def test_public_master_rights_privacy_malware_authenticity_claims_are_rejected(self):
        record = {
            "truth_boundary": {
                "public_index_mutated": True,
                "master_index_mutated": True,
                "rights_clearance_claimed": True,
                "privacy_safety_claimed": True,
                "malware_safety_claimed": True,
                "verified_authenticity_claimed": True,
            }
        }
        self.assertEqual(len(detect_h6_web_archive_live_probe_truth_boundary_violations(record)), 6)
        self.assertTrue(detect_h6_web_archive_live_probe_product_boundary_violations({"product_boundary": {"mutated_master_index": True}}))

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H6_SOURCE_IDS:
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
        endpoint["allowlisted_endpoint_or_metadata_classes_current"] = [cfg["endpoint_or_metadata_class"]]
        rate = self._source(bundle, "rate_limit_policy", source_id)
        rate["decision_status"] = "approved_for_bounded_metadata_probe"
        rate["max_requests_per_run"] = 1
        rate["max_requests_per_minute"] = 1
        rate["request_budget"] = 1
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
            "original_url": f"https://example.invalid/h6/{source_id}/resource",
            "normalized_url_candidate": f"https://example.invalid/h6/{source_id}/resource",
            "capture_url": f"fixture:h6:{source_id}:capture",
            "capture_timestamp": "20260510000000",
            "memento_datetime": "Sun, 10 May 2026 00:00:00 GMT",
            "capture_status_code": "200",
            "capture_mime_type": "text/html",
            "capture_digest": "sha256:candidate-only",
            "collection_id": "mock-collection",
            "article_or_record_id": f"{source_id}-article",
            "headline_or_title": f"{source_id} metadata headline",
            "publication_or_program": cfg["label"],
            "publication_date": "2026-05-10",
            "event_date_candidate": "2026-05-10",
            "mentioned_entity": "Eureka fixture entity",
            "mentioned_url": f"fixture:h6:{source_id}:mention",
            "dead_url_candidate": f"https://example.invalid/h6/{source_id}/dead",
            "archived_snapshot_candidate": f"fixture:h6:{source_id}:snapshot",
            "document_collection_ref": "restricted_public_document_manifest",
            "document_record_id": f"{source_id}-document",
            "document_title": "manifest only candidate",
            "media_or_program_id": f"{source_id}-media",
            "media_title": "metadata-only media candidate",
            "transcript_or_caption_ref": "not-fetched-current",
            "media_ref": "not-fetched-current",
            "source_metadata": {"mocked_response": True},
        }


if __name__ == "__main__":
    unittest.main()
