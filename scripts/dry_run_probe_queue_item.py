#!/usr/bin/env python3
"""Emit a non-persistent dry-run Probe Queue Item v0.

This helper prints one hypothetical probe queue item to stdout only. It
performs no network calls, telemetry, logging, persistence, queue writes, probe
execution, source cache writes, evidence ledger writes, candidate-index
mutation, local-index mutation, or master-index mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_probe_queue_item import ALLOWED_PROBE_KINDS, SENSITIVE_PATTERNS  # noqa: E402


TOKEN_RE = re.compile(r"[a-z0-9_.-]+", re.IGNORECASE)


def build_dry_run_probe_item(label: str, kind: str) -> dict[str, Any]:
    raw_label = label or ""
    stripped = " ".join(raw_label.strip().split())
    normalized_label = stripped.casefold()
    findings = _privacy_findings(raw_label)
    unsafe = bool(findings)
    normalized_kind = kind if kind in ALLOWED_PROBE_KINDS else "unknown"
    safe_terms = [] if unsafe else TOKEN_RE.findall(normalized_label)
    basis = "<redacted>" if unsafe else f"{normalized_label}|{normalized_kind}|probe_queue"
    probe_hash = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    status = "rejected_by_privacy_filter" if unsafe else "dry_run_validated"
    live_future = normalized_kind in {
        "source_metadata_probe",
        "source_identifier_probe",
        "wayback_availability_probe",
        "package_metadata_probe",
        "repository_release_probe",
    }
    execution_class = "approval_gated_live_probe_future" if live_future else "human_operated_future"
    source_policy_kind = "live_metadata_probe_after_approval" if live_future else "manual_only"
    output_policy = "source_cache_future" if live_future else "manual_report_future"
    expected_kind = "source_cache_record" if live_future else "manual_observation"

    return {
        "schema_version": "0.1.0",
        "probe_item_id": f"dry_run.probe_queue.{probe_hash[:16]}.v0",
        "probe_item_kind": "probe_queue_item",
        "status": status,
        "created_by_tool": "dry_run_probe_queue_item.py",
        "probe_identity": {
            "probe_fingerprint": {
                "algorithm": "sha256",
                "normalized_basis": "redacted_canonical_probe_label" if unsafe else "canonical_probe_label|probe_kind|probe_queue",
                "value": probe_hash,
                "reversible": False,
                "salt_policy": "unsalted_public_aggregate",
            },
            "canonical_probe_label": "<redacted>" if unsafe else stripped,
            "normalized_probe_terms": safe_terms,
        },
        "probe_kind": {
            "kind": normalized_kind,
            "execution_class": execution_class,
            "live_network_required_future": live_future,
            "approval_required": live_future,
            "operator_required": live_future,
            "human_required": True,
        },
        "source_policy": {
            "source_policy_kind": source_policy_kind,
            "allowed_source_ids": [],
            "allowed_source_families": ["future_approved_source_family"] if live_future else ["manual_external_baseline_future"],
            "prohibited_source_families": ["unapproved_live_network_sources", "private_local_stores"],
            "live_probe_enabled": False,
            "source_rate_limit_policy_ref": "future.source_rate_limit_policy.required" if live_future else "",
            "source_terms_review_required": True,
            "rights_review_required": True,
            "notes": ["Dry-run stdout only; no source call or queue write is performed."],
        },
        "input_refs": {
            "query_observation_refs": [],
            "search_result_cache_refs": [],
            "search_miss_ledger_refs": [],
            "search_need_refs": [
                {
                    "ref_id": "dry_run.search_need.unwritten",
                    "ref_kind": "search_need",
                    "status": "dry_run_validated" if not unsafe else "rejected_by_privacy_filter",
                    "privacy_classification": "public_safe_aggregate" if not unsafe else "rejected_sensitive",
                    "contribution_weight": 1.0,
                    "limitations": ["Dry-run ref only; no search need runtime emitted this input."],
                }
            ],
            "manual_observation_refs": [],
            "source_pack_refs": [],
            "evidence_pack_refs": [],
        },
        "target": {
            "target_kind": "source_family" if live_future else "compatibility_evidence",
            "product_name": "<redacted>" if unsafe else stripped,
            "artifact_type": "metadata summary" if live_future else "manual observation",
            "source_family": "future_approved_source_family" if live_future else "manual_external_baseline_future",
            "desired_evidence_kind": expected_kind,
            "limitations": ["Dry-run target only; no evidence or candidate record is created."],
        },
        "priority": {
            "priority_class": "example_only",
            "priority_basis": "single_need_example",
            "demand_count_claimed": False,
            "notes": ["Dry-run helper does not claim public demand."],
        },
        "scheduling": {
            "schedule_status": "future_after_approval" if live_future else "future_manual",
            "earliest_run_policy": "after_source_policy_review_future" if live_future else "not_applicable_v0",
            "retry_policy": "future_bounded_retry" if live_future else "none_v0",
            "timeout_policy": "future_bounded_timeout" if live_future else "none_v0",
            "notes": ["Dry-run helper creates no schedule."],
        },
        "expected_outputs": {
            "expected_output_kinds": [expected_kind],
            "output_destination_policy": output_policy,
            "public_output_allowed_after_review": False,
            "requires_validation": True,
            "requires_review": True,
            "notes": ["Future output would require validation and review before reuse."],
        },
        "safety_requirements": {
            "max_runtime_ms_future": 5000 if live_future else 1000,
            "rate_limit_required_future": live_future,
            "retry_backoff_required_future": live_future,
            "circuit_breaker_required_future": live_future,
            "user_agent_required_future": live_future,
            "source_terms_review_required": True,
            "robots_or_source_policy_review_required": live_future,
            "cache_required_before_public_use": live_future,
            "no_downloads": True,
            "no_installs": True,
            "no_execution": True,
            "no_uploads": True,
            "no_private_paths": True,
            "no_credentials": True,
            "no_arbitrary_url_fetch": True,
        },
        "privacy": _privacy(findings, unsafe),
        "retention_policy": {
            "raw_query_retention": "none",
            "probe_item_retention": "example_only",
            "deletion_supported_future": True,
            "notes": ["P63 dry-run helper writes nothing and implements no retention runtime."],
        },
        "aggregation_policy": {
            "aggregate_allowed": not unsafe,
            "aggregate_fields_allowed": ["probe_kind", "target_kind", "priority_class"],
            "raw_query_aggregation_allowed": False,
            "private_identifier_aggregation_allowed": False,
            "notes": ["Aggregate policy is future-only and excludes raw queries and private identifiers."],
        },
        "limitations": [
            "Dry-run stdout only; no probe queue file is written.",
            "No telemetry, queue mutation, source cache write, evidence ledger write, candidate-index mutation, local-index mutation, or master-index mutation.",
        ],
        "no_execution_guarantees": {
            "probe_executed": False,
            "live_source_called": False,
            "external_calls_performed": False,
        },
        "no_mutation_guarantees": {
            "source_cache_mutated": False,
            "evidence_ledger_mutated": False,
            "candidate_index_mutated": False,
            "master_index_mutated": False,
            "local_index_mutated": False,
            "result_cache_mutated": False,
            "miss_ledger_mutated": False,
            "search_need_mutated": False,
            "telemetry_exported": False,
        },
        "notes": ["Dry-run probe queue items are examples for validation and future integration planning only."],
    }


def _privacy(findings: set[str], unsafe: bool) -> dict[str, Any]:
    return {
        "privacy_classification": "rejected_sensitive" if unsafe else "public_safe_aggregate",
        "contains_raw_query": False,
        "contains_private_path": any(item in findings for item in {"windows_absolute_path", "posix_private_path"}),
        "contains_secret": "api_key_marker" in findings,
        "contains_private_url": "private_url" in findings,
        "contains_user_identifier": "account_identifier" in findings,
        "contains_ip_address": "ip_address" in findings,
        "contains_local_result": False,
        "publishable": False,
        "public_aggregate_allowed": not unsafe,
        "reasons": sorted(findings) if unsafe else ["raw query retention is disabled by default"],
    }


def _privacy_findings(text: str) -> set[str]:
    findings: set[str] = set()
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            findings.add(label)
    return findings


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="Public-safe probe label to normalize.")
    parser.add_argument("--kind", default="unknown", help="Probe kind.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only. Plain mode still prints JSON because this is a dry-run artifact.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    item = build_dry_run_probe_item(args.label, args.kind)
    output = stdout or sys.stdout
    output.write(json.dumps(item, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
