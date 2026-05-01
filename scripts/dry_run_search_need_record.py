#!/usr/bin/env python3
"""Emit a non-persistent dry-run Search Need Record v0.

This helper prints one hypothetical search need record to stdout only. It
performs no network calls, telemetry, logging, persistence, need-store
mutation, probe enqueueing, candidate-index mutation, result cache mutation,
miss ledger mutation, local-index mutation, or master-index mutation.
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

from scripts.validate_search_need_record import SENSITIVE_PATTERNS  # noqa: E402


TOKEN_RE = re.compile(r"[a-z0-9_.-]+", re.IGNORECASE)
INDEX_SNAPSHOT_REF = "eureka_public_search_index_v0"
ALLOWED_OBJECT_KINDS = {
    "software",
    "software_version",
    "driver",
    "manual_or_documentation",
    "source_code_release",
    "package_metadata",
    "web_capture",
    "article_or_scan_segment",
    "file_inside_container",
    "compatibility_evidence",
    "source_identity",
    "unknown",
}


def build_dry_run_search_need(label: str, object_kind: str) -> dict[str, Any]:
    raw_label = label or ""
    stripped = " ".join(raw_label.strip().split())
    normalized_label = stripped.casefold()
    findings = _privacy_findings(raw_label)
    unsafe = bool(findings)
    normalized_kind = object_kind if object_kind in ALLOWED_OBJECT_KINDS else "unknown"
    safe_terms = [] if unsafe else TOKEN_RE.findall(normalized_label)
    basis = "<redacted>" if unsafe else f"{normalized_label}|{normalized_kind}|search_need"
    need_hash = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    status = "rejected_by_privacy_filter" if unsafe else "dry_run_validated"

    return {
        "schema_version": "0.1.0",
        "search_need_id": f"dry_run.search_need.{need_hash[:16]}.v0",
        "search_need_kind": "search_need_record",
        "status": status,
        "created_by_tool": "dry_run_search_need_record.py",
        "need_identity": {
            "need_fingerprint": {
                "algorithm": "sha256",
                "normalized_basis": "redacted_canonical_need_label" if unsafe else "canonical_need_label|object_kind|search_need",
                "value": need_hash,
                "reversible": False,
                "salt_policy": "unsalted_public_aggregate",
            },
            "canonical_need_label": "<redacted>" if unsafe else stripped,
            "normalized_need_terms": safe_terms,
            "disambiguation_terms": [] if unsafe else safe_terms[:4],
            "equivalence_keys": [] if unsafe else [f"{normalized_kind}:{'-'.join(safe_terms[:6])}"],
            "alias_terms": [],
        },
        "target_object": {
            "object_kind": normalized_kind,
            "product_name": "<redacted>" if unsafe else stripped,
            "artifact_type": "unknown",
            "desired_action": "inspect",
        },
        "originating_inputs": {
            "query_observation_refs": [],
            "search_miss_ledger_refs": [
                {
                    "ref_id": "dry_run.search_miss_ledger.unwritten",
                    "ref_kind": "search_miss_ledger",
                    "status": "dry_run_validated" if not unsafe else "rejected_by_privacy_filter",
                    "privacy_classification": "public_safe_aggregate" if not unsafe else "rejected_sensitive",
                    "contribution_weight": 1.0,
                    "limitations": ["Dry-run ref only; no miss ledger runtime emitted this input."],
                }
            ],
            "search_result_cache_refs": [],
            "manual_observation_refs": [],
            "source_pack_refs": [],
            "evidence_pack_refs": [],
        },
        "aggregate_summary": {
            "occurrence_count": 1 if not unsafe else 0,
            "distinct_query_fingerprint_count": 1 if not unsafe else 0,
            "distinct_normalized_need_count": 1 if not unsafe else 0,
            "first_seen_policy": "not_tracked_in_v0_example",
            "last_seen_policy": "not_tracked_in_v0_example",
            "representative_intents": [] if unsafe else ["unknown"],
            "representative_platforms": [],
            "representative_artifact_types": ["unknown"],
            "confidence": "low",
            "demand_classification": "single_example" if not unsafe else "unknown",
        },
        "source_and_capability_gaps": [
            {
                "gap_type": "query_interpretation_gap" if not unsafe else "unknown",
                "capability": "future_search_need_review",
                "explanation": "Dry-run search need requires future review before any probe, candidate, or source action.",
                "blocking": True,
                "suggested_resolution_future": "run_manual_observation",
            }
        ],
        "checked_scope": {
            "checked_indexes": [] if unsafe else ["public_index", "local_index_only"],
            "checked_sources": [] if unsafe else ["data/public_index"],
            "checked_source_families": [] if unsafe else ["public_index_fixture_and_recorded_sources"],
            "checked_capabilities": [] if unsafe else ["search_need_contract_projection"],
            "checked_index_snapshot_refs": [] if unsafe else [INDEX_SNAPSHOT_REF],
            "live_probes_attempted": False,
            "external_calls_performed": False,
        },
        "not_checked_scope": {
            "sources_not_checked": ["future source cache", "private local stores", "approved live probes"],
            "source_families_not_checked": ["live_source_families_future"],
            "capabilities_not_checked": ["probe_queue", "candidate_index", "master_index_promotion"],
            "reasons_not_checked": ["disabled_by_policy", "not_implemented"],
            "limitations": ["Dry-run need is scoped and does not claim anything outside checked contract behavior."],
        },
        "evidence_and_result_context": {
            "best_known_result_refs": [],
            "near_miss_refs": [],
            "weak_hit_refs": [],
            "absence_refs": [],
            "relevant_source_refs": [],
            "relevant_evidence_refs": [],
            "confidence": "low",
            "limitations": ["Dry-run stdout only; no result or evidence payload is stored."],
        },
        "suggested_next_steps": [
            {
                "step_type": "run_manual_observation",
                "reason": "Future review would be required before any action.",
                "future_only": True,
                "approval_required": False,
                "human_required": True,
                "operator_required": False,
            }
        ],
        "priority": {
            "priority_class": "example_only",
            "priority_basis": "single_miss_example",
            "demand_count_claimed": False,
            "notes": ["Dry-run helper does not claim public demand counts."],
        },
        "privacy": _privacy(findings, unsafe),
        "retention_policy": {
            "raw_query_retention": "none",
            "need_record_retention": "example_only",
            "deletion_supported_future": True,
            "notes": ["P62 dry-run helper writes nothing and implements no retention runtime."],
        },
        "aggregation_policy": {
            "aggregate_allowed": not unsafe,
            "aggregate_fields_allowed": ["need_fingerprint", "object_kind", "gap_type", "priority_class"],
            "raw_query_aggregation_allowed": False,
            "private_identifier_aggregation_allowed": False,
            "notes": ["Aggregate policy is future-only and excludes raw queries and private identifiers."],
        },
        "limitations": [
            "Dry-run stdout only; no search need file is written.",
            "No telemetry, need-store mutation, probe enqueue, candidate-index mutation, result cache mutation, miss ledger mutation, local-index mutation, or master-index mutation.",
        ],
        "no_mutation_guarantees": {
            "master_index_mutated": False,
            "local_index_mutated": False,
            "candidate_index_mutated": False,
            "probe_enqueued": False,
            "result_cache_mutated": False,
            "miss_ledger_mutated": False,
            "query_observation_mutated": False,
            "telemetry_exported": False,
            "external_calls_performed": False,
            "public_need_runtime_created": False,
        },
        "notes": ["Dry-run search need records are examples for validation and future integration planning only."],
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
    parser.add_argument("--label", required=True, help="Public-safe search need label to normalize.")
    parser.add_argument("--object-kind", default="unknown", help="Target object kind.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only. Plain mode still prints JSON because this is a dry-run artifact.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    record = build_dry_run_search_need(args.label, args.object_kind)
    output = stdout or sys.stdout
    output.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
