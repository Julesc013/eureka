from __future__ import annotations

import copy
import unittest

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.rollup_dry_run_common import (
    REQUEST_FORBIDDEN_TRUE_KEYS,
    build_h14_rollup_blocked_result,
    build_h14_rollup_dry_run_result,
    build_h14_source_discovery_rollup_dry_run_request,
    detect_h14_registry_or_pack_mutation_violations,
    detect_h14_rollup_product_boundary_violations,
    detect_h14_rollup_truth_boundary_violations,
    load_h14_rollup_inputs,
    load_h14_rollup_policy_bundle,
    validate_h14_rollup_approval,
    validate_h14_rollup_dry_run_request,
)


class H14SourceDiscoveryRollupDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_h14_rollup_policy_bundle()
        self.request = build_h14_source_discovery_rollup_dry_run_request("source_need_registry", "example_source_need_rollup", self.bundle)

    def test_policy_approved_dry_run_preflight_passes(self) -> None:
        result = validate_h14_rollup_dry_run_request(self.request, self.bundle)
        self.assertTrue(result["approved"], result["blocked_reasons"])

    def test_policy_pending_blocks_dry_run(self) -> None:
        request = build_h14_source_discovery_rollup_dry_run_request("source_discovery_policy", "example_source_discovery_rollup", self.bundle)
        result = validate_h14_rollup_dry_run_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertEqual("blocked_by_missing_approval", result["result_status"])

    def test_source_not_in_allowlist_blocks_dry_run(self) -> None:
        request = dict(self.request, source_id="unknown_source")
        result = validate_h14_rollup_dry_run_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("known H14", result["blocked_reasons"][0])

    def test_request_key_not_approved_blocks_dry_run(self) -> None:
        result = validate_h14_rollup_approval("source_need_registry", "not_approved", self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("request key is not approved for this source", result["blocked_reasons"])

    def test_kill_switch_blocks_otherwise_approved(self) -> None:
        bundle = copy.deepcopy(self.bundle)
        bundle["kill_switch_policy"]["rollup_dry_run_kill_switch_enabled"] = True
        result = validate_h14_rollup_dry_run_request(self.request, bundle)
        self.assertFalse(result["approved"])
        self.assertEqual("blocked_by_kill_switch", result["result_status"])

    def test_forbidden_operation_class_blocks_dry_run(self) -> None:
        request = dict(self.request, rollup_operation_class="source_discovery_runtime")
        result = validate_h14_rollup_dry_run_request(request, self.bundle)
        self.assertFalse(result["approved"])
        self.assertIn("approved operation class is not rollup_preview_only", result["blocked_reasons"])

    def test_forbidden_request_flags_are_rejected(self) -> None:
        for flag in sorted(REQUEST_FORBIDDEN_TRUE_KEYS):
            with self.subTest(flag=flag):
                result = validate_h14_rollup_dry_run_request(dict(self.request, **{flag: True}), self.bundle)
                self.assertFalse(result["approved"])

    def test_mocked_committed_artifact_rollup_builds_result(self) -> None:
        inputs = load_h14_rollup_inputs(None, self.bundle)
        result = build_h14_rollup_dry_run_result("source_need_registry", inputs, self.bundle)
        self.assertEqual("rollup_dry_run_completed", result["result_status"])
        self.assertEqual(1, result["operation_count"])
        self.assertFalse(result["network_used"])
        self.assertFalse(result["registry_mutation_performed"])

    def test_candidates_and_previews_remain_non_truth(self) -> None:
        result = build_h14_rollup_dry_run_result("source_need_registry", load_h14_rollup_inputs(None, self.bundle), self.bundle)
        candidate_keys = (
            "source_need_candidates", "source_candidate_candidates", "source_discovery_candidates",
            "source_pack_manifest_candidates", "connector_pack_manifest_candidates", "coverage_manifest_candidates",
            "connector_scorecard_candidates", "source_reliability_freshness_candidates",
            "source_dispute_revocation_candidates", "source_lineage_provenance_candidates",
            "pack_import_export_boundary_candidates",
        )
        for key in candidate_keys:
            self.assertFalse(result[key][0]["truth_boundary"].get("source_candidate_candidate_is_source_truth", False))
        self.assertFalse(result["source_cache_candidate_preview"]["accepted_source"])
        self.assertFalse(result["evidence_candidate_preview"]["accepted_evidence"])
        self.assertFalse(result["review_queue_seed_preview"]["review_decision"])
        self.assertFalse(detect_h14_rollup_truth_boundary_violations(result, self.bundle))
        self.assertFalse(detect_h14_rollup_product_boundary_violations(result, self.bundle))
        self.assertFalse(detect_h14_registry_or_pack_mutation_violations(result, self.bundle))

    def test_blocked_result_does_not_access_or_mutate(self) -> None:
        request = build_h14_source_discovery_rollup_dry_run_request("source_discovery_policy", "example_source_discovery_rollup", self.bundle)
        blocked = build_h14_rollup_blocked_result(request, ["missing approval"], self.bundle)
        self.assertEqual(0, blocked["operation_count"])
        self.assertFalse(blocked["network_used"])
        self.assertFalse(blocked["pack_export_import_performed"])

    def test_truth_and_product_claims_are_rejected(self) -> None:
        result = build_h14_rollup_dry_run_result("source_need_registry", load_h14_rollup_inputs(None, self.bundle), self.bundle)
        result["truth_boundary"]["rights_clearance_claimed"] = True
        result["product_boundary"]["mutated_public_index"] = True
        self.assertTrue(detect_h14_rollup_truth_boundary_violations(result, self.bundle))
        self.assertTrue(detect_h14_rollup_product_boundary_violations(result, self.bundle))


if __name__ == "__main__":
    unittest.main()
