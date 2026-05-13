import copy
import importlib
from unittest import mock
import unittest

from control.prototypes.legacy_runtime.connectors.h1_metadata_wave.live_probe_common import (
    H1_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h1_live_probe_request,
    build_h1_live_probe_result,
    detect_h1_live_probe_product_boundary_violations,
    detect_h1_live_probe_truth_boundary_violations,
    load_h1_live_probe_policy_bundle,
    validate_h1_live_probe_request,
)
from scripts.run_h1_metadata_live_probe import run_probe


class H1MetadataLiveProbeTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_h1_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self):
        request = build_h1_live_probe_request("pypi", "example_project_metadata", self.bundle, live_requested=True)
        result = validate_h1_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_missing_approval")

    def test_source_not_in_allowlist_blocks_live_call(self):
        request = {"source_id": "not_h1", "approved_request_key": "x", "endpoint_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h1_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h1", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self):
        bundle = self._approved_bundle("pypi")
        request = build_h1_live_probe_request("pypi", "example_project_metadata", bundle, live_requested=True)
        source = self._source(bundle, "allowed_requests", "pypi")
        source["allowed_request_keys"] = []
        result = validate_h1_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self):
        bundle = self._approved_bundle("pypi")
        request = build_h1_live_probe_request("pypi", "example_project_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "pypi")["default_enabled"] = False
        result = validate_h1_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self):
        bundle = self._approved_bundle("pypi")
        request = build_h1_live_probe_request("pypi", "example_project_metadata", bundle, live_requested=True)
        request["endpoint_class"] = "distribution_file_download_forbidden_current"
        result = validate_h1_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_endpoint_policy")

    def test_dry_preflight_does_not_call_network(self):
        request = build_h1_live_probe_request("pypi", "example_project_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self):
        approved = self._approved_all_bundle()
        for source_id in H1_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                payload = self._payload(source_id)
                result = build_h1_live_probe_result(source_id, payload, {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])

    def test_source_cache_preview_remains_candidate_only(self):
        result = build_h1_live_probe_result("pypi", self._payload("pypi"), {"request_key": "example_project_metadata"}, self._approved_bundle("pypi"))
        preview = result["source_cache_candidate_preview"]
        self.assertFalse(preview["truth_boundary"]["source_cache_preview_is_accepted_source"])
        self.assertFalse(preview["source_cache_write_enabled"])

    def test_evidence_preview_remains_candidate_only(self):
        result = build_h1_live_probe_result("osv", self._payload("osv"), {"request_key": "example_vulnerability_metadata"}, self._approved_bundle("osv"))
        preview = result["evidence_candidate_preview"]
        self.assertFalse(preview["truth_boundary"]["evidence_preview_is_accepted_evidence"])
        self.assertFalse(preview["evidence_ledger_write_enabled"])

    def test_review_seed_is_not_decision(self):
        result = build_h1_live_probe_result("pypi", self._payload("pypi"), {"request_key": "example_project_metadata"}, self._approved_bundle("pypi"))
        seed = result["review_queue_seed_preview"]
        self.assertFalse(seed["review_queue_seed_is_review_decision"])

    def test_download_endpoint_attempt_is_rejected(self):
        bundle = self._approved_bundle("github_releases")
        request = build_h1_live_probe_request("github_releases", "example_release_metadata", bundle, live_requested=True)
        request["endpoint_class"] = "release_asset_download_forbidden_current"
        self.assertFalse(validate_h1_live_probe_request(request, bundle)["approved"])

    def test_public_index_mutation_claim_is_rejected(self):
        record = {"truth_boundary": {"public_index_mutated": True}}
        self.assertTrue(detect_h1_live_probe_truth_boundary_violations(record))

    def test_master_index_mutation_claim_is_rejected(self):
        record = {"product_boundary": {"mutated_master_index": True}}
        self.assertTrue(detect_h1_live_probe_product_boundary_violations(record))

    def test_rights_malware_installability_claims_are_rejected(self):
        record = {"truth_boundary": {"rights_clearance_claimed": True, "malware_safety_claimed": True, "verified_installability_claimed": True}}
        errors = detect_h1_live_probe_truth_boundary_violations(record)
        self.assertEqual(len(errors), 3)

    def test_source_modules_normalize_payloads(self):
        for source_id in H1_SOURCE_IDS:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h1_metadata_wave.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H1_SOURCE_IDS:
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
        endpoint = self._source(bundle, "endpoint_policy", source_id)
        endpoint["allowlisted_endpoint_classes_current"] = [cfg["endpoint_class"]]
        rate = self._source(bundle, "rate_limit_policy", source_id)
        rate["decision_status"] = "approved_for_bounded_metadata_probe"
        rate["user_agent_contact_posture"] = "not_required_documented"
        cache = self._source(bundle, "cache_policy", source_id)
        cache["decision_status"] = "approved_for_bounded_metadata_probe"
        cache["no_cache_decision"] = "approved"
        kill = self._source(bundle, "kill_switch_policy", source_id)
        kill["decision_status"] = "approved_for_bounded_metadata_probe"
        kill["default_enabled"] = True

    def _source(self, bundle, bundle_key, source_id):
        for item in bundle[bundle_key]["sources"]:
            if item["source_id"] == source_id:
                return item
        raise AssertionError(source_id)

    def _payload(self, source_id):
        cfg = SOURCE_CONFIGS[source_id]
        return {
            "native_id": cfg["native_id"],
            "title": cfg["title"],
            "description_summary": "Mocked metadata response.",
            "version_or_state": cfg["version_or_state"],
            "artifact_type": cfg["artifact_type"],
            "object_family": cfg["object_family"],
            "platform_or_context": cfg["platform_or_context"],
            "package_or_project_name": cfg["title"],
            "release_or_snapshot_id": cfg["release_or_snapshot_id"],
            "file_or_asset_summary": {"metadata_only": True, "payloads_downloaded": False},
            "identity_refs": [f"mock:h1:{source_id}"],
            "source_metadata": {"mocked": True},
        }


if __name__ == "__main__":
    unittest.main()
