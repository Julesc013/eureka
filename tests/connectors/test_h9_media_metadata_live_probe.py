from __future__ import annotations

import copy
import importlib
from unittest import mock
import unittest

from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.live_probe_common import (
    H9_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h9_media_metadata_live_probe_request,
    build_h9_media_metadata_live_probe_result,
    detect_h9_media_metadata_live_probe_product_boundary_violations,
    detect_h9_media_metadata_live_probe_truth_boundary_violations,
    load_h9_media_metadata_live_probe_policy_bundle,
    validate_h9_media_metadata_live_probe_request,
)
from scripts.run_h9_media_metadata_live_probe import run_probe


class H9MediaMetadataLiveProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_h9_media_metadata_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self) -> None:
        request = build_h9_media_metadata_live_probe_request("musicbrainz", "example_recording_metadata", self.bundle, live_requested=True)
        result = validate_h9_media_metadata_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn(result["result_status"], {"blocked_by_missing_approval", "blocked_by_endpoint_policy", "blocked_by_kill_switch", "blocked_by_download_policy"})

    def test_source_not_in_allowlist_blocks_live_call(self) -> None:
        request = {"source_id": "not_h9", "approved_request_key": "x", "endpoint_or_metadata_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h9_media_metadata_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h9", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self) -> None:
        bundle = self._approved_bundle("musicbrainz")
        request = build_h9_media_metadata_live_probe_request("musicbrainz", "example_recording_metadata", bundle, live_requested=True)
        self._source(bundle, "allowed_requests", "musicbrainz")["allowed_request_keys"] = []
        result = validate_h9_media_metadata_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self) -> None:
        bundle = self._approved_bundle("musicbrainz")
        request = build_h9_media_metadata_live_probe_request("musicbrainz", "example_recording_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "musicbrainz")["default_enabled"] = False
        result = validate_h9_media_metadata_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self) -> None:
        bundle = self._approved_bundle("musicbrainz")
        request = build_h9_media_metadata_live_probe_request("musicbrainz", "example_recording_metadata", bundle, live_requested=True)
        request["endpoint_or_metadata_class"] = "audio_download_forbidden_current"
        result = validate_h9_media_metadata_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_forbidden_requests_are_rejected(self) -> None:
        bundle = self._approved_bundle("musicbrainz")
        request = build_h9_media_metadata_live_probe_request("musicbrainz", "example_recording_metadata", bundle, live_requested=True)
        for key in (
            "api_query_requested",
            "catalog_fetch_requested",
            "media_download_requested",
            "image_download_requested",
            "video_download_requested",
            "audio_download_requested",
            "map_download_requested",
            "score_download_requested",
            "thumbnail_fetch_requested",
            "media_upload_requested",
            "fingerprint_lookup_requested",
            "fingerprint_submission_requested",
            "fingerprint_generation_requested",
            "scraping_or_crawling_requested",
            "restricted_source_requested",
            "bypass_or_automation_requested",
        ):
            with self.subTest(key=key):
                candidate = dict(request)
                candidate[key] = True
                self.assertFalse(validate_h9_media_metadata_live_probe_request(candidate, bundle)["approved"])

    def test_dry_preflight_does_not_call_network(self) -> None:
        request = build_h9_media_metadata_live_probe_request("musicbrainz", "example_recording_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self) -> None:
        approved = self._approved_all_bundle()
        for source_id in H9_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                result = build_h9_media_metadata_live_probe_result(source_id, self._payload(source_id), {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])
                self.assertFalse(result["truth_boundary"]["media_object_identity_candidate_is_truth"])
                self.assertFalse(result["truth_boundary"]["rights_license_candidate_is_rights_truth"])

    def test_source_modules_normalize_payloads(self) -> None:
        for source_id in H9_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h9_media_metadata.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def test_candidate_boundaries(self) -> None:
        result = build_h9_media_metadata_live_probe_result("musicbrainz", self._payload("musicbrainz"), {"request_key": "example_recording_metadata"}, self._approved_bundle("musicbrainz"))
        self.assertFalse(result["media_object_identity_candidate"]["truth_boundary"]["media_object_identity_candidate_is_truth"])
        self.assertFalse(result["music_work_recording_release_candidate"]["truth_boundary"]["music_identity_candidate_is_truth"])
        self.assertFalse(result["image_video_map_identity_candidate"]["truth_boundary"]["image_video_map_identity_candidate_is_truth"])
        self.assertFalse(result["media_creator_collection_relation_candidate"][0]["truth_boundary"]["creator_collection_relation_candidate_is_truth"])
        self.assertFalse(result["media_fingerprint_candidate"]["truth_boundary"]["fingerprint_match_candidate_is_truth"])
        self.assertFalse(result["media_fingerprint_candidate"]["truth_boundary"]["fingerprint_candidate_grants_upload_or_submission_permission"])
        self.assertFalse(result["media_rights_license_candidate"]["truth_boundary"]["license_metadata_is_rights_clearance"])
        self.assertFalse(result["media_rights_license_candidate"]["truth_boundary"]["public_domain_metadata_is_public_domain_truth"])
        self.assertFalse(result["media_rights_license_candidate"]["truth_boundary"]["creative_commons_metadata_is_license_truth"])
        self.assertFalse(result["media_safety_privacy_candidate"]["truth_boundary"]["safety_privacy_candidate_is_safety_truth"])
        self.assertFalse(result["source_cache_candidate_preview"]["truth_boundary"].get("source_cache_preview_is_accepted_source"))
        self.assertFalse(result["evidence_candidate_preview"]["truth_boundary"].get("evidence_preview_is_accepted_evidence"))
        self.assertFalse(result["review_queue_seed_preview"]["review_seed_is_review_decision"])

    def test_public_master_rights_safety_authenticity_claims_are_rejected(self) -> None:
        record = {"truth_boundary": {"public_index_mutated": True, "master_index_mutated": True, "rights_clearance_claimed": True, "public_domain_truth_claimed": True, "creative_commons_truth_claimed": True, "content_safety_claimed": True, "privacy_safety_claimed": True, "malware_safety_claimed": True, "verified_authenticity_claimed": True}}
        self.assertGreaterEqual(len(detect_h9_media_metadata_live_probe_truth_boundary_violations(record)), 9)
        self.assertTrue(detect_h9_media_metadata_live_probe_product_boundary_violations({"product_boundary": {"mutated_master_index": True}}))

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H9_SOURCE_IDS:
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
            "media_title": f"{source_id} metadata title",
            "media_type": "metadata_record",
            "media_format": "metadata_only",
            "catalog_record_id": f"{source_id}-catalog-record",
            "creator_or_contributor": [cfg["label"]],
            "artist_or_creator": [cfg["label"]],
            "work_title": f"{source_id} work",
            "recording_title": f"{source_id} recording",
            "release_title": f"{source_id} release",
            "visual_title": f"{source_id} visual",
            "fingerprint_metadata": {"fingerprint_id_candidate": f"{source_id}-fp", "upload_allowed_current": False},
            "rights_or_license_metadata": {"rights_statement_candidate": "candidate only", "rights_clearance_claimed": False},
            "safety_privacy_metadata": {"safety_candidate": "candidate only", "privacy_safety_claimed": False},
            "source_metadata": {"mocked_response": True},
        }


if __name__ == "__main__":
    unittest.main()
