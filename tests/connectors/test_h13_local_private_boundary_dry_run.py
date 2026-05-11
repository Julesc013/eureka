from __future__ import annotations

import copy
import importlib
import unittest

from runtime.connectors.h13_local_private.boundary_dry_run_common import (
    BOUNDARY_REQUEST_KEYS,
    OPERATION_CLASSES,
    build_h13_boundary_dry_run_blocked_result,
    build_h13_boundary_dry_run_result,
    build_h13_local_private_boundary_dry_run_request,
    detect_h13_boundary_product_boundary_violations,
    detect_h13_boundary_truth_boundary_violations,
    load_h13_local_private_boundary_policy_bundle,
    validate_h13_boundary_dry_run_request,
    validate_h13_boundary_source_approval,
)


class H13LocalPrivateBoundaryDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_h13_local_private_boundary_policy_bundle()
        self.request = build_h13_local_private_boundary_dry_run_request("local_folder_metadata", "example_local_source_boundary", self.bundle)

    def test_policy_pending_blocks_dry_run(self) -> None:
        result = validate_h13_boundary_dry_run_request(self.request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertEqual("blocked_by_missing_approval", result["result_status"])

    def test_source_not_in_allowlist_blocks_dry_run(self) -> None:
        result = validate_h13_boundary_dry_run_request(dict(self.request, source_id="unknown_source"), self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("known H13", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_dry_run(self) -> None:
        result = validate_h13_boundary_source_approval("local_folder_metadata", "not_approved", self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("request key is not approved for this source", result["blocked_reasons"])

    def test_kill_switch_blocks_when_otherwise_approved(self) -> None:
        bundle = copy.deepcopy(self.bundle)
        source = _source(bundle, "local_folder_metadata")
        source.update({"approval_status": "approved_for_boundary_dry_run", "boundary_dry_run_approved": True, "allowed_request_keys": ["example_local_source_boundary"], "max_operations_current": 1})
        result = validate_h13_boundary_source_approval("local_folder_metadata", "example_local_source_boundary", bundle)
        self.assertFalse(result["approved"])
        self.assertEqual("blocked_by_kill_switch", result["result_status"])

    def test_forbidden_operation_class_blocks_dry_run(self) -> None:
        request = dict(self.request, boundary_operation_class="filesystem_scan")
        result = validate_h13_boundary_dry_run_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("boundary_operation_class is not allowlisted for this source", result["blocked_reasons"])

    def test_forbidden_request_flags_are_rejected(self) -> None:
        cases = [
            "local_access_requested", "private_source_access_requested", "user_supplied_url_fetch_requested",
            "authenticated_access_requested", "restricted_source_access_requested", "network_access_requested",
            "external_api_requested", "model_provider_requested", "filesystem_scan_requested",
            "directory_listing_requested", "archive_listing_requested", "credential_handling_requested",
            "local_cas_import_requested", "pack_export_requested", "pack_import_requested", "file_hashing_requested",
            "fingerprinting_requested", "malware_scanning_requested", "extraction_requested", "execution_requested",
            "acquisition_action_requested", "upload_requested", "public_share_requested", "source_cache_write_requested",
            "evidence_write_requested", "review_queue_write_requested", "public_index_write_requested", "master_index_write_requested",
        ]
        for flag in cases:
            with self.subTest(flag=flag):
                result = validate_h13_boundary_dry_run_request(dict(self.request, **{flag: True}), self.bundle)
                self.assertFalse(result["approved"])

    def test_dry_preflight_blocked_result_does_not_access_sources(self) -> None:
        blocked = build_h13_boundary_dry_run_blocked_result(self.request, ["missing approval"], self.bundle)
        self.assertFalse(blocked["local_access_used"])
        self.assertFalse(blocked["network_used"])
        self.assertEqual(0, blocked["operation_count"])

    def test_mocked_boundary_request_builds_result_for_representative_modules(self) -> None:
        payload = {"source_native_id": "mock-boundary", "metadata_summary": "mock boundary only"}
        for source_id in ("local_folder_metadata", "user_supplied_url_metadata_boundary", "restricted_source_manifest_only"):
            with self.subTest(source_id=source_id):
                module = importlib.import_module(f"runtime.connectors.h13_local_private.boundary_dry_run_{source_id}")
                normalized = module.normalize_boundary_payload(payload, self.bundle)
                self.assertEqual(source_id, normalized["source_id"])
                result = build_h13_boundary_dry_run_result(source_id, payload, {"result_status": "boundary_dry_run_completed", "operation_count": 1}, self.bundle)
                self.assertFalse(result["local_access_used"])
                self.assertFalse(result["network_used"])

    def test_candidates_and_previews_remain_non_truth(self) -> None:
        result = build_h13_boundary_dry_run_blocked_result(self.request, ["missing approval"], self.bundle)
        for key in (
            "local_source_identity_candidate", "private_source_boundary_candidate", "user_supplied_url_boundary_candidate",
            "authenticated_source_boundary_candidate", "restricted_source_manifest_candidate", "local_cas_import_boundary_candidate",
            "pack_export_import_boundary_candidate", "privacy_redaction_candidate", "local_private_rights_safety_candidate",
            "source_cache_candidate_preview", "evidence_candidate_preview", "review_queue_seed_preview",
        ):
            self.assertIn("truth_boundary", result[key])
        self.assertFalse(detect_h13_boundary_truth_boundary_violations(result, self.bundle))
        self.assertFalse(detect_h13_boundary_product_boundary_violations(result, self.bundle))

    def test_truth_and_product_claims_are_rejected(self) -> None:
        result = build_h13_boundary_dry_run_blocked_result(self.request, ["missing approval"], self.bundle)
        result["truth_boundary"]["rights_clearance_claimed"] = True
        result["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(detect_h13_boundary_truth_boundary_violations(result, self.bundle))
        self.assertTrue(detect_h13_boundary_product_boundary_violations(result, self.bundle))


def _source(bundle: dict, source_id: str) -> dict:
    for item in bundle["allowed_requests"]["sources"]:
        if item["source_id"] == source_id:
            return item
    raise AssertionError(source_id)


if __name__ == "__main__":
    unittest.main()
