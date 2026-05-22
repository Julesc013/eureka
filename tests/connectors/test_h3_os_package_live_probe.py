import copy
import importlib
from unittest import mock
import unittest

from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.live_probe_common import (
    H3_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h3_os_package_live_probe_request,
    build_h3_os_package_live_probe_result,
    detect_h3_os_package_live_probe_product_boundary_violations,
    detect_h3_os_package_live_probe_truth_boundary_violations,
    load_h3_os_package_live_probe_policy_bundle,
    validate_h3_os_package_live_probe_request,
)
from scripts.run_h3_os_package_live_probe import run_probe


class H3OSPackageLiveProbeTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_h3_os_package_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self):
        request = build_h3_os_package_live_probe_request("debian_snapshot", "example_package_metadata", self.bundle, live_requested=True)
        result = validate_h3_os_package_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn(result["result_status"], {"blocked_by_missing_approval", "blocked_by_endpoint_policy", "blocked_by_kill_switch"})

    def test_source_not_in_allowlist_blocks_live_call(self):
        request = {"source_id": "not_h3", "approved_request_key": "x", "endpoint_or_index_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h3_os_package_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h3", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self):
        bundle = self._approved_bundle("debian_snapshot")
        request = build_h3_os_package_live_probe_request("debian_snapshot", "example_package_metadata", bundle, live_requested=True)
        self._source(bundle, "allowed_requests", "debian_snapshot")["allowed_request_keys"] = []
        result = validate_h3_os_package_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self):
        bundle = self._approved_bundle("debian_snapshot")
        request = build_h3_os_package_live_probe_request("debian_snapshot", "example_package_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "debian_snapshot")["default_enabled"] = False
        result = validate_h3_os_package_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self):
        bundle = self._approved_bundle("debian_snapshot")
        request = build_h3_os_package_live_probe_request("debian_snapshot", "example_package_metadata", bundle, live_requested=True)
        request["endpoint_or_index_class"] = "deb_download_forbidden_current"
        result = validate_h3_os_package_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_repository_index_sync_attempt_is_rejected(self):
        bundle = self._approved_bundle("debian_snapshot")
        request = build_h3_os_package_live_probe_request("debian_snapshot", "example_package_metadata", bundle, live_requested=True)
        request["repository_index_fetch_requested"] = True
        result = validate_h3_os_package_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_index_sync_policy")

    def test_dry_preflight_does_not_call_network(self):
        request = build_h3_os_package_live_probe_request("debian_snapshot", "example_package_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self):
        approved = self._approved_all_bundle()
        for source_id in H3_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                payload = self._payload(source_id)
                result = build_h3_os_package_live_probe_result(source_id, payload, {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])
                self.assertFalse(result["truth_boundary"]["os_package_identity_candidate_is_truth"])
                self.assertFalse(result["truth_boundary"]["os_platform_compatibility_candidate_is_truth"])

    def test_source_modules_normalize_payloads(self):
        for source_id in H3_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def test_identity_and_purl_remain_candidates_only(self):
        result = build_h3_os_package_live_probe_result("debian_snapshot", self._payload("debian_snapshot"), {"request_key": "example_package_metadata"}, self._approved_bundle("debian_snapshot"))
        identity = result["os_package_identity_candidate"]
        self.assertFalse(identity["truth_boundary"]["identity_candidate_is_accepted_identity"])
        self.assertFalse(identity["truth_boundary"]["purl_candidate_is_truth"])

    def test_compatibility_candidate_does_not_prove_correctness(self):
        result = build_h3_os_package_live_probe_result("arch_linux_archive", self._payload("arch_linux_archive"), {"request_key": "example_package_metadata"}, self._approved_bundle("arch_linux_archive"))
        compatibility = result["os_platform_compatibility_candidate"]
        self.assertFalse(compatibility["truth_boundary"]["compatibility_candidate_is_verified_compatibility"])
        self.assertFalse(compatibility["truth_boundary"]["architecture_match_proves_runtime_compatibility"])

    def test_dependency_candidate_does_not_prove_correctness(self):
        result = build_h3_os_package_live_probe_result("fedora_rpm_metadata", self._payload("fedora_rpm_metadata"), {"request_key": "example_package_metadata"}, self._approved_bundle("fedora_rpm_metadata"))
        dependency = result["dependency_candidate_preview"][0]
        self.assertFalse(dependency["truth_boundary"]["dependency_candidate_is_correctness_proof"])

    def test_file_hash_candidate_does_not_grant_download_or_safety(self):
        result = build_h3_os_package_live_probe_result("freebsd_packages_ports", self._payload("freebsd_packages_ports"), {"request_key": "example_package_metadata"}, self._approved_bundle("freebsd_packages_ports"))
        file_candidate = result["package_file_candidate_preview"][0]
        self.assertFalse(file_candidate["download_allowed_current"])
        self.assertFalse(file_candidate["truth_boundary"]["file_hash_candidate_is_malware_safety"])

    def test_source_cache_evidence_and_review_previews_remain_previews(self):
        result = build_h3_os_package_live_probe_result("homebrew", self._payload("homebrew"), {"request_key": "example_package_metadata"}, self._approved_bundle("homebrew"))
        self.assertFalse(result["source_cache_candidate_preview"]["truth_boundary"]["source_cache_preview_is_accepted_source"])
        self.assertFalse(result["evidence_candidate_preview"]["truth_boundary"]["evidence_preview_is_accepted_evidence"])
        self.assertFalse(result["review_queue_seed_preview"]["review_queue_seed_is_review_decision"])

    def test_download_package_manager_and_install_attempts_are_rejected(self):
        bundle = self._approved_bundle("winget")
        request = build_h3_os_package_live_probe_request("winget", "example_package_metadata", bundle, live_requested=True)
        for key in ("package_download_requested", "package_manager_invocation_requested", "install_execute_requested"):
            with self.subTest(key=key):
                candidate = dict(request)
                candidate[key] = True
                self.assertFalse(validate_h3_os_package_live_probe_request(candidate, bundle)["approved"])

    def test_public_and_master_index_mutation_claims_are_rejected(self):
        self.assertTrue(detect_h3_os_package_live_probe_truth_boundary_violations({"truth_boundary": {"public_index_mutated": True}}))
        self.assertTrue(detect_h3_os_package_live_probe_product_boundary_violations({"product_boundary": {"mutated_master_index": True}}))

    def test_rights_malware_installability_dependency_compatibility_claims_are_rejected(self):
        record = {
            "truth_boundary": {
                "rights_clearance_claimed": True,
                "malware_safety_claimed": True,
                "verified_installability_claimed": True,
                "dependency_correctness_claimed": True,
                "compatibility_correctness_claimed": True,
            }
        }
        self.assertEqual(len(detect_h3_os_package_live_probe_truth_boundary_violations(record)), 5)

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H3_SOURCE_IDS:
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
        endpoint["allowlisted_endpoint_or_index_classes_current"] = [cfg["endpoint_or_index_class"]]
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
        package = cfg["package_name"]
        return {
            "ecosystem": cfg["ecosystem"],
            "distribution": cfg["distribution"],
            "distribution_release": cfg["distribution_release"],
            "repository_component": cfg["repository_component"],
            "repository_channel": cfg["repository_channel"],
            "package_name": package,
            "source_package_name": f"{package}-src",
            "binary_package_name": package,
            "architecture": cfg["architecture"],
            "version": cfg["version"],
            "epoch": "0",
            "release_revision": "live-probe",
            "build_id": f"{source_id}-mock-build",
            "source_native_id": f"{source_id}/{package}/1.2.3/mock",
            "title": package,
            "description_summary": "Mocked OS package metadata response.",
            "project_urls": ["fixture:project:h3:mock"],
            "upstream_urls": ["fixture:upstream:h3:mock"],
            "repository_urls": ["fixture:repository:h3:mock"],
            "license_metadata": {"license_claimed": "NOASSERTION", "rights_clearance_claimed": False},
            "relations": [{"relation_kind": "depends", "related_package_name": f"{package}-dep", "version_range_or_constraint": ">= 1.0", "optional": False}],
            "files": [{"file_name": f"{package}-1.2.3.metadata", "file_kind": "metadata_record", "file_size": 0, "file_hashes": {"sha256": "not-a-payload-hash"}}],
            "hash_metadata": {"metadata_hash_present": True, "payload_hash_downloaded": False},
            "platform_or_environment_markers": [cfg["distribution"], cfg["architecture"]],
            "source_metadata": {"mocked": True},
        }


if __name__ == "__main__":
    unittest.main()
