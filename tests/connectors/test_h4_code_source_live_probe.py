import copy
import importlib
from unittest import mock
import unittest

from runtime.connectors.h4_code_source_release.live_probe_common import (
    H4_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h4_code_source_live_probe_request,
    build_h4_code_source_live_probe_result,
    detect_h4_code_source_live_probe_product_boundary_violations,
    detect_h4_code_source_live_probe_truth_boundary_violations,
    load_h4_code_source_live_probe_policy_bundle,
    validate_h4_code_source_live_probe_request,
)
from scripts.run_h4_code_source_live_probe import run_probe


class H4CodeSourceLiveProbeTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_h4_code_source_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self):
        request = build_h4_code_source_live_probe_request("github_releases", "example_release_metadata", self.bundle, live_requested=True)
        result = validate_h4_code_source_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn(result["result_status"], {"blocked_by_missing_approval", "blocked_by_endpoint_policy", "blocked_by_kill_switch"})

    def test_source_not_in_allowlist_blocks_live_call(self):
        request = {"source_id": "not_h4", "approved_request_key": "x", "endpoint_or_metadata_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h4_code_source_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h4", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self):
        bundle = self._approved_bundle("github_releases")
        request = build_h4_code_source_live_probe_request("github_releases", "example_release_metadata", bundle, live_requested=True)
        self._source(bundle, "allowed_requests", "github_releases")["allowed_request_keys"] = []
        result = validate_h4_code_source_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self):
        bundle = self._approved_bundle("github_releases")
        request = build_h4_code_source_live_probe_request("github_releases", "example_release_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "github_releases")["default_enabled"] = False
        result = validate_h4_code_source_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self):
        bundle = self._approved_bundle("github_releases")
        request = build_h4_code_source_live_probe_request("github_releases", "example_release_metadata", bundle, live_requested=True)
        request["endpoint_or_metadata_class"] = "release_asset_download_forbidden_current"
        result = validate_h4_code_source_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_clone_download_git_and_build_attempts_are_rejected(self):
        bundle = self._approved_bundle("github_releases")
        request = build_h4_code_source_live_probe_request("github_releases", "example_release_metadata", bundle, live_requested=True)
        for key in ("repository_clone_requested", "source_archive_download_requested", "release_asset_download_requested", "git_command_invocation_requested", "build_tool_invocation_requested"):
            with self.subTest(key=key):
                candidate = dict(request)
                candidate[key] = True
                self.assertFalse(validate_h4_code_source_live_probe_request(candidate, bundle)["approved"])

    def test_dry_preflight_does_not_call_network(self):
        request = build_h4_code_source_live_probe_request("github_releases", "example_release_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self):
        approved = self._approved_all_bundle()
        for source_id in H4_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                payload = self._payload(source_id)
                result = build_h4_code_source_live_probe_result(source_id, payload, {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])
                self.assertFalse(result["truth_boundary"]["source_identity_candidate_is_truth"])
                self.assertFalse(result["truth_boundary"]["release_identity_candidate_is_truth"])

    def test_source_modules_normalize_payloads(self):
        for source_id in H4_SOURCE_IDS:
            module = importlib.import_module(f"runtime.connectors.h4_code_source_release.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def test_source_identity_and_git_swhid_remain_candidates_only(self):
        result = build_h4_code_source_live_probe_result("software_heritage_identity", self._payload("software_heritage_identity"), {"request_key": "example_swhid_resolution_metadata"}, self._approved_bundle("software_heritage_identity"))
        identity = result["source_identity_candidate"]
        self.assertFalse(identity["truth_boundary"]["source_identity_candidate_is_accepted_identity"])
        self.assertFalse(identity["truth_boundary"]["git_object_candidate_is_accepted_provenance"])
        self.assertFalse(identity["truth_boundary"]["swhid_candidate_is_accepted_object_truth"])

    def test_release_identity_relation_asset_source_cache_evidence_and_review_boundaries(self):
        result = build_h4_code_source_live_probe_result("github_releases", self._payload("github_releases"), {"request_key": "example_release_metadata"}, self._approved_bundle("github_releases"))
        self.assertFalse(result["release_identity_candidate"]["truth_boundary"]["release_identity_candidate_is_accepted_release_truth"])
        self.assertFalse(result["source_to_binary_relation_candidate_preview"][0]["truth_boundary"]["relation_candidate_is_accepted_provenance"])
        self.assertFalse(result["release_asset_candidate_preview"][0]["download_allowed_current"])
        self.assertFalse(result["release_asset_candidate_preview"][0]["truth_boundary"]["asset_hash_proves_malware_safety"])
        self.assertFalse(result["release_asset_candidate_preview"][0]["truth_boundary"]["signature_metadata_proves_authenticity"])
        self.assertFalse(result["release_asset_candidate_preview"][0]["truth_boundary"]["sbom_metadata_is_provenance"])
        self.assertFalse(result["source_cache_candidate_preview"]["truth_boundary"]["source_cache_preview_is_accepted_source"])
        self.assertFalse(result["evidence_candidate_preview"]["truth_boundary"]["evidence_preview_is_accepted_evidence"])
        self.assertFalse(result["review_queue_seed_preview"]["review_queue_seed_is_review_decision"])

    def test_public_master_rights_malware_installability_authenticity_and_build_claims_are_rejected(self):
        record = {
            "truth_boundary": {
                "public_index_mutated": True,
                "master_index_mutated": True,
                "rights_clearance_claimed": True,
                "malware_safety_claimed": True,
                "verified_installability_claimed": True,
                "verified_authenticity_claimed": True,
                "verified_build_reproducibility_claimed": True,
            }
        }
        self.assertEqual(len(detect_h4_code_source_live_probe_truth_boundary_violations(record)), 7)
        self.assertTrue(detect_h4_code_source_live_probe_product_boundary_violations({"product_boundary": {"mutated_master_index": True}}))

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H4_SOURCE_IDS:
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
        endpoint["allowlisted_endpoint_or_metadata_classes_current"] = [cfg["endpoint_or_metadata_class"]]
        rate = self._source(bundle, "rate_limit_policy", source_id)
        rate["decision_status"] = "approved_for_bounded_metadata_probe"
        rate["max_requests_per_run"] = 1
        rate["max_requests_per_minute"] = 1
        rate["user_agent_contact_posture"] = "not_required_documented"
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
        project = cfg["repository_or_project"]
        return {
            "source_host": cfg["source_host"],
            "owner_or_namespace": cfg["owner_or_namespace"],
            "repository_name": project,
            "project_name": project,
            "origin_url_candidate": f"fixture:origin:h4:{source_id}",
            "repository_url_candidate": f"fixture:repository:h4:{source_id}",
            "source_native_id": f"{source_id}/mock/live-probe",
            "git_commit_id_candidate": "git:fixture:commit:h4:0000001",
            "git_tree_id_candidate": "git:fixture:tree:h4:0000001",
            "git_tag_candidate": cfg["release_or_tag_identifier"],
            "branch_name_candidate": "main",
            "release_id": f"{source_id}-release",
            "release_tag": cfg["release_or_tag_identifier"],
            "release_name": f"{project} mock release",
            "release_version": "1.0.0-fixture",
            "release_timestamp": "2026-05-10T00:00:00Z",
            "release_actor_or_author": "fixture-maintainer",
            "release_notes_summary": "Mocked metadata-only release response.",
            "release_asset_summary": {"asset_count": 1, "download_allowed_current": False, "payload_available_current": False},
            "release_assets": [{"asset_name": f"{project}-1.0.0.tar.gz", "asset_kind": "source_archive_metadata", "asset_size": 0, "asset_hashes": {"sha256": "metadata-only"}, "asset_locator": "fixture:asset:h4", "signature_metadata": {"present": True, "verified_current": False}, "sbom_metadata": {"present": False, "verified_current": False}}],
            "swhid_candidate": "swh:1:rev:fixture0000000000000000000000000000000000000000",
            "archived_origin_candidate": "fixture:archive:h4",
            "license_metadata": {"declared_license": "NOASSERTION", "rights_clearance_claimed": False},
            "source_to_binary_relation": {"relation_kind": "tag_to_release_candidate", "relation_confidence_or_uncertainty": "candidate_only"},
            "source_metadata": {"mocked": True},
        }


if __name__ == "__main__":
    unittest.main()
