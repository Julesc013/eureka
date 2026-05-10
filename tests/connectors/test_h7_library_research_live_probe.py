import copy
import importlib
from unittest import mock
import unittest

from runtime.connectors.h7_library_research.live_probe_common import (
    H7_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h7_library_research_live_probe_request,
    build_h7_library_research_live_probe_result,
    detect_h7_library_research_live_probe_product_boundary_violations,
    detect_h7_library_research_live_probe_truth_boundary_violations,
    load_h7_library_research_live_probe_policy_bundle,
    validate_h7_library_research_live_probe_request,
)
from scripts.run_h7_library_research_live_probe import run_probe


class H7LibraryResearchLiveProbeTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_h7_library_research_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self):
        request = build_h7_library_research_live_probe_request("openalex", "example_work_metadata", self.bundle, live_requested=True)
        result = validate_h7_library_research_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn(result["result_status"], {"blocked_by_missing_approval", "blocked_by_endpoint_policy", "blocked_by_kill_switch", "blocked_by_harvest_policy"})

    def test_source_not_in_allowlist_blocks_live_call(self):
        request = {"source_id": "not_h7", "approved_request_key": "x", "endpoint_or_metadata_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h7_library_research_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h7", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self):
        bundle = self._approved_bundle("openalex")
        request = build_h7_library_research_live_probe_request("openalex", "example_work_metadata", bundle, live_requested=True)
        self._source(bundle, "allowed_requests", "openalex")["allowed_request_keys"] = []
        result = validate_h7_library_research_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self):
        bundle = self._approved_bundle("openalex")
        request = build_h7_library_research_live_probe_request("openalex", "example_work_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "openalex")["default_enabled"] = False
        result = validate_h7_library_research_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self):
        bundle = self._approved_bundle("openalex")
        request = build_h7_library_research_live_probe_request("openalex", "example_work_metadata", bundle, live_requested=True)
        request["endpoint_or_metadata_class"] = "patent_document_download_forbidden_current"
        result = validate_h7_library_research_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_harvest_api_fetch_download_sensitive_bypass_attempts_are_rejected(self):
        bundle = self._approved_bundle("openalex")
        request = build_h7_library_research_live_probe_request("openalex", "example_work_metadata", bundle, live_requested=True)
        for key in (
            "oai_pmh_harvest_requested",
            "api_query_requested",
            "full_text_fetch_requested",
            "pdf_download_requested",
            "book_scan_download_requested",
            "article_download_requested",
            "dataset_download_requested",
            "patent_document_download_requested",
            "iiif_manifest_fetch_requested",
            "media_download_requested",
            "scraping_or_crawling_requested",
            "restricted_source_requested",
            "bypass_or_automation_requested",
        ):
            with self.subTest(key=key):
                candidate = dict(request)
                candidate[key] = True
                self.assertFalse(validate_h7_library_research_live_probe_request(candidate, bundle)["approved"])

    def test_dry_preflight_does_not_call_network(self):
        request = build_h7_library_research_live_probe_request("openalex", "example_work_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self):
        approved = self._approved_all_bundle()
        for source_id in H7_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                result = build_h7_library_research_live_probe_result(source_id, self._payload(source_id), {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])
                self.assertFalse(result["truth_boundary"]["bibliographic_identity_candidate_is_truth"])
                self.assertFalse(result["truth_boundary"]["citation_relation_candidate_is_truth"])

    def test_source_modules_normalize_payloads(self):
        for source_id in H7_SOURCE_IDS:
            module = importlib.import_module(f"runtime.connectors.h7_library_research.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def test_candidate_boundaries(self):
        result = build_h7_library_research_live_probe_result("openalex", self._payload("openalex"), {"request_key": "example_work_metadata"}, self._approved_bundle("openalex"))
        self.assertFalse(result["bibliographic_identity_candidate"]["truth_boundary"]["bibliographic_identity_candidate_is_truth"])
        self.assertFalse(result["research_work_identity_candidate"]["truth_boundary"]["research_work_candidate_is_truth"])
        self.assertFalse(result["dataset_identity_candidate"]["truth_boundary"]["dataset_identity_candidate_is_truth"])
        self.assertFalse(result["cultural_object_identity_candidate"]["truth_boundary"]["cultural_object_candidate_is_truth"])
        self.assertFalse(result["patent_identity_candidate"]["truth_boundary"]["patent_identity_candidate_is_truth"])
        self.assertFalse(result["citation_relation_candidate"][0]["truth_boundary"]["citation_relation_candidate_is_truth"])
        self.assertFalse(result["access_rights_availability_candidate"]["truth_boundary"]["access_metadata_is_rights_truth"])
        self.assertFalse(result["source_cache_candidate_preview"]["truth_boundary"]["source_cache_preview_is_accepted_source"])
        self.assertFalse(result["evidence_candidate_preview"]["truth_boundary"]["evidence_preview_is_accepted_evidence"])
        self.assertFalse(result["review_queue_seed_preview"]["review_seed_is_review_decision"])

    def test_public_master_rights_privacy_malware_availability_claims_are_rejected(self):
        record = {
            "truth_boundary": {
                "public_index_mutated": True,
                "master_index_mutated": True,
                "rights_clearance_claimed": True,
                "open_access_metadata_is_rights_clearance": True,
                "privacy_safety_claimed": True,
                "malware_safety_claimed": True,
                "verified_availability_claimed": True,
            }
        }
        self.assertGreaterEqual(len(detect_h7_library_research_live_probe_truth_boundary_violations(record)), 7)
        self.assertTrue(detect_h7_library_research_live_probe_product_boundary_violations({"product_boundary": {"mutated_master_index": True}}))

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H7_SOURCE_IDS:
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
            "title": f"{source_id} metadata title",
            "creators": ["Eureka Synthetic Author"],
            "contributors": ["Eureka Synthetic Contributor"],
            "publisher_or_institution": cfg["label"],
            "publication_or_creation_date": "2026-05-11",
            "language": "en",
            "format_or_medium": "metadata_record",
            "identifiers": [{"scheme": "fixture", "value": f"{source_id}:probe"}],
            "doi_candidate": f"10.5555/{source_id}.probe",
            "isbn_candidate": "9780000000000",
            "openalex_id_candidate": "W123",
            "dataset_id_candidate": f"dataset:{source_id}",
            "patent_number_candidate": f"{source_id.upper()}-0001",
            "citation_or_relation_summary": "candidate relation only",
            "relations": [{"relation_kind": "related_work", "target_ref": f"{source_id}:related"}],
            "access_rights_availability_summary": "candidate access metadata only",
            "license_metadata_candidate": "unknown",
            "landing_page_candidate": f"fixture://h7/{source_id}",
            "access": {"download_permission_current": False},
            "source_metadata": {"mocked_response": True},
        }


if __name__ == "__main__":
    unittest.main()
