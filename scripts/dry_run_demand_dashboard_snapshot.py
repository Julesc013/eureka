#!/usr/bin/env python3
"""Emit a synthetic Demand Dashboard Snapshot v0 to stdout only."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Sequence


def build_snapshot() -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "dashboard_snapshot_id": "dry_run.demand_dashboard.synthetic_snapshot.v0",
        "dashboard_snapshot_kind": "demand_dashboard_snapshot",
        "status": "dry_run_validated",
        "created_by_tool": "dry_run_demand_dashboard_snapshot_v0",
        "input_summary": {
            "input_kind": "dry_run_example",
            "input_refs": [{"ref_id": "dry_run.synthetic_guarded_input", "ref_kind": "query_guard_decision", "status": "dry_run"}],
            "source_contracts_referenced": [
                "query_observation",
                "search_result_cache",
                "search_miss_ledger",
                "search_need_record",
                "probe_queue",
                "candidate_index",
                "known_absence_page",
                "query_guard_decision",
            ],
            "real_user_data_included": False,
            "raw_queries_included": False,
            "protected_data_included": False,
            "limitations": ["Stdout-only dry run; no logs, telemetry, account/IP tracking, or private data are read."],
        },
        "privacy_guard_summary": {
            "privacy_filter_required": True,
            "guard_contract_ref": "contracts/query/query_guard_decision.v0.json",
            "decisions_required_before_aggregation": True,
            "high_privacy_risk_excluded": True,
            "raw_query_aggregation_allowed": False,
            "private_path_aggregation_allowed": False,
            "secret_aggregation_allowed": False,
            "user_identifier_aggregation_allowed": False,
            "ip_address_aggregation_allowed": False,
            "notes": ["Dry-run snapshot assumes future query guard filtering before aggregation."],
        },
        "poisoning_guard_summary": {
            "poisoning_filter_required": True,
            "guard_contract_ref": "contracts/query/query_guard_decision.v0.json",
            "fake_demand_excluded": True,
            "spam_excluded": True,
            "source_stuffing_excluded": True,
            "candidate_poisoning_excluded": True,
            "high_poisoning_risk_excluded": True,
            "throttling_runtime_implemented": False,
            "notes": ["Dry-run snapshot excludes poisoning classes by policy and implements no throttling runtime."],
        },
        "dashboard_scope": {
            "scope_kind": "synthetic_example",
            "time_window_policy": "not_applicable_example",
            "source_scope": ["internet_archive_metadata", "wayback_cdx_memento", "github_releases"],
            "query_scope": ["synthetic old-platform source gaps"],
            "index_snapshot_refs": ["dry_run.public_index_snapshot_ref"],
            "includes_live_probe_data": False,
            "includes_external_calls": False,
            "limitations": ["No runtime data, live probes, external calls, or private local data are used."],
        },
        "aggregate_buckets": [
            _bucket("dry.bucket.source_gap.ia", "source_gap", "Internet Archive metadata source gap", "source_gap:internet_archive_metadata", 2),
            _bucket("dry.bucket.capability.member", "capability_gap", "Member enumeration capability gap", "capability:member_enumeration", 1),
            _bucket("dry.bucket.known_absence", "known_absence_status", "Scoped absence pattern", "known_absence:source_coverage_gap", 1),
        ],
        "demand_signals": [
            _signal("dry.signal.source_gap", "source_gap", "Synthetic source gap priority", "medium"),
            _signal("dry.signal.connector_needed", "connector_needed", "Synthetic connector approval priority", "medium"),
            _signal("dry.signal.candidate_review", "candidate_review_needed", "Synthetic candidate review priority", "low"),
        ],
        "source_gap_demand": [
            {
                "source_gap_id": "dry.source_gap.internet_archive_metadata",
                "source_family": "internet_archive",
                "source_id": "internet_archive_metadata",
                "gap_type": "connector_missing",
                "priority_class": "medium",
                "suggested_future_work": "connector_approval_pack",
                "approval_required": True,
                "operator_required": False,
                "human_required": True,
                "limitations": ["Dry-run future hint only; no connector is called."],
            }
        ],
        "capability_gap_demand": [
            {
                "capability_gap_id": "dry.capability.member_enumeration",
                "capability": "member_enumeration",
                "priority_class": "medium",
                "suggested_future_work": "Define future source-cache-backed member enumeration requirements.",
                "approval_required": True,
                "operator_required": False,
                "limitations": ["No extraction runtime is implemented."],
            }
        ],
        "manual_observation_demand": [
            {
                "manual_observation_need_id": "dry.manual_observation.batch0",
                "batch_ref": "manual_observation_batch_0",
                "query_family": "old-platform software search",
                "source_family": "manual_external_baseline",
                "reason": "external_baseline_pending",
                "human_required": True,
                "real_observation_count_claimed": False,
                "limitations": ["No manual observation count is claimed."],
            }
        ],
        "connector_priorities": [
            {
                "connector_priority_id": "dry.connector.internet_archive_metadata",
                "source_family": "internet_archive",
                "connector_kind": "internet_archive_metadata",
                "priority_class": "medium",
                "basis": "synthetic_example",
                "approval_required": True,
                "operator_required": False,
                "prerequisites": ["connector_approval_pack_future"],
                "limitations": ["No live connector runtime is implemented."],
            }
        ],
        "deep_extraction_priorities": [
            {
                "extraction_priority_id": "dry.extract.container_member_enumeration",
                "extraction_kind": "container_member_enumeration",
                "target_kind": "archived package member list",
                "priority_class": "medium",
                "prerequisites": ["source_cache_evidence_ledger_contract_future"],
                "safety_requirements": ["no downloads", "no execution", "approved source cache only"],
                "limitations": ["No extraction runtime is implemented."],
            }
        ],
        "candidate_review_priorities": [
            {
                "candidate_review_priority_id": "dry.candidate_review.compatibility",
                "candidate_type": "compatibility_claim_candidate",
                "review_kind": "evidence_review",
                "priority_class": "low",
                "basis": "synthetic_example",
                "promotion_policy_ref": "contracts/query/candidate_promotion_assessment.v0.json",
                "limitations": ["No candidate promotion or candidate mutation is performed."],
            }
        ],
        "known_absence_patterns": [
            {
                "absence_pattern_id": "dry.absence.source_coverage_gap",
                "absence_status": "source_coverage_gap",
                "pattern_label": "Synthetic source coverage gap",
                "checked_scope_summary": "Dry-run synthetic scope.",
                "not_checked_scope_summary": "No live source, source cache, or evidence ledger is checked.",
                "priority_class": "medium",
                "suggested_future_work": "source_sync_worker_contract",
                "limitations": ["No global absence claim is made."],
            }
        ],
        "priority_summary": {
            "top_source_gaps": ["internet_archive_metadata"],
            "top_capability_gaps": ["member_enumeration"],
            "top_manual_observation_needs": ["manual_observation_batch_0"],
            "top_connector_priorities": ["internet_archive_metadata"],
            "top_deep_extraction_priorities": ["container_member_enumeration"],
            "top_candidate_review_priorities": ["compatibility_claim_candidate"],
            "top_known_absence_patterns": ["source_coverage_gap"],
            "priority_basis": "synthetic_example",
            "real_user_demand_claimed": False,
            "limitations": ["Dry-run priorities are synthetic and not real demand proof."],
        },
        "public_visibility": {
            "public_dashboard_allowed": False,
            "visibility_class": "synthetic_example_only",
            "raw_queries_visible": False,
            "private_data_visible": False,
            "demand_counts_claimed_as_real": False,
            "caveats_required": ["stdout-only", "synthetic example", "no telemetry", "no real demand counts"],
            "limitations": ["No hosted or runtime dashboard is created."],
        },
        "freshness_and_invalidation": {
            "snapshot_freshness_policy": "example_only",
            "invalidation_required_on": [
                "query_guard_policy_change",
                "public_index_rebuild",
                "source_cache_refresh",
                "candidate_promotion_policy_change",
                "privacy_policy_change",
                "poisoning_policy_change",
            ],
            "invalidated": False,
            "limitations": ["No persistent snapshot exists."],
        },
        "limitations": ["Stdout-only dry run; no files are written and no runtime data is read."],
        "no_runtime_guarantees": {
            "runtime_dashboard_implemented": False,
            "persistent_dashboard_store_implemented": False,
            "telemetry_exported": False,
            "account_tracking_performed": False,
            "ip_tracking_performed": False,
            "public_query_logging_enabled": False,
            "raw_query_retained": False,
            "real_user_demand_claimed": False,
        },
        "no_mutation_guarantees": {
            "query_observation_mutated": False,
            "result_cache_mutated": False,
            "miss_ledger_mutated": False,
            "search_need_mutated": False,
            "probe_queue_mutated": False,
            "candidate_index_mutated": False,
            "candidate_promotion_mutated": False,
            "known_absence_mutated": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "master_index_mutated": False,
            "external_calls_performed": False,
            "live_source_called": False,
        },
        "notes": ["Demand Dashboard v0 dry-run output is synthetic and non-persistent."],
    }


def _bucket(bucket_id: str, bucket_type: str, label: str, normalized_key: str, count_value: int) -> dict[str, Any]:
    return {
        "bucket_id": bucket_id,
        "bucket_type": bucket_type,
        "label": label,
        "normalized_key": normalized_key,
        "count_policy": "synthetic_example_count",
        "count_value": count_value,
        "count_claimed_as_real_user_demand": False,
        "privacy_safe": True,
        "poisoning_filtered": True,
        "limitations": ["Synthetic example bucket only."],
    }


def _signal(signal_id: str, signal_type: str, label: str, priority_class: str) -> dict[str, Any]:
    return {
        "signal_id": signal_id,
        "signal_type": signal_type,
        "label": label,
        "priority_class": priority_class,
        "priority_basis": "synthetic dry-run basis",
        "supporting_refs": ["dry_run.synthetic_ref"],
        "synthetic_or_real": "synthetic_example",
        "real_user_demand_claimed": False,
        "limitations": ["Synthetic signal only."],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit a synthetic Demand Dashboard Snapshot v0 to stdout only.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. Kept explicit so command matrices document stdout-only behavior.")
    args = parser.parse_args(argv)
    if not args.json:
        print("Use --json to emit the synthetic dry-run demand dashboard snapshot.", file=sys.stderr)
        return 2
    json.dump(build_snapshot(), sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
