import copy
import importlib
from unittest import mock
import unittest

from archive.prototypes.legacy_runtime.connectors.h2_package_registries.live_probe_common import (
    H2_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h2_package_live_probe_request,
    build_h2_package_live_probe_result,
    detect_h2_package_live_probe_product_boundary_violations,
    detect_h2_package_live_probe_truth_boundary_violations,
    load_h2_package_live_probe_policy_bundle,
    validate_h2_package_live_probe_request,
)
from scripts.run_h2_package_live_probe import run_probe


class H2PackageLiveProbeTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_h2_package_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self):
        request = build_h2_package_live_probe_request("crates_io", "example_package_metadata", self.bundle, live_requested=True)
        result = validate_h2_package_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn(result["result_status"], {"blocked_by_missing_approval", "blocked_by_endpoint_policy", "blocked_by_kill_switch"})

    def test_source_not_in_allowlist_blocks_live_call(self):
        request = {"source_id": "not_h2", "approved_request_key": "x", "endpoint_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h2_package_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h2", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self):
        bundle = self._approved_bundle("crates_io")
        request = build_h2_package_live_probe_request("crates_io", "example_package_metadata", bundle, live_requested=True)
        self._source(bundle, "allowed_requests", "crates_io")["allowed_request_keys"] = []
        result = validate_h2_package_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self):
        bundle = self._approved_bundle("crates_io")
        request = build_h2_package_live_probe_request("crates_io", "example_package_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "crates_io")["default_enabled"] = False
        result = validate_h2_package_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self):
        bundle = self._approved_bundle("crates_io")
        request = build_h2_package_live_probe_request("crates_io", "example_package_metadata", bundle, live_requested=True)
        request["endpoint_class"] = "crate_download_forbidden_current"
        result = validate_h2_package_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_dry_preflight_does_not_call_network(self):
        request = build_h2_package_live_probe_request("crates_io", "example_package_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self):
        approved = self._approved_all_bundle()
        for source_id in H2_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                payload = self._payload(source_id)
                result = build_h2_package_live_probe_result(source_id, payload, {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])
                self.assertFalse(result["truth_boundary"]["package_identity_candidate_is_truth"])

    def test_source_modules_normalize_payloads(self):
        for source_id in H2_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h2_package_registries.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def test_package_identity_candidate_remains_candidate_only(self):
        result = build_h2_package_live_probe_result("crates_io", self._payload("crates_io"), {"request_key": "example_package_metadata"}, self._approved_bundle("crates_io"))
        identity = result["package_identity_candidate"]
        self.assertFalse(identity["truth_boundary"]["identity_candidate_is_accepted_identity"])
        self.assertFalse(identity["truth_boundary"]["purl_candidate_is_truth"])

    def test_dependency_candidate_does_not_prove_correctness(self):
        result = build_h2_package_live_probe_result("maven_central", self._payload("maven_central"), {"request_key": "example_package_metadata"}, self._approved_bundle("maven_central"))
        dependency = result["dependency_candidate_preview"][0]
        self.assertFalse(dependency["truth_boundary"]["dependency_candidate_is_correctness_proof"])

    def test_file_hash_candidate_does_not_grant_download_or_safety(self):
        result = build_h2_package_live_probe_result("nuget", self._payload("nuget"), {"request_key": "example_package_metadata"}, self._approved_bundle("nuget"))
        file_candidate = result["package_file_candidate_preview"][0]
        self.assertFalse(file_candidate["download_allowed_current"])
        self.assertFalse(file_candidate["truth_boundary"]["file_hash_candidate_is_malware_safety"])

    def test_source_cache_and_evidence_previews_remain_candidates(self):
        result = build_h2_package_live_probe_result("rubygems", self._payload("rubygems"), {"request_key": "example_package_metadata"}, self._approved_bundle("rubygems"))
        self.assertFalse(result["source_cache_candidate_preview"]["truth_boundary"]["source_cache_preview_is_accepted_source"])
        self.assertFalse(result["evidence_candidate_preview"]["truth_boundary"]["evidence_preview_is_accepted_evidence"])

    def test_review_seed_is_not_decision(self):
        result = build_h2_package_live_probe_result("cran", self._payload("cran"), {"request_key": "example_package_metadata"}, self._approved_bundle("cran"))
        self.assertFalse(result["review_queue_seed_preview"]["review_queue_seed_is_review_decision"])

    def test_package_download_attempt_is_rejected(self):
        bundle = self._approved_bundle("crates_io")
        request = build_h2_package_live_probe_request("crates_io", "example_package_metadata", bundle, live_requested=True)
        request["package_download_requested"] = True
        self.assertFalse(validate_h2_package_live_probe_request(request, bundle)["approved"])

    def test_package_manager_invocation_attempt_is_rejected(self):
        bundle = self._approved_bundle("rubygems")
        request = build_h2_package_live_probe_request("rubygems", "example_package_metadata", bundle, live_requested=True)
        request["package_manager_invocation_requested"] = True
        self.assertEqual(validate_h2_package_live_probe_request(request, bundle)["result_status"], "blocked_by_package_manager_policy")

    def test_install_execute_attempt_is_rejected(self):
        bundle = self._approved_bundle("nuget")
        request = build_h2_package_live_probe_request("nuget", "example_package_metadata", bundle, live_requested=True)
        request["install_execute_requested"] = True
        self.assertEqual(validate_h2_package_live_probe_request(request, bundle)["result_status"], "blocked_by_package_manager_policy")

    def test_public_index_mutation_claim_is_rejected(self):
        record = {"truth_boundary": {"public_index_mutated": True}}
        self.assertTrue(detect_h2_package_live_probe_truth_boundary_violations(record))

    def test_master_index_mutation_claim_is_rejected(self):
        record = {"product_boundary": {"mutated_master_index": True}}
        self.assertTrue(detect_h2_package_live_probe_product_boundary_violations(record))

    def test_rights_malware_installability_dependency_claims_are_rejected(self):
        record = {
            "truth_boundary": {
                "rights_clearance_claimed": True,
                "malware_safety_claimed": True,
                "verified_installability_claimed": True,
                "dependency_correctness_claimed": True,
            }
        }
        self.assertEqual(len(detect_h2_package_live_probe_truth_boundary_violations(record)), 4)

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H2_SOURCE_IDS:
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
            "ecosystem": cfg["ecosystem"],
            "package_name": cfg["package_name"],
            "namespace_or_scope": cfg["namespace_or_scope"],
            "version": cfg["version"],
            "release_id": cfg["release_id"],
            "source_native_id": cfg["release_id"],
            "title": cfg["package_name"],
            "description_summary": "Mocked package metadata response.",
            "project_urls": ["https://example.invalid/project"],
            "repository_urls": ["https://example.invalid/repository"],
            "license_metadata": {"license_claimed": "NOASSERTION", "rights_clearance_claimed": False},
            "dependencies": [{"dependency_name": "sample-dependency", "dependency_version_range": ">=1.0", "dependency_kind": "runtime", "optional": False}],
            "distribution_files": [{"file_name": f"{cfg['package_name']}-1.0.0.metadata", "file_kind": "metadata_record", "file_size": 0, "file_hashes": {"sha256": "not-a-payload-hash"}}],
            "hash_metadata": {"metadata_hash_present": True, "payload_hash_downloaded": False},
            "source_metadata": {"mocked": True},
        }


if __name__ == "__main__":
    unittest.main()
