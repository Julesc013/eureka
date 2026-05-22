import copy
import importlib
from unittest import mock
import unittest

from archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.live_probe_common import (
    H5_SOURCE_IDS,
    SOURCE_CONFIGS,
    build_h5_vendor_update_live_probe_request,
    build_h5_vendor_update_live_probe_result,
    detect_h5_vendor_update_live_probe_product_boundary_violations,
    detect_h5_vendor_update_live_probe_truth_boundary_violations,
    load_h5_vendor_update_live_probe_policy_bundle,
    validate_h5_vendor_update_live_probe_request,
)
from scripts.run_h5_vendor_update_live_probe import run_probe


class H5VendorUpdateLiveProbeTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_h5_vendor_update_live_probe_policy_bundle()

    def test_policy_pending_blocks_live_calls(self):
        request = build_h5_vendor_update_live_probe_request("nvidia_driver_downloads", "example_driver_metadata", self.bundle, live_requested=True)
        result = validate_h5_vendor_update_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn(result["result_status"], {"blocked_by_missing_approval", "blocked_by_endpoint_policy", "blocked_by_kill_switch"})

    def test_source_not_in_allowlist_blocks_live_call(self):
        request = {"source_id": "not_h5", "approved_request_key": "x", "endpoint_or_metadata_class": "metadata", "operation_scope": "metadata_only"}
        result = validate_h5_vendor_update_live_probe_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("not_h5", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_live_call(self):
        bundle = self._approved_bundle("nvidia_driver_downloads")
        request = build_h5_vendor_update_live_probe_request("nvidia_driver_downloads", "example_driver_metadata", bundle, live_requested=True)
        self._source(bundle, "allowed_requests", "nvidia_driver_downloads")["allowed_request_keys"] = []
        result = validate_h5_vendor_update_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertTrue(any("request key is not approved" in reason for reason in result["blocked_reasons"]))

    def test_kill_switch_blocks_live_call(self):
        bundle = self._approved_bundle("nvidia_driver_downloads")
        request = build_h5_vendor_update_live_probe_request("nvidia_driver_downloads", "example_driver_metadata", bundle, live_requested=True)
        self._source(bundle, "kill_switch_policy", "nvidia_driver_downloads")["default_enabled"] = False
        result = validate_h5_vendor_update_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_kill_switch")

    def test_forbidden_endpoint_class_blocks_live_call(self):
        bundle = self._approved_bundle("nvidia_driver_downloads")
        request = build_h5_vendor_update_live_probe_request("nvidia_driver_downloads", "example_driver_metadata", bundle, live_requested=True)
        request["endpoint_or_metadata_class"] = "driver_download_forbidden_current"
        result = validate_h5_vendor_update_live_probe_request(request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual(result["result_status"], "blocked_by_download_policy")

    def test_catalog_download_tool_flash_install_attempts_are_rejected(self):
        bundle = self._approved_bundle("nvidia_driver_downloads")
        request = build_h5_vendor_update_live_probe_request("nvidia_driver_downloads", "example_driver_metadata", bundle, live_requested=True)
        for key in (
            "vendor_catalog_fetch_requested",
            "driver_download_requested",
            "firmware_download_requested",
            "runtime_download_requested",
            "installer_download_requested",
            "checksum_signature_fetch_requested",
            "vendor_tool_invocation_requested",
            "firmware_flash_requested",
            "install_execute_requested",
        ):
            with self.subTest(key=key):
                candidate = dict(request)
                candidate[key] = True
                self.assertFalse(validate_h5_vendor_update_live_probe_request(candidate, bundle)["approved"])

    def test_dry_preflight_does_not_call_network(self):
        request = build_h5_vendor_update_live_probe_request("nvidia_driver_downloads", "example_driver_metadata", self.bundle)
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            artifacts = run_probe(request, self.bundle, live=False)
        live = artifacts["live_probe_result"]
        self.assertEqual(live["request_count"], 0)
        self.assertFalse(live["network_used"])

    def test_mocked_response_builds_live_probe_result_for_each_source(self):
        approved = self._approved_all_bundle()
        for source_id in H5_SOURCE_IDS:
            with self.subTest(source_id=source_id):
                result = build_h5_vendor_update_live_probe_result(source_id, self._payload(source_id), {"request_key": SOURCE_CONFIGS[source_id]["request_key"], "network_used": True}, approved)
                self.assertEqual(result["result_status"], "live_probe_completed")
                self.assertEqual(result["normalized_record"]["source_id"], source_id)
                self.assertTrue(result["network_used"])
                self.assertFalse(result["truth_boundary"]["vendor_identity_candidate_is_truth"])
                self.assertFalse(result["truth_boundary"]["compatibility_candidate_is_truth"])

    def test_source_modules_normalize_payloads(self):
        for source_id in H5_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.live_probe_{source_id}")
            record = module.normalize_response_payload(self._payload(source_id), self.bundle)
            self.assertEqual(record["source_id"], source_id)

    def test_candidate_boundaries(self):
        result = build_h5_vendor_update_live_probe_result("nvidia_driver_downloads", self._payload("nvidia_driver_downloads"), {"request_key": "example_driver_metadata"}, self._approved_bundle("nvidia_driver_downloads"))
        self.assertFalse(result["vendor_identity_candidate"]["truth_boundary"]["vendor_identity_candidate_is_accepted_vendor_truth"])
        self.assertFalse(result["driver_device_compatibility_candidate"]["truth_boundary"]["compatibility_candidate_is_verified_compatibility"])
        self.assertFalse(result["payload_metadata_candidate"]["download_allowed_current"])
        self.assertFalse(result["payload_metadata_candidate"]["truth_boundary"]["payload_hash_proves_malware_safety"])
        self.assertFalse(result["payload_metadata_candidate"]["truth_boundary"]["signature_metadata_proves_authenticity"])
        self.assertFalse(result["source_cache_candidate_preview"]["truth_boundary"]["source_cache_preview_is_accepted_source"])
        self.assertFalse(result["evidence_candidate_preview"]["truth_boundary"]["evidence_preview_is_accepted_evidence"])
        self.assertFalse(result["review_queue_seed_preview"]["review_seed_is_review_decision"])

    def test_public_master_rights_malware_installability_compatibility_authenticity_claims_are_rejected(self):
        record = {
            "truth_boundary": {
                "public_index_mutated": True,
                "master_index_mutated": True,
                "rights_clearance_claimed": True,
                "malware_safety_claimed": True,
                "verified_installability_claimed": True,
                "verified_compatibility_claimed": True,
                "verified_authenticity_claimed": True,
            }
        }
        self.assertEqual(len(detect_h5_vendor_update_live_probe_truth_boundary_violations(record)), 7)
        self.assertTrue(detect_h5_vendor_update_live_probe_product_boundary_violations({"product_boundary": {"mutated_master_index": True}}))

    def _approved_all_bundle(self):
        bundle = copy.deepcopy(self.bundle)
        for source_id in H5_SOURCE_IDS:
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
            "vendor_name": cfg["vendor_name"],
            "product_name": f"{cfg['label']} mock product",
            "product_family": cfg["catalog_kind"],
            "product_line": "metadata-only",
            "support_page_ref": f"fixture:h5:{source_id}:support",
            "catalog_record_id": f"{source_id}-catalog",
            "update_record_id": f"{source_id}-update",
            "download_record_id": "download-blocked-current",
            "vendor_native_id": f"{source_id}/mock/live-probe",
            "vendor_release_id": f"{source_id}-release",
            "vendor_version": "1.0.0-fixture",
            "release_date_candidate": "2026-05-10",
            "package_or_payload_name": f"{source_id}-metadata-only-payload",
            "payload_kind": "metadata_only",
            "device_vendor_id": "VEN_FIXTURE",
            "device_product_id": "DEV_FIXTURE",
            "hardware_model": "Fixture Model",
            "hardware_revision": "A",
            "operating_system_family": "FixtureOS",
            "operating_system_version": "1",
            "architecture": "x64",
            "driver_name": "Fixture Driver",
            "driver_version": "1.0",
            "driver_class": "display",
            "chipset_or_component": "fixture chipset",
            "firmware_name": "Fixture Firmware",
            "firmware_version": "1.0",
            "bios_or_uefi_version": "1.0",
            "device_model": "Fixture Device",
            "board_model": "Fixture Board",
            "update_package_id": "update-blocked-current",
            "update_type": "metadata_only",
            "runtime_family": "Fixture Runtime",
            "runtime_name": "Fixture Runtime",
            "runtime_version": "1.0",
            "installer_name": "installer-download-blocked-current",
            "redistributable_package_id": "runtime-candidate",
            "prerequisite_summary": "candidate-only prerequisites",
            "compatibility_summary": "candidate-only compatibility",
            "risk_warning_summary": "candidate-only risk warning",
            "release_note_or_changelog_refs": ["fixture:h5:release-note"],
            "advisory_refs": ["fixture:h5:advisory"],
            "hash_metadata": {"candidate_only": True, "hash_metadata_proves_malware_safety": False},
            "signature_metadata": {"candidate_only": True, "signature_metadata_proves_authenticity": False},
            "payload_locator_candidate": "download-blocked-current",
        }


if __name__ == "__main__":
    unittest.main()
