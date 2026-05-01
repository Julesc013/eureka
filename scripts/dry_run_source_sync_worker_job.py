#!/usr/bin/env python3
"""Emit a hypothetical Source Sync Worker Job v0 to stdout only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from typing import Any, Sequence


ALLOWED_KINDS = {
    "manual_source_review",
    "source_metadata_sync",
    "source_identifier_lookup",
    "source_availability_check",
    "source_cache_refresh",
    "source_record_normalization",
    "connector_health_check",
    "rate_limit_policy_check",
    "deep_extraction_request",
    "package_metadata_sync",
    "repository_release_sync",
    "wayback_availability_sync",
    "internet_archive_metadata_sync",
    "software_heritage_metadata_sync",
    "wikidata_identity_sync",
    "unknown",
}
ALLOWED_SOURCE_FAMILIES = {
    "internet_archive",
    "wayback",
    "github_releases",
    "pypi",
    "npm",
    "software_heritage",
    "wikidata_open_library",
    "sourceforge",
    "manual_source_pack",
    "local_fixture",
    "recorded_fixture",
    "unknown",
}
LIVE_FAMILIES = {
    "internet_archive",
    "wayback",
    "github_releases",
    "pypi",
    "npm",
    "software_heritage",
    "wikidata_open_library",
    "sourceforge",
}
PRIVATE_PATH = re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+|(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)
SECRET = re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key)\b|\b(?:secret|credential)\s*[:=]", re.IGNORECASE)
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)


def build_job(label: str, kind: str, source_family: str) -> dict[str, Any]:
    if kind not in ALLOWED_KINDS:
        kind = "unknown"
    if source_family not in ALLOWED_SOURCE_FAMILIES:
        source_family = "unknown"
    unsafe = bool(PRIVATE_PATH.search(label) or SECRET.search(label) or EMAIL.search(label))
    live_network = source_family in LIVE_FAMILIES and source_family not in {"recorded_fixture", "local_fixture"}
    source_policy_kind = "live_metadata_sync_after_approval" if live_network else "manual_only"
    execution_class = "approval_gated_live_sync_future" if live_network else "human_operated_future"
    status = "blocked_by_policy" if unsafe else "dry_run_validated"
    basis_label = "<redacted-source-sync-label>" if unsafe else label
    basis = f"{kind}:{source_family}:{basis_label}:dry_run:v0"
    fingerprint = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    return {
        "schema_version": "0.1.0",
        "source_sync_job_id": f"dry_run.source_sync.{fingerprint[:16]}",
        "source_sync_job_kind": "source_sync_worker_job",
        "status": status,
        "created_by_tool": "dry_run_source_sync_worker_job_v0",
        "job_identity": {
            "job_fingerprint": {
                "algorithm": "sha256",
                "normalized_basis": basis,
                "value": fingerprint,
                "reversible": False,
                "salt_policy": "unsalted_public_aggregate",
            },
            "canonical_job_label": basis_label,
            "normalized_job_terms": [kind, source_family],
            "duplicate_of": None,
            "supersedes": None,
        },
        "job_kind": {
            "kind": kind,
            "execution_class": execution_class,
            "live_network_required_future": live_network,
            "approval_required": True,
            "operator_required": live_network,
            "human_required": True,
        },
        "source_target": {
            "source_id": source_family,
            "source_family": source_family,
            "source_status": "approval_required" if live_network else "future",
            "target_identifier": "dry-run-synthetic-target",
            "target_query": None,
            "target_scope": "single_identifier" if live_network else "manual_review",
            "arbitrary_url_allowed": False,
            "limitations": ["Stdout-only synthetic target; no arbitrary URL or source call is performed."],
        },
        "source_policy": {
            "source_policy_kind": source_policy_kind,
            "live_source_enabled_now": False,
            "source_terms_review_required": True,
            "robots_or_source_policy_review_required": True,
            "user_agent_required_future": live_network,
            "rate_limit_required_future": True,
            "retry_backoff_required_future": True,
            "circuit_breaker_required_future": True,
            "cache_required_before_public_use": True,
            "evidence_attribution_required": True,
            "max_records_future": 100,
            "max_runtime_ms_future": 30000,
            "allowed_source_ids": [source_family],
            "allowed_source_families": [source_family],
            "prohibited_source_families": ["unknown"],
            "limitations": ["Dry-run policy projection only; no live source is enabled now."],
        },
        "approval_gates": _gates(live_network),
        "scheduling": {
            "schedule_status": "not_scheduled_v0",
            "earliest_run_policy": "after_source_policy_review_future" if live_network else "after_human_approval_future",
            "recurrence_policy": "none_v0",
            "notes": ["No schedule is created."],
        },
        "retry_timeout_rate_limit": {
            "retry_policy": "future_bounded_retry" if live_network else "none_v0",
            "max_retries_future": 2 if live_network else None,
            "timeout_policy": "future_bounded_timeout" if live_network else "none_v0",
            "max_runtime_ms_future": 30000 if live_network else None,
            "rate_limit_policy": "source_policy_required_future" if live_network else "none_v0",
            "per_source_qps_future": 0.2 if live_network else None,
            "circuit_breaker_policy": "future_required" if live_network else "none_v0",
            "limitations": ["Future policy hints only."],
        },
        "user_agent_and_terms": {
            "user_agent_required_future": live_network,
            "user_agent_value_current": None,
            "descriptive_user_agent_required_future": live_network,
            "contact_url_or_email_required_future": live_network,
            "source_terms_review_required": True,
            "robots_or_source_policy_review_required": True,
            "retry_after_respect_required_future": live_network,
            "notes": ["No fake contact email, credentials, or current User-Agent value is configured."],
        },
        "input_refs": {
            "query_observation_refs": [],
            "search_result_cache_refs": [],
            "search_miss_ledger_refs": [],
            "search_need_refs": [],
            "probe_queue_refs": [],
            "demand_dashboard_refs": [{"ref_id": "dry_run.demand_dashboard.source_gap", "ref_kind": "demand_dashboard_snapshot", "status": "synthetic_ref", "privacy_classification": "public_safe_example", "limitations": []}],
            "source_inventory_refs": [{"ref_id": f"dry_run.source_inventory.{source_family}", "ref_kind": "source_inventory", "status": "synthetic_ref", "privacy_classification": "public_safe_example", "limitations": []}],
            "source_pack_refs": [],
            "evidence_pack_refs": [],
        },
        "expected_outputs": {
            "expected_output_kinds": ["source_cache_record_future", "evidence_ledger_record_future"] if live_network else ["manual_report_future"],
            "output_destination_policy": "source_cache_future" if live_network else "manual_report_future",
            "requires_validation": True,
            "requires_review": True,
            "public_output_allowed_after_review": False,
            "limitations": ["No output is written by the dry-run helper."],
        },
        "safety_requirements": {
            "no_public_query_fanout": True,
            "no_arbitrary_url_fetch": True,
            "no_downloads": True,
            "no_installs": True,
            "no_execution": True,
            "no_uploads": True,
            "no_private_paths": True,
            "no_credentials_in_examples": True,
            "no_raw_payload_dump": True,
            "source_cache_required_before_public_use": True,
            "evidence_attribution_required": True,
            "bounded_result_count_required_future": True,
            "timeout_required_future": True,
            "rate_limit_required_future": True,
            "circuit_breaker_required_future": True,
            "rights_review_required": True,
            "risk_review_required": True,
            "notes": ["Dry-run safety policy only."],
        },
        "privacy": {
            "privacy_classification": "redacted" if unsafe else "public_safe_example",
            "contains_raw_query": False,
            "contains_private_path": False,
            "contains_secret": False,
            "contains_private_url": False,
            "contains_user_identifier": False,
            "contains_ip_address": False,
            "contains_local_result": False,
            "publishable": True,
            "public_aggregate_allowed": not unsafe,
            "reasons": ["Unsafe label was redacted."] if unsafe else ["Synthetic public-safe dry-run input."],
        },
        "rights_and_risk": {
            "rights_classification": "source_terms_apply" if live_network else "review_required",
            "risk_classification": "metadata_only",
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "downloads_enabled": False,
            "installs_enabled": False,
            "execution_enabled": False,
            "limitations": ["No rights clearance or malware safety claim is made."],
        },
        "limitations": ["Dry-run helper emits JSON to stdout only and writes no files."],
        "no_execution_guarantees": {
            "worker_runtime_implemented": False,
            "job_executed": False,
            "live_source_called": False,
            "external_calls_performed": False,
            "telemetry_exported": False,
            "credentials_used": False,
        },
        "no_mutation_guarantees": {
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "candidate_index_mutated": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "master_index_mutated": False,
            "probe_queue_mutated": False,
            "search_need_mutated": False,
            "result_cache_mutated": False,
        },
        "notes": ["No source sync job is persisted, queued, or executed."],
    }


def _gates(live_network: bool) -> list[dict[str, Any]]:
    gate_types = [
        "source_policy_review",
        "rights_review",
        "risk_review",
        "operator_approval",
        "human_approval",
        "rate_limit_review",
        "user_agent_review",
        "circuit_breaker_review",
        "cache_policy_review",
        "evidence_output_review",
        "connector_contract_review",
        "credential_policy_review",
    ]
    live_required = {"source_policy_review", "rate_limit_review", "user_agent_review", "circuit_breaker_review", "cache_policy_review"}
    return [
        {
            "gate_id": f"dry_run.gate.{gate_type}",
            "gate_type": gate_type,
            "required": bool(live_network and gate_type in live_required),
            "status": "review_required" if live_network and gate_type in live_required else "not_applicable",
            "reason": "Required before future live source sync." if live_network and gate_type in live_required else "Not required for this dry-run projection.",
            "limitations": ["No gate approval is granted."],
        }
        for gate_type in gate_types
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit a hypothetical Source Sync Worker Job v0 to stdout only.")
    parser.add_argument("--label", required=True, help="Public-safe synthetic label.")
    parser.add_argument("--kind", required=True, help="Source sync job kind.")
    parser.add_argument("--source-family", required=True, help="Source family.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args(argv)
    if not args.json:
        print("Use --json to emit the dry-run source sync worker job.", file=sys.stderr)
        return 2
    json.dump(build_job(args.label, args.kind, args.source_family), sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
