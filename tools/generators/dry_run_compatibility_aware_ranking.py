#!/usr/bin/env python3
"""Emit a stdout-only synthetic compatibility-aware ranking assessment."""

import argparse
import json
import sys
from typing import Sequence, TextIO


def build_assessment(target_os: str, left_title: str, right_title: str) -> dict:
    return {
        "schema_version": "0.1.0",
        "compatibility_ranking_assessment_id": "compat-ranking:dry-run",
        "compatibility_ranking_assessment_kind": "compatibility_aware_ranking_assessment",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_compatibility_aware_ranking_v0",
        "ranking_scope": {"scope_kind": "synthetic_example", "ranking_mode": "dry_run_example", "current_runtime_order_preserved": True, "live_runtime_changed": False, "limitations": ["stdout only"]},
        "target_profile_ref": f"dry-run-target:{target_os}",
        "ranked_items": [
            {"item_ref": "dry-run:left", "item_kind": "synthetic_example", "item_label": left_title, "item_status": "evidence_backed", "proposed_rank": 1, "current_rank": 1, "rank_changed_now": False, "source_refs": [], "evidence_refs": ["dry-run:evidence"], "compatibility_status": "likely_compatible", "limitations": []},
            {"item_ref": "dry-run:right", "item_kind": "synthetic_example", "item_label": right_title, "item_status": "unknown", "proposed_rank": 2, "current_rank": 2, "rank_changed_now": False, "source_refs": [], "evidence_refs": [], "compatibility_status": "unknown", "limitations": []},
        ],
        "compatibility_factors": [{"factor_id": "dry-run:factor:platform", "factor_type": "platform_os_match", "direction": "positive", "weight_policy": "descriptive_only", "score_applied_now": False, "evidence_refs": ["dry-run:evidence"], "limitations": []}],
        "platform_os_version_matching": {"platform_match_status": "likely_compatible", "target_platforms": [target_os], "result_platforms": [target_os], "os_version_relation": "unknown", "platform_evidence_refs": ["dry-run:evidence"], "platform_match_not_truth": True, "limitations": []},
        "architecture_cpu_abi_api_matching": {"architecture_match_status": "unknown", "cpu_match_status": "unknown", "abi_match_status": "unknown", "api_match_status": "unknown", "target_architectures": [], "result_architectures": [], "target_cpu_features": [], "result_cpu_requirements": [], "target_apis": [], "result_api_requirements": [], "evidence_refs": [], "limitations": []},
        "runtime_dependency_requirements": {"runtime_match_status": "unknown", "required_runtimes": [], "required_libraries": [], "package_dependencies": [], "dependency_metadata_status": "not_checked", "dependency_resolution_performed": False, "dependency_safety_claimed": False, "installability_claimed": False, "evidence_refs": [], "gaps": [], "limitations": []},
        "hardware_peripheral_driver_requirements": {"hardware_match_status": "unknown", "required_hardware": [], "required_peripherals": [], "required_drivers": [], "driver_evidence_status": "unknown", "evidence_refs": [], "gaps": [], "limitations": []},
        "emulator_vm_reconstruction_feasibility": {"feasibility_status": "unknown", "emulator_or_vm_kind": "unknown", "launch_enabled": False, "VM_launch_enabled": False, "emulator_launch_enabled": False, "reconstruction_manifest_required_future": False, "evidence_refs": [], "gaps": [], "limitations": []},
        "compatibility_evidence_strength": {"compatibility_evidence_class": "weak", "evidence_basis": "metadata_claim", "evidence_refs": ["dry-run:evidence"], "compatibility_evidence_not_truth": True, "limitations": []},
        "incompatibility_and_unknown_gaps": {"incompatibility_status": "unknown", "unknown_gap_status": "compatibility_evidence_gap", "gaps": [], "absence_of_evidence_is_not_incompatibility": True, "limitations": []},
        "source_provenance_candidate_caution": {"source_refs": [], "evidence_refs": ["dry-run:evidence"], "provenance_refs": [], "candidate_refs": [], "source_posture": "unknown", "provenance_strength": "unknown", "candidate_status": "review_required", "source_trust_claimed": False, "candidate_confidence_not_truth": True, "provenance_not_truth": True, "limitations": []},
        "action_safety_installability_caution": {"action_safety_class": "safe_metadata_actions_only", "allowed_actions": ["inspect_metadata", "view_sources", "view_evidence", "compare", "cite"], "disabled_actions": ["download", "install", "execute", "upload", "mirror", "arbitrary_url_fetch", "package_manager_invoke", "emulator_launch", "VM_launch"], "downloads_enabled": False, "installs_enabled": False, "execution_enabled": False, "package_manager_invoked": False, "emulator_launch_enabled": False, "VM_launch_enabled": False, "installability_claimed": False, "installability_evidence_required": True, "limitations": []},
        "rights_risk": {"rights_classification": "public_metadata_only", "risk_classification": "metadata_only", "rights_clearance_claimed": False, "malware_safety_claimed": False, "dependency_safety_claimed": False, "risk_caution_required": True, "rights_risk_affects_rank_future": True, "rights_risk_score_applied_now": False, "limitations": []},
        "tie_breaks": {"tie_break_policy": "preserve_current_order_v0", "tie_break_factors": ["stable_id"], "tie_break_applied_now": False, "random_tie_break_allowed": False, "limitations": []},
        "compatibility_explanation_ref": "compat-explanation:dry-run",
        "public_projection": {"result_card_projection": "future", "result_merge_group_projection": "future", "object_page_projection": "future", "source_page_projection": "future", "comparison_page_projection": "future", "compatibility_badge_projection": "categorical_future", "explanation_visibility": "user_visible_summary", "user_visible_compatibility_reason_required": True, "compatibility_score_publication_policy": "no_numeric_score_v0", "limitations": []},
        "privacy": {"privacy_classification": "public_safe_example", "contains_private_path": False, "contains_secret": False, "contains_private_url": False, "contains_user_identifier": False, "contains_ip_address": False, "contains_raw_private_query": False, "contains_local_machine_fingerprint": False, "publishable": True, "public_aggregate_allowed": True, "reasons": ["dry run synthetic"]},
        "limitations": ["stdout-only dry run; no files written"],
        "no_runtime_guarantees": {"runtime_compatibility_ranking_implemented": False},
        "no_ranking_change_guarantees": {"compatibility_ranking_applied_to_live_search": False, "public_search_order_changed": False},
        "no_mutation_guarantees": {"master_index_mutated": False, "public_index_mutated": False, "local_index_mutated": False, "source_cache_mutated": False, "evidence_ledger_mutated": False, "candidate_index_mutated": False},
        "notes": ["dry run only"],
    } | {key: False for key in [
        "runtime_compatibility_ranking_implemented", "persistent_compatibility_ranking_store_implemented", "compatibility_ranking_applied_to_live_search", "public_search_order_changed", "result_suppressed", "hidden_suppression_performed", "candidate_promotion_performed", "installability_claimed", "compatibility_truth_claimed", "dependency_safety_claimed", "emulator_vm_launch_enabled", "package_manager_invoked", "executable_inspected", "downloads_enabled", "installs_enabled", "execution_enabled", "master_index_mutated", "public_index_mutated", "local_index_mutated", "source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated", "live_source_called", "external_calls_performed", "telemetry_exported", "popularity_signal_used", "user_profile_signal_used", "ad_signal_used", "model_call_performed", "rights_clearance_claimed", "malware_safety_claimed"
    ]}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-os", required=True)
    parser.add_argument("--left-title", required=True)
    parser.add_argument("--right-title", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    assessment = build_assessment(args.target_os, args.left_title, args.right_title)
    if args.json:
        print(json.dumps(assessment, indent=2), file=stdout)
    else:
        print("status: dry_run_validated", file=stdout)
        print(f"target_os: {args.target_os}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
